# Contributing to Chandamama Studio

Welcome to the team! This guide will help you set up your environment and work effectively on the project.

## 🚀 Quick Start for New Teammates

Since we don't commit the heavy Database (`qdrant_db/`) to Git, you need to build it locally.

1.  **Clone the Repo**:
    ```bash
    git clone <repo-url>
    cd chandamama-studio
    ```

2.  **Install Dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

3.  **Setup Environment**:
    - Copy `.env.template` to `.env`
    - Add your `OPENAI_API_KEY` (Ask lead dev if you don't have one).

4.  **⚡ Build the Database**:
    Run this script to index the chandamama chunks locally.
    ```bash
    python rebuild_db.py
    ```
    *Wait ~10 mins for it to finish.*

5.  **Run the App**:
    ```bash
    streamlit run app.py
    ```

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
