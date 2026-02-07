import argparse
import time
from tqdm import tqdm
from . import config
from . import data_loader
from . import story_processor
from .storage import QdrantStorage
from .embedder import StoryEmbedder 
from . import skipped_log

def process_single_file(file_path, storage, embedder):
    """
    Sequential processor that uses persistent storage/embedder instances.
    """
    stats = {
        'processed': 0,
        'embedded': 0,
        'updated': 0,
        'failed': 0,
        'file': file_path,
        'error': None
    }
    
    try:
        # 1. Load Chunks
        chunks = data_loader.load_raw_chunks(file_path)
        if not chunks:
            return stats
            
        # 2. Process Stories
        stories = story_processor.process_file_to_stories(file_path, chunks)
        if not stories:
            return stats
            
        stats['processed'] = len(stories)
        
        # 3. Check Existing
        # Even if DB is cleared, this check is fast and safe.
        story_ids = [s.story_id for s in stories]
        existing_ids = storage.check_existing(story_ids)
        
        stories_to_embed = []
        stories_to_update = []
        
        for s in stories:
            if s.story_id in existing_ids:
                stories_to_update.append(s)
            else:
                stories_to_embed.append(s)
        
        # 4. Update Payloads (if any found)
        if stories_to_update:
            count = storage.update_payloads(stories_to_update)
            stats['updated'] = count
            
        # 5. Embed New (Ingest)
        if stories_to_embed:
            embeddings_data = embedder.generate_embeddings(stories_to_embed)
            if embeddings_data:
                count = storage.upsert_stories(embeddings_data)
                stats['embedded'] = count
                
    except Exception as e:
        stats['error'] = str(e)
        stats['failed'] = 1
        print(f"❌ Error processing {file_path}: {e}")
        
    return stats

def main(dry_run=False):
    start_time = time.time()
    
    print("=== Sequential Story Embedding Pipeline ===")
    print("Mode: SEQUENTIAL (Single Thread)")
    print("Loading Models & Connections ONCE...")
    
    # Initialize ONCE
    storage = QdrantStorage()
    embedder = None
    
    if not dry_run:
        embedder = StoryEmbedder()
    
    # 1. Scan files
    files = data_loader.scan_chunk_files()
    print(f"Found {len(files)} chunk files to process.")
    
    # Initialize skipped log
    skipped_log.init_log()
    
    total_processed = 0
    total_embedded = 0
    total_updated = 0
    total_failed = 0
    
    # Sequential Loop
    for file_path in tqdm(files, desc="Sequential Processing"):
        if dry_run:
            # Fake processing
            print(f"Would process: {file_path}")
            continue
            
        res = process_single_file(file_path, storage, embedder)
        
        total_processed += res['processed']
        total_embedded += res['embedded']
        total_updated += res['updated']
        if res['failed']:
            total_failed += 1

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n=== Pipeline Complete ===")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Total Stories Scanned: {total_processed}")
    print(f"Updated (Payload Only): {total_updated}")
    print(f"Successfully Embedded: {total_embedded}")
    print(f"Failed Files: {total_failed}")
    print(f"Check {config.SKIPPED_STORIES_LOG} for skipped items.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run story embedding pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Scan files but do not embed or store")
    args = parser.parse_args()
    
    main(dry_run=args.dry_run)
