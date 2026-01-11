
import streamlit as st
import os
import sys
import json
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Ensure we can import from src
# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
# Get the directory of the current file (retrieval_logics_test)
current_dir = os.path.dirname(current_file_path)
# Get the parent directory (src)
src_dir = os.path.dirname(current_dir)
# Get the project root
project_root = os.path.dirname(src_dir)

# Add src to sys.path
if src_dir not in sys.path:
    sys.path.append(src_dir)

# Add project root to sys.path (needed for 'src' package imports)
if project_root not in sys.path:
    sys.path.append(project_root)

from retrieval_logics_test.contextual_retrieval import ContextualRetriever
from retrieval_logics_test.full_story_retrieval import FullStoryRetriever
from retrieval_logics_test.simple_retrieval import SimpleRetriever
from retrieval_logics_test.hybrid_retrieval import HybridRetriever
from retrieval_logics_test.story_embeddings_retrieval import StoryEmbeddingsRetriever
from retrieval_logics_test.local_gen_utils import generate_hybrid_story
from story_gen import generate_story

# --- Configuration & Stats Loading ---
STATS_PATH = os.path.join(project_root, "stats", "global_stats.json")

# Helper: Load Stats
@st.cache_data
def load_stats(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}

# Helper: Safe Key Access
def get_keys(stats_dict, key_name):
    data = stats_dict.get(key_name, {})
    if isinstance(data, dict):
        return list(data.keys())
    return []

global_stats = load_stats(STATS_PATH)

# Page Config
st.set_page_config(layout="wide", page_title="RAG Strategy 5-Way Comparator")

st.title("🏹 RAG Retrieval Strategy Comparator (5-Way)")
st.markdown("Compare 5 distinct logic paths for story generation side-by-side.")

# Initialize Retrievers (Cached)
@st.cache_resource
def get_retrievers():
    try:
        r1 = ContextualRetriever(top_k=3)
        r2 = FullStoryRetriever(top_k=2)
        r3 = SimpleRetriever(top_k=7)
        r4 = HybridRetriever(content_top_k=3)
        r5 = StoryEmbeddingsRetriever(top_k=3)
        return r1, r2, r3, r4, r5
    except Exception as e:
        st.error(f"Failed to initialize retrievers: {e}")
        return None, None, None, None, None

retriever1, retriever2, retriever3, retriever4, retriever5 = get_retrievers()

if not all([retriever1, retriever2, retriever3, retriever4, retriever5]):
    st.stop()

# --- Faceted Inputs ---
st.sidebar.header("Story Parameters")

# 1. Genre
genres = ["Folklore", "Fantasy", "Moral", "Animal Fable", "Mythology", "Humor", "History", "Adventure"]
sel_genre = st.sidebar.selectbox("Genre", genres, index=0)

# 2. Keywords
all_keywords = get_keys(global_stats, "top_keywords")
if not all_keywords:
    all_keywords = ["magic", "king", "forest", "rabbit"]
sel_keywords = st.sidebar.multiselect("Keywords", all_keywords[:100])

# 3. Characters
all_chars = get_keys(global_stats, "top_characters")
if not all_chars:
    all_chars = ["King", "Queeen", "Lion"]
sel_chars = st.sidebar.multiselect("Characters", all_chars[:100])

# 4. Locations
all_locs = get_keys(global_stats, "top_locations")
if not all_locs:
    all_locs = ["Village", "Palace", "Forest"]
sel_locs = st.sidebar.multiselect("Locations", all_locs[:100])

st.sidebar.divider()
st.sidebar.subheader("Select Strategies to Run")
use_contextual = st.sidebar.checkbox("1. Contextual", value=True)
use_full = st.sidebar.checkbox("2. Full Story", value=True)
use_simple = st.sidebar.checkbox("3. Simple", value=True)
use_hybrid = st.sidebar.checkbox("4. Hybrid", value=True)
use_embedded = st.sidebar.checkbox("5. Story Embeddings", value=True)

