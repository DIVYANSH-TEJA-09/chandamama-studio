from typing import List, Dict, Any
from .common_utils import get_qdrant_client, get_embedding, COLLECTION_NAME
from qdrant_client.models import Filter, FieldCondition, MatchValue

class FullStoryRetriever:
    def __init__(self, top_k: int = 3):
        self.client = get_qdrant_client()
        self.top_k = top_k

    def retrieve(self, query: str) -> str:
        """
        Retrieves the FULL text of the top identified stories.
        Logic:
        - Find Top K relevant chunks.
        - Extract unique Story IDs.
        - For each Story ID, fetch ALL chunks belonging to it.
        - Sort by index and concatenate.
        """
        query_vector = get_embedding(query)
        
        # 1. Standard Semantic Search to find RELEVANT STORIES
        # Using query_points() to match app.py (requires qdrant-client>=1.7.0)
        search_results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=self.top_k,
            with_payload=True
        ).points

        unique_story_ids = []
        seen = set()
        
        # Preserve order of relevance
        for hit in search_results:
            s_id = hit.payload.get("story_id")
            if s_id and s_id not in seen:
                unique_story_ids.append(s_id)
                seen.add(s_id)

        final_context_parts = []
        current_total_chars = 0
        MAX_CHARS = 6000  # API Limit Safety

        for story_id in unique_story_ids:
            # Scroll/Filter to get all chunks for this story
            # We use scroll to ensure we get everything (though stories are usually small enough for high limit)
            
            # Filter condition
            scroll_filter = Filter(
                must=[
                    FieldCondition(
                        key="story_id",
                        match=MatchValue(value=story_id)
                    )
                ]
            )

            all_points = []
            next_offset = None
            
            # Fetch all chunks
            while True:
                records, next_offset = self.client.scroll(
                    collection_name=COLLECTION_NAME,
                    scroll_filter=scroll_filter,
                    limit=100, # Should cover most stories in one go
                    offset=next_offset,
                    with_payload=True
                )
                all_points.extend(records)
                if next_offset is None:
                    break
            
            if not all_points:
                continue

            # Sort by chunk_index
            # Ensure chunk_index is int
            all_points.sort(key=lambda x: int(x.payload.get("chunk_index", 0)))
            
            # Metadata from first chunk (usually consistent)
            first_payload = all_points[0].payload
            title = first_payload.get("title", "Unknown")
            year = first_payload.get("year", "Unknown")
            month = first_payload.get("month", "Unknown")

            story_text_blocks = []
            header = f"### Full Story: {title} (ID: {story_id}, Date: {year}-{month})"
            story_text_blocks.append(header)
            
            story_content = ""
            for point in all_points:
                text = point.payload.get("text", "").strip()
                if text:
                    story_content += text + "\n"
            
            story_text_blocks.append(story_content)
            full_story_text = "\n".join(story_text_blocks)
            
            # Check length
            if current_total_chars + len(full_story_text) > MAX_CHARS:
                # Calculate remaining space
                remaining = MAX_CHARS - current_total_chars
                if remaining > 500: # Only add if we can add a meaningful amount
                    truncated_text = full_story_text[:remaining] + "... [TRUNCATED DUE TO LENGTH]"
                    final_context_parts.append(truncated_text)
                break # Stop adding stories
            
            final_context_parts.append(full_story_text)
            current_total_chars += len(full_story_text)

        return "\n\n".join(final_context_parts)
