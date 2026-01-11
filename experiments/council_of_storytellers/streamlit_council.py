
import streamlit as st
import os
import sys
import json
import time
from dotenv import load_dotenv

# Ensure we can import from src
# Get the absolute path of the current file
current_file_path = os.path.abspath(__file__)
# src/council_of_storytellers
current_dir = os.path.dirname(current_file_path)
# src
src_dir = os.path.dirname(current_dir)
# project root
project_root = os.path.dirname(src_dir)

# Add project root to sys.path
if project_root not in sys.path:
    sys.path.append(project_root)

# Load env vars
load_dotenv()

from src import config
from src.retrieval_logics_test.story_embeddings_retrieval import StoryEmbeddingsRetriever
from src.council_of_storytellers.evaluator import _construct_prompt 
from src.local_llm_multi import generate_response_multi

# Helper: Load Stats
STATS_PATH = os.path.join(project_root, "stats", "global_stats.json")
@st.cache_data
def load_stats(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}

def get_keys(stats_dict, key_name):
    data = stats_dict.get(key_name, {})
    if isinstance(data, dict):
        return list(data.keys())
    return []

global_stats = load_stats(STATS_PATH)

st.set_page_config(layout="wide", page_title="Council of Storytellers")

st.title("🏰 Council of Storytellers")
st.markdown("One Prompt. One Context. Multiple Master Storytellers.")

# Initialize Retriever (Cached)
@st.cache_resource
def get_retriever():
    try:
        return StoryEmbeddingsRetriever(top_k=2)
    except Exception as e:
        st.error(f"Failed to initialize retriever: {e}")
        return None

retriever = get_retriever()

if not retriever:
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
st.sidebar.subheader("Council Members")
selected_models = st.sidebar.multiselect("Active Models", config.COUNCIL_MODELS, default=config.COUNCIL_MODELS)

# Main Area Input
with st.form("council_form"):
    st.subheader("1. Propose Plot to the Council")
    prompt_input = st.text_area("Plot Idea", height=100, placeholder="e.g. A magic parrot...")
    submitted = st.form_submit_button("Summon the Council")

if submitted and selected_models:
    # Facets
    facets = {
        "genre": sel_genre,
        "keywords": sel_keywords,
        "characters": sel_chars,
        "locations": sel_locs,
        "prompt_input": prompt_input
    }
    search_query = f"{prompt_input} {sel_genre} {' '.join(sel_keywords)} {' '.join(sel_chars)}"

    # 1. Retrieve Context
    with st.spinner("Retrieving Ancient Wisdom (Full Story Embeddings)..."):
        context_text = retriever.retrieve(search_query)
        
    with st.expander("📜 View Retrieved Context (Shared by All Models)"):
        st.text(context_text)

    # 2. Generate Columns
    cols = st.columns(len(selected_models))
    
    # 3. Iterate Models
    for idx, model_id in enumerate(selected_models):
        with cols[idx]:
            st.markdown(f"**{model_id.split('/')[-1]}**")
            status_container = st.empty()
            
            prompt = _construct_prompt(facets, context_text)
            
            try:
                status_container.info("Writing...")
                start_time = time.time()
                
                story_output = generate_response_multi(
                    model_id=model_id,
                    prompt=prompt,
                    system_prompt="You are a creative storyteller.",
                    max_tokens=3000,
                    temperature=0.7
                )
                
                elapsed = time.time() - start_time
                status_container.success(f"{elapsed:.1f}s")
                
                st.markdown("---")
                st.markdown(story_output)
                
            except Exception as e:
                status_container.error("Failed")
                st.error(f"Error: {e}")

elif submitted and not selected_models:
    st.error("Please select at least one model from the sidebar.")
