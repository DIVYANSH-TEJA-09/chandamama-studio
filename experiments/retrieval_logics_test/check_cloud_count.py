import os
import sys

# Add project root to sys.path
sys.path.append(os.getcwd())

from dotenv import load_dotenv
load_dotenv(os.path.join(os.getcwd(), ".env"))

from qdrant_client import QdrantClient
from src import config

# Ensure we use CLOUD credentials
load_dotenv()

def main():
    print(f"Checking Qdrant Cloud at: {config.QDRANT_URL}")
    
    try:
        client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
        
        # Check Story Collection
        col_name = "chandamama_stories"
        print(f"\nChecking collection: {col_name}")
        
        if not client.collection_exists(col_name):
            print("❌ Collection DOES NOT exist.")
            return

        count = client.count(collection_name=col_name).count
        print(f"Total Stories in DB: {count}")
        
        # Check a sample for metadata
        if count > 0:
            res = client.scroll(collection_name=col_name, limit=1, with_payload=True, with_vectors=False)
            if res[0]:
                payload = res[0][0].payload
                print(f"Sample Payload Keys: {list(payload.keys())}")
                if 'text' in payload:
                    print(f"✅ Text content present (Length: {len(payload['text'])})")
                
    except Exception as e:
        print(f"Error reading Cloud DB: {e}")

if __name__ == "__main__":
    main()
