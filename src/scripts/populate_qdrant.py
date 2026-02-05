
import os
import sys
import json
import uuid
import math
import multiprocessing
from typing import List, Dict, Any
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Add the project root to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
sys.path.insert(0, project_root)

from src import config

# Configuration
CHUNKS_DIR = os.path.join(project_root, "data", "chunks")
COLLECTION_NAME = config.COLLECTION_NAME
MODEL_NAME = config.EMBEDDING_MODEL_NAME
VECTOR_SIZE = 768
BATCH_SIZE = 64

def get_chunk_files(base_dir: str) -> List[str]:
    chunk_files = []
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith("_chunks.json"):
                chunk_files.append(os.path.join(root, file))
    return sorted(chunk_files)

def load_chunks(file_path: str) -> List[Dict[str, Any]]:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return []

# Worker Function
def process_chunks_worker(file_path):
    stats = {
        'processed': 0,
        'indexed': 0,
        'file': file_path,
        'error': None
    }
    
    try:
        # Lazy import SentenceTransformer to be process-safe
        from sentence_transformers import SentenceTransformer
        
        chunks = load_chunks(file_path)
        if not chunks:
            return stats
            
        stats['processed'] = len(chunks)
        
        # Initialize Client Per Worker
        if config.QDRANT_URL and config.QDRANT_API_KEY:
            client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
        else:
            client = QdrantClient(path=config.QDRANT_PATH)
            
        # Initialize Model Per Worker (or rely on efficiency if small)
        # Re-initializing model per file is expensive if files are small.
        # But for multiprocessing safety, it's the standard way without shared memory.
        model = SentenceTransformer(MODEL_NAME)
        
        # Process in batches
        total_indexed = 0
        
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            
            texts_to_embed = [f"passage: {c['text']}" for c in batch]
            embeddings = model.encode(texts_to_embed, normalize_embeddings=True)
            
            points = []
            for j, chunk in enumerate(batch):
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk['chunk_id']))
                payload = chunk.copy()
                points.append(models.PointStruct(id=point_id, vector=embeddings[j].tolist(), payload=payload))
            
            try:
                client.upsert(collection_name=COLLECTION_NAME, points=points)
                total_indexed += len(points)
            except Exception as e:
                pass # Fail silently for partial batch or log?
                
        stats['indexed'] = total_indexed
        
    except Exception as e:
        stats['error'] = str(e)
        
    return stats

def main():
    print(f"Initializing Parallel Chunk Injection...")
    print(f"Target Database: {config.QDRANT_PATH}")
    
    # Initialize Collection (Main Thread)
    if config.QDRANT_URL and config.QDRANT_API_KEY:
        client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    else:
        client = QdrantClient(path=config.QDRANT_PATH)

    if not client.collection_exists(collection_name=COLLECTION_NAME):
        print(f"Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(size=VECTOR_SIZE, distance=models.Distance.COSINE)
        )
    
    # Get Files
    chunk_files = get_chunk_files(CHUNKS_DIR)
    print(f"Found {len(chunk_files)} chunk files.")
    
    # Workers
    total_cores = multiprocessing.cpu_count()
    workers = max(1, math.floor(total_cores * 0.75))
    print(f"Using Workers: {workers} (75% of {total_cores} Cores)")
    
    total_chunks = 0
    
    # Parallel Execution
    with multiprocessing.Pool(processes=workers) as pool:
        results = list(tqdm(
            pool.imap_unordered(process_chunks_worker, chunk_files),
            total=len(chunk_files),
            desc="Parallel Indexing"
        ))
        
        for res in results:
            total_chunks += res['indexed']
            if res['error']:
                print(f"Error in {res['file']}: {res['error']}")

    print(f"Ingestion complete. Total chunks indexed: {total_chunks}")

if __name__ == "__main__":
    multiprocessing.freeze_support()
    main()
