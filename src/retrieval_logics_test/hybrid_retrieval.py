from typing import List, Dict, Any
import random
from .common_utils import get_qdrant_client, get_embedding, COLLECTION_NAME
from .contextual_retrieval import ContextualRetriever
from qdrant_client.models import Filter, FieldCondition, MatchValue

class HybridRetriever:
    def __init__(self, content_top_k: int = 3):
        self.client = get_qdrant_client()
        self.content_retriever = ContextualRetriever(top_k=content_top_k)

    GENRE_MAPPING = {
        "Folklore": "FOLK_TALE",
        "Fantasy": "FANTASY_STORY",
        "Moral": "MORAL_STORY",
        "Animal Fable": "ANIMAL_STORY",
        "Mythology": "MYTHOLOGY_STORY",
        "Humor": "HUMOR_STORY",
        "History": "HISTORICAL_STORY",
        "Adventure": "ADVENTURE_STORY"
    }

    def retrieve_style_context(self, genre: str) -> str:
        """
        Channel A: Retrieves a full story from the same genre to serve as a Style Template.
        Uses random scrolling/filtering.
        """
        # 1. Filter by Genre
        # Note: Genre in metadata is 'normalized_genre_code' or similar. 
        # But 'genre' input is "Folklore", "Mythology" etc.
        # We need to map or just search. Simple filter might be empty if mapping doesn't match.
        # Let's try to search for the genre keyword first to find a relevant story ID.
        
        # Alternative: Just pick a random story from the DB (simplest approximation of 'Style').
        # Better: Search for genre keyword, pick a random hit, get that story.
        
        try:
            # Search for genre to find a representative story
            genre_vector = get_embedding(genre)
            
            # Map UI Genre to Normalized Genre Code
            target_genre_code = self.GENRE_MAPPING.get(genre)
            
            must_conditions = []
            if target_genre_code:
                must_conditions.append(FieldCondition(key="normalized_genre_code", match=MatchValue(value=target_genre_code)))
            
            # Filter out poems
            must_not_conditions = [FieldCondition(key="content_type", match=MatchValue(value="POEM"))]
            
            # Combine filters
            style_filter = Filter(must=must_conditions, must_not=must_not_conditions)

            candidates = self.client.query_points(
                collection_name=COLLECTION_NAME,
                query=genre_vector,
                query_filter=style_filter,
                limit=20, # Pool of candidates
                with_payload=True
            ).points
            
            if not candidates:
                return "Style Context: No suitable story found."

            # Pick one random candidate
            selected_hit = random.choice(candidates)
            story_id = selected_hit.payload.get("story_id")
            
            # Fetch FULL story for this ID
            scroll_filter = Filter(must=[FieldCondition(key="story_id", match=MatchValue(value=story_id))])
            
            all_points = []
            next_offset = None
            while True:
                records, next_offset = self.client.scroll(
                    collection_name=COLLECTION_NAME,
                    scroll_filter=scroll_filter,
                    limit=100,
                    offset=next_offset,
                    with_payload=True
                )
                all_points.extend(records)
                if next_offset is None:
                    break
            
            # Sort and assemble
            all_points.sort(key=lambda x: int(x.payload.get("chunk_index", 0)))
            story_lines = [p.payload.get("text", "") for p in all_points]
            full_text = "\n".join(story_lines)
            
            title = all_points[0].payload.get("title", "Unknown")
            return f"### STYLE REFERENCE: {title} (Genre: {genre})\n{full_text}"

        except Exception as e:
            return f"Error retrieving style: {e}"

    def retrieve_content_context(self, query: str) -> str:
        """
        Channel B: Retrieves semantic content using Contextual Chunks.
        """
        return self.content_retriever.retrieve(query)

    def retrieve_hybrid(self, query: str, genre: str) -> Dict[str, str]:
        """
        Returns both contexts.
        """
        return {
            "style": self.retrieve_style_context(genre),
            "content": self.retrieve_content_context(query)
        }
