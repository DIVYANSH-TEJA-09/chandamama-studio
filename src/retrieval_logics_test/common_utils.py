import os
import sys
import uuid
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# Common Utils
try:
    from src import config
except ImportError:
    import config

_client_instance = None
_model_instance = None

def get_qdrant_client():
    global _client_instance
    if _client_instance is None:
        if config.QDRANT_MODE == "cloud":
            print(f"Connecting to Qdrant Cloud at {config.QDRANT_PATH}...", flush=True)
            _client_instance = QdrantClient(
                url=config.QDRANT_PATH, 
                api_key=config.QDRANT_API_KEY
            )
        else:
            # Local Mode
            if not os.path.exists(config.QDRANT_PATH):
                 raise FileNotFoundError(f"Qdrant DB not found at {config.QDRANT_PATH}. Please run rebuild_db.py first.")
            print(f"Connecting to Local Qdrant at {config.QDRANT_PATH}...", flush=True)
            _client_instance = QdrantClient(path=config.QDRANT_PATH)
    return _client_instance

def get_embedding_model():
    global _model_instance
    if _model_instance is None:
        print(f"Loading embedding model '{config.EMBEDDING_MODEL_NAME}'...", flush=True)
        _model_instance = SentenceTransformer(config.EMBEDDING_MODEL_NAME)
    return _model_instance

def get_embedding(text: str):
    model = get_embedding_model()
    # e5 requires "query: " prefix for retrieval queries
    return model.encode(f"query: {text}", normalize_embeddings=True)

def generate_uuid(chunk_id: str) -> str:
    """Replicates the UUID generation logic from populate_qdrant.py"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, chunk_id))
