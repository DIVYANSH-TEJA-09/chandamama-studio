from typing import List, Dict, Any
from .common_utils import get_qdrant_client, get_embedding, generate_uuid, COLLECTION_NAME
from qdrant_client.models import Filter, FieldCondition, MatchValue

class ContextualRetriever:
    def __init__(self, top_k: int = 3):
        self.client = get_qdrant_client()
        self.top_k = top_k

    def retrieve(self, query: str) -> str:
        """
        Retrieves chunks with their neighbors (previous and next).
        Logic: 
        - Find Top K relevant chunks.
        - For each chunk, try to fetch [Prev, Target, Next].
        - Fallbacks:
            - No Prev -> [Target, Next, Next+1]
            - No Next -> [Prev-1, Prev, Target]
            - Isolated -> [Target]
        """
        query_vector = get_embedding(query)
        
        # Filter out poems
        poem_filter = Filter(must_not=[FieldCondition(key="content_type", match=MatchValue(value="POEM"))])

        # 1. Standard Semantic Search
        # Using query_points() to match app.py (requires qdrant-client>=1.7.0)
        search_results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            query_filter=poem_filter,
            limit=self.top_k,
            with_payload=True
        ).points

        final_context_parts = []

        for hit in search_results:
            payload = hit.payload
            story_id = payload.get("story_id")
            chunk_index = payload.get("chunk_index") # Integer
            title = payload.get("title")

            if not story_id or chunk_index is None:
                continue

            # Identify IDs for potential neighbors (Prev-1, Prev, Target, Next, Next+1)
            # We calculate more than needed to handle fallbacks
            indices_to_check = {
                "p2": chunk_index - 2,
                "p1": chunk_index - 1,
                "t": chunk_index,
                "n1": chunk_index + 1,
                "n2": chunk_index + 2
            }
            
            ids_map = {}
            for key, idx in indices_to_check.items():
                if idx > 0: # Indices are 1-based (usually, based on generate_chunks.py)
                    # Reconstruct ID: "storyid_01", "storyid_02"
                     # Note: populate_qdrant uses uuid5(chunk_id). 
                     # chunk_id format in generate_chunks.py is: f"{story_id}_{index:02d}"
                    raw_chunk_id = f"{story_id}_{idx:02d}"
                    ids_map[key] = generate_uuid(raw_chunk_id)

            # Bulk retrieve all potentially needed points
            # qdrant retrieve by ID
            points_to_fetch = list(ids_map.values())
            try:
                fetched_points = self.client.retrieve(
                    collection_name=COLLECTION_NAME,
                    ids=points_to_fetch,
                    with_payload=True
                )
            except Exception as e:
                print(f"Error fetching neighbors: {e}")
                fetched_points = []

            # Map UUID back to payload for easy access
            points_dict = {point.id: point.payload for point in fetched_points}

            # Helper to get text if exists
            def get_text(k):
                uid = ids_map.get(k)
                if uid and uid in points_dict:
                    return points_dict[uid].get("text", "")
                return None

            # Logic for selection
            # Standard: p1, t, n1
            
            chain = []
            
            has_p1 = get_text("p1") is not None
            has_n1 = get_text("n1") is not None
            
            if has_p1 and has_n1:
                # Ideal: [Prev, Target, Next]
                chain = ["p1", "t", "n1"]
            elif not has_p1 and has_n1:
                # No Prev (Start of story?) -> [Target, Next, Next+1]
                chain = ["t", "n1", "n2"]
            elif has_p1 and not has_n1:
                # No Next (End of story?) -> [Prev-1, Prev, Target]
                chain = ["p2", "p1", "t"]
            else:
                # Isolated -> [Target]
                chain = ["t"]

            # Construct text for this hit group
            group_text = []
            group_text.append(f"### Segment from: {title} (ID: {story_id}, Center Chunk: {chunk_index})")
            
            valid_chunks_found = False
            for key in chain:
                txt = get_text(key)
                if txt:
                    group_text.append(txt)
                    valid_chunks_found = True
            
            if valid_chunks_found:
                final_context_parts.append("\n".join(group_text))

        return "\n\n".join(final_context_parts)
