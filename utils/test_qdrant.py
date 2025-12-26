
import sys
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Configuration
QDRANT_PATH = r"d:/Viswam_Projects/chandamama-studio/qdrant_db"
COLLECTION_NAME = "chandamama_chunks"
MODEL_NAME = "intfloat/multilingual-e5-base"

def main():
    try:
        client = QdrantClient(path=QDRANT_PATH)
        if not client.collection_exists(COLLECTION_NAME):
            print("Collection not found.")
            return
            
        info = client.get_collection(COLLECTION_NAME)
        print(f"Collection Points: {info.points_count}")
        
        if info.points_count == 0:
            return

        model = SentenceTransformer(MODEL_NAME)
        query = "Moral stories about greed"
        print(f"Querying: {query}")
        
        query_text = f"query: {query}"
        embedding = model.encode(query_text, normalize_embeddings=True)
        
        results = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=embedding,
            limit=3,
            with_payload=True
        )
        
        for i, hit in enumerate(results):
            print(f"[{i+1}] {hit.payload.get('title')} (Score: {hit.score:.4f})")

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
