
import os
import csv
import sys
import collections
from typing import List, Dict, Set
from tqdm import tqdm

# Allow running as a script from root
# If this script is run directly, ensure project root is in path
if __name__ == "__main__" and __package__ is None:
    # This hack allows running as `python src/story_embedder/retry_skipped.py`
    # But better to run as `python -m src.story_embedder.retry_skipped`
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(current_dir))
    sys.path.append(project_root)
    __package__ = "src.story_embedder"

from . import config
from . import story_processor
from .embedder import StoryEmbedder
from .storage import QdrantStorage
from . import data_loader

def get_skipped_ids() -> Set[str]:
    """Read the log file and return a set of skipped story IDs."""
    if not os.path.exists(config.SKIPPED_STORIES_LOG):
        print(f"No log file found at {config.SKIPPED_STORIES_LOG}")
        return set()

    skipped_ids = set()
    try:
        with open(config.SKIPPED_STORIES_LOG, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['story_id']:
                    skipped_ids.add(row['story_id'])
    except Exception as e:
        print(f"Error reading log file: {e}")
    
    return skipped_ids

def map_ids_to_files(skipped_ids: Set[str]) -> Dict[str, List[str]]:
    """
    Map story IDs to their expected chunk file paths.
    Format: YYYY_MM_XX -> chunks/YYYY/చందమామ_YYYY_MM_chunks.json
    """
    files_map = collections.defaultdict(list)
    
    for sid in skipped_ids:
        parts = sid.split('_')
        if len(parts) >= 2:
            year = parts[0]
            month = parts[1]
            try:
                # Construct path
                filename = f"చందమామ_{year}_{month}_chunks.json"
                file_path = os.path.join(config.CHUNKS_DIR, year, filename)
                files_map[file_path].append(sid)
            except Exception:
                print(f"Skipping malformed ID: {sid}")
                
    return files_map

def main():
    print("=== Retry Skipped Stories Pipeline ===")
    
    # 1. Identify skipped stories
    skipped_ids = get_skipped_ids()
    if not skipped_ids:
        print("No skipped stories found in log.")
        return
        
    print(f"Found {len(skipped_ids)} unique skipped stories in log.")
    
    # 2. Map to files
    file_map = map_ids_to_files(skipped_ids)
    print(f"Stories are distributed across {len(file_map)} files.")
    
    # 3. Initialize components
    # Assuming config is already updated to new model (checked in previous steps)
    storage = QdrantStorage()
    embedder = StoryEmbedder()
    
    total_embedded = 0
    total_failed = 0
    files_processed = 0
    
    # 4. Process files
    for file_path, target_ids in tqdm(file_map.items(), desc="Processing Files"):
        try:
            if not os.path.exists(file_path):
                print(f"Warning: File not found: {file_path}")
                continue
                
            # Load chunks
            chunks = data_loader.load_raw_chunks(file_path)
            if not chunks:
                continue
            
            # Convert to stories
            all_stories = story_processor.process_file_to_stories(file_path, chunks)
            
            # Filter for only the skipped ones
            target_set = set(target_ids)
            stories_to_retry = [s for s in all_stories if s.story_id in target_set]
            
            if not stories_to_retry:
                # This might happen if the ID in log doesn't match ID in file (unlikely)
                print(f"Warning: None of the target stories found in {os.path.basename(file_path)}")
                continue
                
            # Embed and Upsert
            # The embedder will check the new token limit (8192)
            embeddings_data = embedder.generate_embeddings(stories_to_retry)
            
            if embeddings_data:
                count = storage.upsert_stories(embeddings_data)
                total_embedded += count
                # Optional: Remove from log or mark as done? 
                # For now, just appending to log is default behavior of embedder on fail.
                # We don't remove from CSV, user can delete file later.
            
            files_processed += 1
            
        except Exception as e:
            print(f"Error processing {os.path.basename(file_path)}: {e}")
            total_failed += 1
            
    print("\n=== Retry Complete ===")
    print(f"Total Files Processed: {files_processed}/{len(file_map)}")
    print(f"Total Stories Successfully Re-Embedded: {total_embedded}")
    print("Note: If any stories were skipped again, they are appended to the log.")

if __name__ == "__main__":
    main()
