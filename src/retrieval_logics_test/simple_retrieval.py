from typing import List, Dict, Any
from .common_utils import get_qdrant_client, get_embedding, COLLECTION_NAME

class SimpleRetriever:
    def __init__(self, top_k: int = 7):
        self.client = get_qdrant_client()
        self.top_k = top_k

    def retrieve(self, query: str) -> str:
        """
        Retrieves the top K chunks based on semantic similarity.
        This mimics the 'Simple' / Baseline logic.
        """
        query_vector = get_embedding(query)
        
        # 1. Standard Semantic Search
        search_results = self.client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=self.top_k,
            with_payload=True
        ).points

        context_parts = []
        for i, hit in enumerate(search_results):
            payload = hit.payload
            text = payload.get("text", "").strip()
            title = payload.get("title", "Unknown")
            chunk_id = payload.get("chunk_id", "Unknown")
            
            if text:
                 context_parts.append(f"### [Chunk {i+1}] {title} (ID: {chunk_id}):\n{text}")
        
        return "\n\n".join(context_parts)
