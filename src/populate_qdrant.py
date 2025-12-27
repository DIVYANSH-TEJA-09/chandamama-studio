
import os
import json
import uuid
from typing import List, Dict, Any
from tqdm import tqdm
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer

# Configuration
# Configuration
CHUNKS_DIR = os.getenv("CHUNKS_DIR", "chunks")
QDRANT_PATH = os.getenv("QDRANT_PATH", "qdrant_db")
COLLECTION_NAME = "chandamama_chunks"
MODEL_NAME = "intfloat/multilingual-e5-base"
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
    print(f"Initializing Qdrant at {QDRANT_PATH}...")
    client = QdrantClient(path=QDRANT_PATH)

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
            
            # Prepare inputs for embedding (e5 requires "query: " or "passage: " prefix, 
            # but usually for retrieval. For indexing, "passage: " is common or raw. 
            # The user just said "embed text". 
            # Multilingual-e5 docs say: "passage: " for docs, "query: " for queries.
            # I will use "passage: " prefix as best practice for e5.)
            texts_to_embed = [f"passage: {c['text']}" for c in batch]
            
            embeddings = model.encode(texts_to_embed, normalize_embeddings=True)
            
            points = []
            for j, chunk in enumerate(batch):
                # Use a deterministic UUID or just a random one? 
                # User said "One chunk = one Qdrant point". 
                # Chunks have "chunk_id" like "1947_07_01_01". We can use that as ID if Qdrant supports string IDs (it does, UUIDs or ints).
                # Using UUID based on chunk_id for consistency.
                point_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk['chunk_id']))
                
                # Payload is the chunk itself (excluding text? No, user said "Metadata is stored ONLY as payload". 
                # Usually text is also in payload for retrieval display. User said "Only `chunk["text"]` is embedded".
                # User constraint: "Metadata is stored ONLY as payload (never embedded)". 
                # It doesn't explicitly forbid storing text in payload. 
                # Usually we want text in payload to show results. I will include it.)
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

if __name__ == "__main__":
    main()
