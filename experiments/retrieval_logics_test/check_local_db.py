import os
import sys
# Add project root to sys.path
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
exp_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(exp_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from dotenv import load_dotenv
from qdrant_client import QdrantClient
from src import config

# Force LOCAL mode for this check
config.QDRANT_MODE = "local" 
config.QDRANT_PATH = os.path.join(os.getcwd(), "qdrant_db")

def main():
    print(f"Checking LOCAL Qdrant at: {config.QDRANT_PATH}")
    
    try:
        client = QdrantClient(path=config.QDRANT_PATH)
        
        # Check Story Collection
        print(f"\nChecking collection: {config.STORY_COLLECTION_NAME}")
        if not client.collection_exists(config.STORY_COLLECTION_NAME):
            print("❌ Collection DOES NOT exist locally.")
            return

        count = client.count(collection_name=config.STORY_COLLECTION_NAME).count
        print(f"Total Stories: {count}")
        
        if count > 0:
            res = client.scroll(collection_name=config.STORY_COLLECTION_NAME, limit=1, with_payload=True, with_vectors=False)
            if res[0]:
                payload = res[0][0].payload
                print(f"Payload Keys: {list(payload.keys())}")
                
                if 'text' in payload:
                    length = len(payload['text'])
                    print(f"✅ 'text' field is PRESENT (Length of sample: {length} chars)")
                else:
                    print("❌ 'text' field is MISSING from payload!")
    except Exception as e:
        print(f"Error reading local DB: {e}")

if __name__ == "__main__":
    main()
