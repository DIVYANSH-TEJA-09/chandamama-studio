# Research Report: Chandamama Studio

## 1. Project Objective
The goal was to modernize the access and creativity around the **Chandamama** magazine archive (1947–2012), a cultural treasure of Telugu children's literature. 
**Key Challenge:** The archive consisted of thousands of scanned PDFs and disparate JSON files with inconsistent metadata. The objective was to create an AI-powered "Story Weaver" that could generate *new* stories grounded in the archive's specific style and tone.

## 2. Methodology & Journey

### Phase 1: Data Alignment & Cleanup
- **Initial State:** Metadata was fragmented across year-based folders.
- **Action:** 
    - Analyzed the folder structure (`1947-2012/`).
    - Created scripts (`utils/aggregate_stats.py`) to scan 755+ JSON files.
    - Aggregated 10,000+ stories, extracting unique characters, locations, and keywords.
    - Result: `global_stats.json` became the "Brain" of the application, powering the UI facets.

### Phase 2: RAG Implementation (Retrieval Augmented Generation)
- **Challenge:** LLMs hallucinate non-Chandamama elements (e.g., modern slang, Western tropes).
- **Solution:** Integrated **Qdrant** (Vector Database).
    - **Indexing:** Processed text chunks using `intfloat/multilingual-e5-base` (optimized for Telugu).
    - **Retrieval:** Implemented a pipeline where User Input -> Semantic Search -> Top 3 Context Chunks -> AI Prompt.
    - **Outcome:** The AI now sees actual excerpts (e.g., "Tenali Rama's wit") before writing, ensuring stylistic consistency.

### Phase 3: UI/UX Revamp (Streamlit)
- **Evolution:** Moved from a basic Search/RAG tabs interface to a unified "Story Weaver" dashboard.
- **Faceted Search:** 
    - Replaced open text inputs with **Multi-select widgets** powered by `global_stats.json`.
    - Allowed users to mix-and-match: "Folklore" + "Magic" + "Forest".
- **Result:** A "No-Code" creativity tool where users guide the AI without needing complex prompting skills.

### Phase 4: Poem Weaver (New Feature)
- **Insight:** The archive contains 60+ poems and songs that were underutilized.
- **Action:** 
    - Created a dedicated stats aggregation for poems (`stats/poem_stats.json`).
    - Built a specialized "Poem Weaver" mode in the UI.
    - Prompt Engineering: Tuned the AI to generate "Padyam" (Metric) and "Paata" (Song) styles specific to Telugu literature.

## 3. Technical Architecture
- **Frontend**: Streamlit (Python)
- **Backend/Logic**: OpenAI GPT-4o-mini (Reasoning/Generation)
- **Database**: Qdrant (Local Vector DB)
- **Embeddings**: `intfloat/multilingual-e5-base`
- **Data Pipeline**: Custom Python scripts for scrubbing and aggregation.

## 4. Challenges & Solutions
| Challenge | Solution |
| :--- | :--- |
| **Data Privacy/Size** | The 300MB Vector DB was too large for Git. Implemented a "Seed Script" (`rebuild_db.py`) to allow teammates to regenerate the DB locally from source JSONs. |
| **Metadata Gaps** | Some files lacked specific genre tags. Implemented fallback logic (`generate_normalized_stats.py`) to categorize them based on keywords. |
| **Language Support** | Telugu tokenization issues. Switched to `multilingual-e5` which handles Dravidian languages better than standard BERT models. |

## 5. Future Recommendations
- **Interactive Puzzles:** Identified 54 "Quiz" items in the archive. Recommended processing these into a "Daily Riddle" game.
- **Visuals:** Future integration of diffusion models to generate Chandamama-style line art for the stories.

## 6. Conclusion
Chandamama Story Weaver 2.0 successfully bridges the gap between static archives and dynamic AI generation. By tightly coupling RAG with a structured metadata taxonomy, we achieved a system that respects the source material's cultural integrity while enabling infinite new creativity.
