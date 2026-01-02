import os

# Base paths
# Getting the project root by going up two levels from this file (src/story_embedder/config.py -> src -> PROJECT_ROOT)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Data paths
CHUNKS_DIR = os.path.join(PROJECT_ROOT, "chunks")
QDRANT_PATH = os.path.join(PROJECT_ROOT, "qdrant_db")
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Files
SKIPPED_STORIES_LOG = os.path.join(LOG_DIR, "skipped_stories.csv")

# Qdrant Settings
# Using a separate collection for story-level embeddings as requested
COLLECTION_NAME = "chandamama_stories" 
VECTOR_SIZE = 768

# Model Settings
# Using the same model as populate_qdrant.py to match ecosystem, though new models exist.
# User requested "Use a single multilingual embedding model consistently."
MODEL_NAME = "intfloat/multilingual-e5-base"
# e5-base has a limit of 512 tokens. Stories longer than this will be skipped.
MAX_TOKEN_LIMIT = 512 

# Processing Settings
BATCH_SIZE = 32  # Batch size for embedding generation
