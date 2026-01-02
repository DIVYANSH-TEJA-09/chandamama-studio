import os
import sys
import uuid
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Add src to path to import config if needed, though we are redefining some here for isolation
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configuration matching the main app
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
QDRANT_PATH = os.path.join(PROJECT_ROOT, "qdrant_db")
COLLECTION_NAME = "chandamama_chunks"
MODEL_NAME = "intfloat/multilingual-e5-base"

_client_instance = None
_model_instance = None

def get_qdrant_client():
    global _client_instance
    if _client_instance is None:
        if not os.path.exists(QDRANT_PATH):
             raise FileNotFoundError(f"Qdrant DB not found at {QDRANT_PATH}. Please run rebuild_db.py first.")
        _client_instance = QdrantClient(path=QDRANT_PATH)
    return _client_instance

def get_embedding_model():
    global _model_instance
    if _model_instance is None:
        print(f"Loading embedding model '{MODEL_NAME}'...", flush=True)
        _model_instance = SentenceTransformer(MODEL_NAME)
    return _model_instance

def get_embedding(text: str):
    model = get_embedding_model()
    # e5 requires "query: " prefix for retrieval queries
    return model.encode(f"query: {text}", normalize_embeddings=True)

def generate_uuid(chunk_id: str) -> str:
    """Replicates the UUID generation logic from populate_qdrant.py"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
