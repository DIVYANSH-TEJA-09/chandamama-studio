
import os
import sys
from dotenv import load_dotenv
from qdrant_client import QdrantClient

# Load env vars
load_dotenv()

# Add project root to sys.path
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
exp_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(exp_dir)
if project_root not in sys.path:
    sys.path.append(project_root)

from src import config

def main():
    print(f"Checking Qdrant Collection: {config.STORY_COLLECTION_NAME}")
    print(f"Mode: {config.QDRANT_MODE}")
    print(f"URL: {config.QDRANT_PATH}")
    
    if config.QDRANT_MODE == 'cloud':
        client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    else:
        client = QdrantClient(path=config.QDRANT_PATH)
        
    try:
        count = client.count(collection_name=config.STORY_COLLECTION_NAME).count
        print(f"Total Stories: {count}")
        
        if count > 0:
            # check payload of one
            res = client.scroll(collection_name=config.STORY_COLLECTION_NAME, limit=1, with_payload=True, with_vectors=False)
            if res[0]:
                print(f"Full Keys: {list(res[0][0].payload.keys())}")
                # check for any large string field
                for k, v in res[0][0].payload.items():
                    if isinstance(v, str) and len(v) > 100:
                        print(f"Potential Text Field found: '{k}' (len: {len(v)})")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
