from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Any, Dict
import numpy as np # Implicit dependency of sentence-transformers but good to have for typing if needed
from . import config
from .story_processor import Story
from . import skipped_log

class StoryEmbedder:
    def __init__(self):
        print(f"Loading embedding model '{config.MODEL_NAME}'...")
        self.model = SentenceTransformer(config.MODEL_NAME)
        # We can use the model's tokenizer to count tokens accurately
        self.tokenizer = self.model.tokenizer

    def generate_embeddings(self, stories: List[Story]) -> List[Tuple[str, List[float], Dict[str, Any]]]:
        """
        Generate embeddings for a list of stories.
        Skips stories that exceed the token limit.
        
        Returns:
            List of tuples: (story_id, embedding_vector, metadata)
        """
        valid_stories = []
        valid_texts = []
        
        # 1. Filter stories by length
        filtered_results = []
        
        for story in stories:
            # Prefix for e5 models passed as "passage: "
            # Instructions: "Embed ONLY the full story text."
            # But e5 expects "passage: " for documents. 
            # In `populate_qdrant.py` (which I must mimic logic-wise where appropriate), 
            # line 78 says: texts_to_embed = [f"passage: {c['text']}" for c in batch]
            # So I will use the prefix.
            text_to_embed = f"passage: {story.text}"
            
            # Count tokens
            # tokenizer.encode returns input_ids. len(input_ids) is token count.
            # Using truncation=False to get actual length check.
            token_ids = self.tokenizer.encode(text_to_embed, add_special_tokens=True, truncation=False)
            token_count = len(token_ids)
            
            if token_count > config.MAX_TOKEN_LIMIT:
                print(f"Skipping story {story.story_id}: {token_count} tokens (Limit: {config.MAX_TOKEN_LIMIT})")
                skipped_log.log_skipped_story(story.story_id, "Exceeds token limit", token_count)
                continue
                
            valid_stories.append(story)
            valid_texts.append(text_to_embed)
            
        if not valid_stories:
            return []

        # 2. Generate embeddings for valid stories
        print(f"Embedding {len(valid_stories)} stories...")
        embeddings = self.model.encode(valid_texts, normalize_embeddings=True, batch_size=config.BATCH_SIZE)
        
        # 3. Pack results
        results = []
        for i, story in enumerate(valid_stories):
            results.append((
                story.story_id,
                embeddings[i].tolist(),
                story.metadata
            ))
            
        return results
