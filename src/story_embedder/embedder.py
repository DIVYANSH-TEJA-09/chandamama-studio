from sentence_transformers import SentenceTransformer
from typing import List, Tuple, Any, Dict
import numpy as np # Implicit dependency of sentence-transformers but good to have for typing if needed
from . import config
from .story_processor import Story
from . import skipped_log

class StoryEmbedder:
    def __init__(self):
        print(f"Loading embedding model '{config.MODEL_NAME}'...")
        # trust_remote_code=True is required for GTE models
        self.model = SentenceTransformer(config.MODEL_NAME, trust_remote_code=True)
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
            # [METADATA INFUSION]
            # Construct a rich context string including Title, Author, and Keywords.
            # This ensures the vector captures the "Meta-Context" not just the raw narrative.
            
            meta_header = []
            if story.metadata.get('title'):
                meta_header.append(f"Title: {story.metadata['title']}")
            if story.metadata.get('author'):
                meta_header.append(f"Author: {story.metadata['author']}")
            if story.metadata.get('keywords'):
                # Key words might be a list or a comma-separated string
                kws = story.metadata['keywords']
                if isinstance(kws, list):
                    kws = ", ".join(kws)
                meta_header.append(f"Keywords: {kws}")
                
            header_text = "\n".join(meta_header)
            full_content = f"{header_text}\n\n{story.text}"
            
            # Use 'passage: ' prefix if model requires it (GTE/E5 usually do for retrieval docs)
            text_to_embed = f"{full_content}" # Alibaba GTE might not strictly need 'passage:', but 'text_to_embed' var name kept.
            
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
