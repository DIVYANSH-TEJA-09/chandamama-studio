import os

# Paths
STATS_PATH = "data/stats/global_stats.json"
POEM_STATS_PATH = "data/stats/poem_stats.json"

# Qdrant Configuration - Support both Cloud and Local
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")

# Use Qdrant Cloud if credentials provided, otherwise use local
if QDRANT_URL and QDRANT_API_KEY:
    QDRANT_PATH = QDRANT_URL  # Cloud URL
    QDRANT_MODE = "cloud"
else:
    QDRANT_PATH = os.path.join(os.getcwd(), "qdrant_db")  # Local path
    QDRANT_MODE = "local"

# Qdrant / Embeddings
COLLECTION_NAME = "chandamama_chunks"
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"

# Operations
SEARCH_LIMIT = 5

# LLM Configuration
LLM_MODEL_ID = "openai/gpt-oss-120b"
LLM_MAX_TOKENS = 3000
LLM_TEMPERATURE = 0.7

# Model Configuration
AVAILABLE_MODELS = [
    "openai/gpt-oss-120b"
]

# Map models to specific Environment Variable names for their API keys
MODEL_API_KEY_MAP = {
    "openai/gpt-oss-120b": "GROQ_API_KEY"
}

# Story Embeddings (Alibaba GTE)
STORY_COLLECTION_NAME = "chandamama_stories"
STORY_EMBEDDING_MODEL_NAME = "Alibaba-NLP/gte-multilingual-base"
STORY_MAX_TOKEN_LIMIT = 8192
STORY_BATCH_SIZE = 1

# Chunking Configuration
CHUNK_TARGET_MIN = 300
CHUNK_TARGET_MAX = 500
CHUNK_HARD_MIN = 150
CHUNK_HARD_MAX = 700
