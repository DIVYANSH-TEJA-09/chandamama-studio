import os

# Refactored to use src.config
try:
    from src import config
except ImportError:
    import sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
    from src import config

# Base paths
# Getting the project root by going up two levels from this file (src/story_embedder/config.py -> src -> PROJECT_ROOT)
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))

# Data paths
CHUNKS_DIR = os.path.join(PROJECT_ROOT, "data", "chunks")
QDRANT_PATH = config.QDRANT_PATH
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")

# Ensure logs directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Files
SKIPPED_STORIES_LOG = os.path.join(LOG_DIR, "skipped_stories.csv")

# Qdrant Settings
COLLECTION_NAME = config.STORY_COLLECTION_NAME 
VECTOR_SIZE = 768

# Model Settings
MODEL_NAME = config.STORY_EMBEDDING_MODEL_NAME
MAX_TOKEN_LIMIT = config.STORY_MAX_TOKEN_LIMIT 

# Processing Settings
BATCH_SIZE = config.STORY_BATCH_SIZE
