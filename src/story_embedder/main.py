import argparse
import time
from tqdm import tqdm
from . import config
from . import data_loader
from . import story_processor
from .embedder import StoryEmbedder
from .storage import QdrantStorage
from . import skipped_log

def main(dry_run=False):
    start_time = time.time()
    print("=== Story-Level Embedding Pipeline ===")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    
    # Initialize components
    storage = QdrantStorage() if not dry_run else None
    embedder = StoryEmbedder() if not dry_run else None
    
    # 1. Scan files
    files = data_loader.scan_chunk_files()
    print(f"Found {len(files)} chunk files to process.")
    
    total_processed = 0
    total_skipped_existing = 0
    total_embedded = 0
    total_failed = 0
    
    # Initialize skipped log
    skipped_log.init_log()
    
    samples_printed = 0
    
    for file_path in tqdm(files, desc="Processing Files"):
        try:
            # 2. Load chunks
            chunks = data_loader.load_raw_chunks(file_path)
            if not chunks:
                continue
                
            # 3. Process into stories
            stories = story_processor.process_file_to_stories(file_path, chunks)
            if not stories:
                continue
                
            total_processed += len(stories)
            
            # 4. Filter existing (Idempotency)
            if not dry_run:
                story_ids = [s.story_id for s in stories]
                existing_ids = storage.check_existing(story_ids)
                
                stories_to_embed = [s for s in stories if s.story_id not in existing_ids]
                
                skipped_count = len(stories) - len(stories_to_embed)
                total_skipped_existing += skipped_count
                
                if not stories_to_embed:
                    continue
            else:
                stories_to_embed = stories
                # For dry run just show the first few
                if samples_printed < 5:
                    for s in stories:
                        if samples_printed >= 5:
                            break
                        print(f"\n[Dry Run] Sample extracted story: {s.story_id}")
                        print(f"Metadata keys: {list(s.metadata.keys())}")
                        print(f"Text length: {len(s.text)} chars")
                        samples_printed += 1
            
            # 5. Embed and Store
            if not dry_run and stories_to_embed:
                # Embedder handles token limit checks internally
                embeddings_data = embedder.generate_embeddings(stories_to_embed)
                
                if embeddings_data:
                    count = storage.upsert_stories(embeddings_data)
                    total_embedded += count
                    
        except Exception as e:
            print(f"Error processing file {file_path}: {e}")
            total_failed += 1
            
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n=== Pipeline Complete ===")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Total Stories Scanned: {total_processed}")
    if not dry_run:
        print(f"Skipped (Already Exists): {total_skipped_existing}")
        print(f"Successfully Embedded: {total_embedded}")
        print(f"Failed Files: {total_failed}")
        print(f"Check {config.SKIPPED_STORIES_LOG} for skipped items (token limit).")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run story embedding pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Scan files but do not embed or store")
    args = parser.parse_args()
    
    main(dry_run=args.dry_run)
