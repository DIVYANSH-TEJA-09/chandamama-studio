import os

# Paths
STATS_PATH = "data/stats/global_stats.json"
POEM_STATS_PATH = "data/stats/poem_stats.json"
QDRANT_PATH = os.path.join(os.getcwd(), "qdrant_db")

# Qdrant / Embeddings
COLLECTION_NAME = "chandamama_chunks"
EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-base"

# Operations
SEARCH_LIMIT = 5

# LLM Configuration
LLM_MODEL_ID = "openai/gpt-oss-120b"
LLM_MAX_TOKENS = 3000
LLM_TEMPERATURE = 0.7

# Council of Storytellers Configuration
COUNCIL_MODELS = [
    "Qwen/Qwen2.5-72B-Instruct",
    "meta-llama/Meta-Llama-3.1-70B-Instruct",
    "google/gemma-2-27b-it",
    "mistralai/Mistral-Nemo-Instruct-2407",
    "gpt-4o-mini"
]

# Map models to specific Environment Variable names for their API keys
MODEL_API_KEY_MAP = {
    "Qwen/Qwen2.5-72B-Instruct": "HF_TOKEN_QWEN",
    "meta-llama/Meta-Llama-3.1-70B-Instruct": "HF_TOKEN_LLAMA", 
    "google/gemma-2-27b-it": "HF_TOKEN_GEMMA",
    "mistralai/Mistral-Nemo-Instruct-2407": "HF_TOKEN_MISTRAL",
    "gpt-4o-mini": "OPENAI_API_KEY",
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
