# Classic Telugu Studio 🌙

An AI-powered application to explore, search, and "weave" new stories inspired by Classic Telugu Literature.

## Features
- **📖 Story Weaver**: Generate *new* stories in strict classic style, grounded in actual archive content (RAG).
- **🏛️ The Council**: Evaluate story quality across 5 top LLMs (GPT-4o, Qwen 2.5, Llama 3.1, etc.).
- **🪕 Poem Weaver**: Compose new Telugu poems and songs based on archive themes.
- **🔍 RAG Search**: Semantically search full stories using `Alibaba-NLP/gte-multilingual-base` (8k context).
- **📊 Analytics**: View stats on 10,000+ stories (Authors, Characters, Locations).

## 🧠 System Architecture (RAG Flow)

```mermaid
graph LR
    User["User Plot Idea"] --> Retriever["Story Embeddings Retriever"]
    Retriever -- Search --> Qdrant[("Qdrant DB")]
    Qdrant -- Return Top 2 --> Context["Full Story Context"]
    Context --> LLM["LLM (GPT-4o-mini)"]
    LLM --> Story["New Chandamama Story"]
```

## Setup & Installation

### 1. Requirements
- Python 3.9+
- OpenAI API Key

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```
*(Ensure `qdrant-client`, `sentence-transformers`, `streamlit`, `openai`, `python-dotenv` are installed)*

### 3. Environment Variables
1. Copy `.env.template` to `.env`.
2. Add your `OPENAI_API_KEY`.
```bash
cp .env.template .env
```

## How to Run

### Run the App
```bash
streamlit run app.py
```

### Modes
- **Online Mode (RAG Enabled)**: Requires `qdrant_db/` folder to exist.
- **Offline Mode**: If `qdrant_db/` is missing, the app runs in "Creative Mode" (Uses AI knowledge only, no archive context).

## Collaboration & Deployment

**Cloud Deployment is Recommended** (Zero Setup):

1. **Qdrant Cloud**: Create a free cluster at [cloud.qdrant.io](https://cloud.qdrant.io).
2. **Environment**: Update `.env` with:
   ```bash
   QDRANT_URL="your-cloud-url"
   QDRANT_API_KEY="your-api-key"
   ```
3. **Populate Data**:
   Run the rebuild script **locally** to push data to the cloud:
   ```bash
   python rebuild_db.py
   # Select 'y' when asked to build Story Embeddings
   ```
4. **Run App**: 
   ```bash
   streamlit run app.py
   ```
   The app will automatically detect cloud credentials and connect.

## Project Structure
- `app.py`: Main Streamlit application.
- `src/`: Core logic (`story_gen.py`, `rag.py`).
- `utils/`: Data processing scripts (`aggregate_stats.py`).
- `stats/`: Aggregated JSON statistics (`global_stats.json`, `poem_stats.json`).
- `qdrant_db/`: Vector Database (Local).
- `chunks/`: Processed text chunks for indexing.

## Research Notes
This project demonstrates **Retrieval Augmented Generation (RAG)** applied to low-resource languages (Telugu) and specific cultural archives. See `report.md` for full research journey.
h