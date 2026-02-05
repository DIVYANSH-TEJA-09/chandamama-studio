import argparse
import time
import multiprocessing
import math
from tqdm import tqdm
from . import config
from . import data_loader
from . import story_processor
from .storage import QdrantStorage
# We import StoryEmbedder inside the worker to avoid eager loading
# from .embedder import StoryEmbedder 
from . import skipped_log

# Helper function MUST be at top level for multiprocessing pickling
def process_file_worker(file_path):
    """
    Worker function to process a single file.
    Instantiates its own Storage and Embedder (lazy) to be process-safe.
    """
    stats = {
        'processed': 0,
        'embedded': 0,
        'updated': 0,
        'failed': 0,
        'skipped_existing': 0,
        'file': file_path,
        'error': None
    }
    
    try:
        # Lazy import to avoid circular dependencies or eager init issues
        from .embedder import StoryEmbedder
        
        # 1. Load Chunks
        chunks = data_loader.load_raw_chunks(file_path)
        if not chunks:
            return stats
            
        # 2. Process Stories
        stories = story_processor.process_file_to_stories(file_path, chunks)
        if not stories:
            return stats
            
        stats['processed'] = len(stories)
        
        # 3. Check Existing (Storage)
        # Each worker needs its own connection
        storage = QdrantStorage()
        story_ids = [s.story_id for s in stories]
        existing_ids = storage.check_existing(story_ids)
        
        stories_to_embed = []
        stories_to_update = []
        
        for s in stories:
            if s.story_id in existing_ids:
                stories_to_update.append(s)
            else:
                stories_to_embed.append(s)
        
        # 4. Update Payloads (Repair)
        if stories_to_update:
            count = storage.update_payloads(stories_to_update)
            stats['updated'] = count
            
        # 5. Embed New (Ingest)
        # Only instantiate Embedder if we actually have work
        if stories_to_embed:
            # Singleton-ish within the worker process? 
            # Since we process 1 file per call, we instantiate. 
            # If batching multiple files per worker, we'd cache it.
            # But process_file_worker is called once per file.
            # Ideally we'd use a worker initializer. But typically file processing takes enough time.
            
            embedder = StoryEmbedder() 
            embeddings_data = embedder.generate_embeddings(stories_to_embed)
            
            if embeddings_data:
                count = storage.upsert_stories(embeddings_data)
                stats['embedded'] = count
                
    except Exception as e:
        stats['error'] = str(e)
        stats['failed'] = 1
        
    return stats

def main(dry_run=False):
    start_time = time.time()
    
    # Calculate Workers - 75% of CPU
    total_cores = multiprocessing.cpu_count()
    workers = max(1, math.floor(total_cores * 0.75))
    
    print("=== Parallel Story Embedding Pipeline ===")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"System Cores: {total_cores}")
    print(f"Using Workers: {workers} (75% Target)")
    
    # 1. Scan files
    files = data_loader.scan_chunk_files()
    print(f"Found {len(files)} chunk files to process.")
    
    # Initialize skipped log (Main process)
    skipped_log.init_log()
    
    total_processed = 0
    total_embedded = 0
    total_updated = 0
    total_failed = 0
    
    if dry_run:
        print("Dry Run: Running sequentially (no multiprocessing)...")
        # Just run a few
        for f in files[:3]:
            res = process_file_worker(f)
            print(f"Dry Run Result for {f}: {res}")
            total_processed += res['processed']
    else:
        # Multiprocessing Pool
        # We use imap_unordered to update tqdm as results come in
        with multiprocessing.Pool(processes=workers) as pool:
            results = list(tqdm(
                pool.imap_unordered(process_file_worker, files), 
                total=len(files), 
                desc="Parallel Processing"
            ))
            
            # Aggregate Results
            for res in results:
                total_processed += res['processed']
                total_embedded += res['embedded']
                total_updated += res['updated']
                if res['failed']:
                    total_failed += 1
                    print(f"Failed {res['file']}: {res['error']}")

    end_time = time.time()
    duration = end_time - start_time
    
    print("\n=== Pipeline Complete ===")
    print(f"Duration: {duration:.2f} seconds")
    print(f"Total Stories Scanned: {total_processed}")
    if not dry_run:
        print(f"Updated (Payload Only): {total_updated}")
        print(f"Successfully Embedded: {total_embedded}")
        print(f"Failed Files: {total_failed}")
        print(f"Check {config.SKIPPED_STORIES_LOG} for skipped items.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run story embedding pipeline")
    parser.add_argument("--dry-run", action="store_true", help="Scan files but do not embed or store")
    args = parser.parse_args()
    
    # Fix for multiprocessing on Windows
    multiprocessing.freeze_support()
    
    main(dry_run=args.dry_run)
