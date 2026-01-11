# Contributing to Chandamama Studio

Welcome to the team! This guide will help you set up your environment and work effectively on the project.

## 🚀 Quick Start for New Teammates

Since we don't commit the heavy Database (`qdrant_db/`) to Git, you need to build it locally.

### 1. Clone the Repo
```bash
git clone <repo-url>
cd chandamama-studio
```

### 2. Set Up Virtual Environment (Recommended)

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**Windows:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment
1.  **Copy the template:**
    - **macOS / Linux:** `cp .env.template .env`
    - **Windows:** `copy .env.template .env`
2.  **Add your API Key:**
    - Open `.env` and paste your `OPENAI_API_KEY`.

### 5. ⚡ Build the Database (All-in-One)
Run the master rebuild script. It handles both **Chunk Indexing** (for RAG) and **Story Embeddings** (for The Council).

```bash
python rebuild_db.py
```

**Workflow:**
1.  **Chunk Indexing**: Runs automatically (~10 mins).
2.  **Story Embeddings**: The script will ask `Build Story Embeddings? (y/n)`.
    *   Type `y` if you want to enable "Full Story Retrieval" features.
    *   This ensures `qdrant_db/` is fully populated for all app modes.

---

## 🛠 Workflow

1.  **Issues**: Check the [Issues](issues) tab for assigned tasks.
2.  **Branches**: Create a refined branch for your feature.
    - Format: `feature/your-feature-name` or `fix/bug-description`
    - Example: `feature/add-quiz-mode`
3.  **Testing**:
    - If you modify `story_gen.py`, generate at least 3 stories to verify consistency.
    - If you modify `app.py`, ensure both "Story Weaver" and "Poem Weaver" modes work.

## 🤝 Code Standards

- **Python**: Use clear variable names.
- **Streamlit**: Keep UI logic inside `app.py` or separate UI modules.
- **Secrets**: NEVER commit `.env` or API keys.

## 📝 Submitting Changes

1.  Push your branch.
2.  Open a **Pull Request (PR)**.
3.  Fill out the PR Template (What changed? How to test?).
4.  Request a review from a teammate.