# Main Area Input
with st.form("query_form"):
    st.subheader("1. Design Story")
    prompt_input = st.text_area("Plot Idea", height=100, placeholder="e.g. A magic parrot...")
    submitted = st.form_submit_button("Generate & Compare All 4")

if submitted:
    # Determine active strategies
    strategies_map = [
        (use_contextual, "Contextual", retriever1),
        (use_full, "Full Story", retriever2),
        (use_simple, "Simple", retriever3),
        (use_hybrid, "Hybrid", retriever4),
        (use_embedded, "Story Embeddings", retriever5)
    ]
    
    active_strategies = [s for s in strategies_map if s[0]]
    
    if not active_strategies:
        st.error("⚠️ Please select at least one strategy from the sidebar.")
    else:
        # Create Dynamic Columns
        cols = st.columns(len(active_strategies))
        col_iter = iter(cols)
        
        # Facets
        facets = {
            "genre": sel_genre,
            "keywords": sel_keywords,
            "characters": sel_chars,
            "locations": sel_locs,
            "prompt_input": prompt_input
        }
        search_query = f"{prompt_input} {sel_genre} {' '.join(sel_keywords)} {' '.join(sel_chars)}"

        # --- Strategy 1: Contextual Chunks ---
        if use_contextual:
            with next(col_iter):
                st.header("1. Contextual")
                st.caption("Top 3 + Neighbors")
                
                with st.spinner("Gen 1..."):
                    context1 = retriever1.retrieve(search_query)
                    with st.expander("Ctx 1"):
                        st.text(context1[:1000] + "..." if len(context1) > 1000 else context1)
                    story1 = generate_story(facets, context_text=context1)
                    st.markdown(story1)

        # --- Strategy 2: Full Story ---
        if use_full:
            with next(col_iter):
                st.header("2. Full Story")
                st.caption("Hydrate Entire Story")
                
                with st.spinner("Gen 2..."):
                    context2 = retriever2.retrieve(search_query)
                    with st.expander("Ctx 2"):
                        st.text(context2[:1000] + "..." if len(context2) > 1000 else context2)
                    story2 = generate_story(facets, context_text=context2)
                    st.markdown(story2)

        # --- Strategy 3: Simple (7 Chunks) ---
        if use_simple:
            with next(col_iter):
                st.header("3. Simple")
                st.caption("Baseline: Top 7 Chunks")
                
                with st.spinner("Gen 3..."):
                    context3 = retriever3.retrieve(search_query)
                    with st.expander("Ctx 3"):
                        st.text(context3[:1000] + "..." if len(context3) > 1000 else context3)
                    story3 = generate_story(facets, context_text=context3)
                    st.markdown(story3)

        # --- Strategy 4: Hybrid (2-Channel) ---
        if use_hybrid:
            with next(col_iter):
                st.header("4. Hybrid")
                st.caption("Style (Full) + Content (Ctx)")
                
                with st.spinner("Gen 4..."):
                    hybrid_ctx = retriever4.retrieve_hybrid(search_query, sel_genre)
                    
                    with st.expander("Ctx 4 (Style)"):
                        st.text(hybrid_ctx['style'][:500] + "...")
                    with st.expander("Ctx 4 (Content)"):
                        st.text(hybrid_ctx['content'][:500] + "...")
                        
                    story4 = generate_hybrid_story(
                        facets, 
                        style_context=hybrid_ctx['style'],
                        content_context=hybrid_ctx['content']
                    )
                    st.markdown(story4)

        # --- Strategy 5: Story Embeddings ---
        if use_embedded:
            with next(col_iter):
                st.header("5. Story Embeddings")
                st.caption("Vector Search on Full Stories")
                
                with st.spinner("Gen 5..."):
                    context5 = retriever5.retrieve(search_query)
                    with st.expander("Ctx 5"):
                        st.text(context5[:1000] + "..." if len(context5) > 1000 else context5)
                    story5 = generate_story(facets, context_text=context5)
                    st.markdown(story5)
