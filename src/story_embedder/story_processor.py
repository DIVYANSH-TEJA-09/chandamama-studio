from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
import collections

@dataclass
class Story:
    story_id: str
    text: str
    metadata: Dict[str, Any]
    # Keep track of source for debugging
    source_file: str = ""

def process_file_to_stories(file_path: str, raw_chunks: List[Dict[str, Any]]) -> List[Story]:
    """
    Reconstruct full stories from a list of chunks.
    
    Args:
        file_path: The path of the source file (for logging/debugging).
        raw_chunks: List of chunk dictionaries.
        
    Returns:
        List of Story objects.
    """
    # Group chunks by story_id
    chunks_by_id = collections.defaultdict(list)
    
    for chunk in raw_chunks:
        s_id = chunk.get('story_id')
        if not s_id:
            continue
        chunks_by_id[s_id].append(chunk)
        
    stories = []
    
    for s_id, chunks in chunks_by_id.items():
        # Sort chunks by chunk_index to ensure correct order
        # Assuming chunk_index is 1-based index from the generation process
        sorted_chunks = sorted(chunks, key=lambda x: x.get('chunk_index', 0))
        
        # Reconstruct full text
        # Join with a newline to preserve paragraph structure if chunks were split at paragraphs.
        # However, if chunks were split mid-sentence, newline might be wrong.
        # The prompt says: "Reconstruct the FULL story text by ordering chunks correctly."
        # Usually chunking splits by paragraphs or sentences. Newline is safer than space to avoid merging words.
        # But if the split was arbitrary, space might be better. 
        # Looking at sample chunks.json (Step 20), chunks seem to be full paragraphs.
        # Example 1: ends with "...\n... తీపి నోట్లో పోసిపోవే."
        # Example 2: ends with "...రాలేను సీతా, సీతా !"
        # I will use newline separator as it likely reflects the original structure better.
        full_text = "\n".join([c.get('text', '') for c in sorted_chunks])
        
        if not full_text.strip():
            # Skip empty stories
            continue

        # Extract metadata from the first chunk
        # "Preserve ALL metadata fields exactly as provided."
        # We take the first chunk's data and remove chunk-specific fields.
        first_chunk = sorted_chunks[0]
        metadata = first_chunk.copy()
        
        # Remove fields that are specific to the chunk or redundant
        # We keep the original 'story_id' in metadata as well, as requested ("STORE ALL METADATA FIELDS AS-IS")
        # But we must NOT embed chunk IDs.
        keys_to_remove = ['chunk_id', 'chunk_index', 'text', 'embedding'] # embedding shouldn't be there but just in case
        for k in keys_to_remove:
            metadata.pop(k, None)
            
        # [FIX] Ensure FULL text is stored in metadata for RAG retrieval
        metadata['text'] = full_text
            
        # Add basic stats to metadata? The prompt says "Store metadata separately".
        # It doesn't ask to ADD new metadata, but preserving existing.
        # We will strictly preserve.
        
        stories.append(Story(
            story_id=s_id,
            text=full_text,
            metadata=metadata,
            source_file=file_path
        ))
        
    return stories
