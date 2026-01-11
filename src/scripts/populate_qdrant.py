
import os
import sys
import json
import uuid
from typing import List, Dict, Any
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# Add the project root to sys.path to allow importing src.config
# Current file: src/scripts/populate_qdrant.py
# Root structure: src/scripts/../.. -> project root
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

def main():
    print(f"Initializing Qdrant at {config.QDRANT_PATH}...")
    print(f"Mode: {getattr(config, 'QDRANT_MODE', 'unknown')}")
    
    # Initialize Client based on configuration
    if config.QDRANT_URL and config.QDRANT_API_KEY:
        client = QdrantClient(
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY
        )
    else:
        client = QdrantClient(path=config.QDRANT_PATH)

    # Create collection if not exists
    if not client.collection_exists(collection_name=COLLECTION_NAME):
        print(f"Creating collection '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=models.VectorParams(
                size=VECTOR_SIZE,
                distance=models.Distance.COSINE
            )
        )
    else:
        print(f"Collection '{COLLECTION_NAME}' already exists.")

    print(f"Loading embedding model '{MODEL_NAME}'...")
    model = SentenceTransformer(MODEL_NAME)

    chunk_files = get_chunk_files(CHUNKS_DIR)
    print(f"Found {len(chunk_files)} chunk files.")

    total_chunks = 0
    
    # Process files
    for file_path in tqdm(chunk_files, desc="Processing Files"):
        chunks = load_chunks(file_path)
        if not chunks:
            continue

        # Prepare batches
        for i in range(0, len(chunks), BATCH_SIZE):
            batch = chunks[i:i + BATCH_SIZE]
            
            # Prepare inputs for embedding
            # "passage: " prefix for e5 models
            texts_to_embed = [f"passage: {c['text']}" for c in batch]
            
            embeddings = model.encode(texts_to_embed, normalize_embeddings=True)
            
            points = []
            for j, chunk in enumerate(batch):
                # Deterministic UUID based on chunk_id
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk['chunk_id']))
                
                payload = chunk.copy() 
                
                points.append(models.PointStruct(
                    id=point_id,
                    vector=embeddings[j].tolist(),
                    payload=payload
                ))

            try:
                client.upsert(
                    collection_name=COLLECTION_NAME,
                    points=points
                )
                total_chunks += len(points)
            except Exception as e:
                print(f"Error upserting batch: {e}")

    print(f"Ingestion complete. Total chunks indexed: {total_chunks}")
    print(f"Target Database: {config.QDRANT_PATH}")

if __name__ == "__main__":
    main()
