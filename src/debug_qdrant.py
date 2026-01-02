
import sys
import os
from qdrant_client import QdrantClient

# Configuration matching common_utils
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QDRANT_PATH = os.path.join(PROJECT_ROOT, "qdrant_db")

print(f"Project Root: {PROJECT_ROOT}")
print(f"Qdrant Path: {QDRANT_PATH}")
print(f"QdrantClient imported from: {sys.modules['qdrant_client']}")

try:
    client = QdrantClient(path=QDRANT_PATH)
    print("\nClient Attributes:")
    attrs = dir(client)
    
    if 'search' in attrs:
        print(" - search: FOUND")
    else:
        print(" - search: NOT FOUND")

    if 'query_points' in attrs:
        print(" - query_points: FOUND")
    else:
        print(" - query_points: NOT FOUND")

    if 'retrieve' in attrs:
        print(" - retrieve: FOUND")
    else:
        print(" - retrieve: NOT FOUND")
        
    print("\nAll public methods:")
    for a in attrs:
        if not a.startswith("_"):
            print(a)
            
except Exception as e:
    print(f"Error initializing client: {e}")
