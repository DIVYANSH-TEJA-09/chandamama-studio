
import sys
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Configuration
QDRANT_PATH = r"d:/Viswam_Projects/chandamama-studio/qdrant_db"
COLLECTION_NAME = "chandamama_chunks"
MODEL_NAME = "intfloat/multilingual-e5-base"

def main():
    print("Loading model...")
    model = SentenceTransformer(MODEL_NAME)
    
    print(f"Connecting to Qdrant at {QDRANT_PATH}...")
    client = QdrantClient(path=QDRANT_PATH)
    
    # Check collection info
    try:
        info = client.get_collection(COLLECTION_NAME)
        print(f"Collection '{COLLECTION_NAME}' ready. Points: {info.points_count}")
    except Exception as e:
        print(f"Error accessing collection: {e}")
        return

    print("\n--- Chandamama Semantic Search ---")
    print("Type 'exit' or 'quit' to stop.")
    
    while True:
        query = input("\nEnter query (English/Telugu): ").strip()
        if query.lower() in ['exit', 'quit']:
            break
        if not query:
            continue
            
        # Embed query
        # Multilingual-e5 requires "query: " prefix for questions
        query_text = f"query: {query}"
        embedding = model.encode(query_text, normalize_embeddings=True)
        
        # Search
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            limit=3,
            with_payload=True
        )
        
        print(f"\nTop 3 Results for: '{query}'")
        for i, hit in enumerate(results):
            payload = hit.payload
            score = hit.score
            
            print(f"\n[{i+1}] Score: {score:.4f}")
            print(f"    Title: {payload.get('title')} ({payload.get('year')}-{payload.get('month'):02d})")
            print(f"    Genre: {payload.get('normalized_genre_code')}")
            print(f"    Text: {payload.get('text')[:200]}...") # Preview
            print(f"    Path: {payload.get('source_path')}")

if __name__ == "__main__":
    main()
