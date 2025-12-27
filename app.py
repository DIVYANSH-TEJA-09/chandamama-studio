import streamlit as st
import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add src to path
sys.path.append(os.path.abspath("src"))

# Import Modules
# Import Modules
from src.story_gen import generate_story, generate_poem
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue, MatchAny
from sentence_transformers import SentenceTransformer

# Configuration
STATS_PATH = "stats/global_stats.json"
POEM_STATS_PATH = "stats/poem_stats.json"
QDRANT_PATH = os.getenv("QDRANT_PATH", "d:/Viswam_Projects/chandamama-studio/qdrant_db")
COLLECTION_NAME = "chandamama_chunks"
MODEL_NAME = "intfloat/multilingual-e5-base"

# Page Config
st.set_page_config(
    page_title="Chandamama Studio",
    page_icon="🌙",
    layout="wide"
)

# --- Initialization ---
@st.cache_resource
def load_resources():
    client = QdrantClient(path=QDRANT_PATH)
    model = SentenceTransformer(MODEL_NAME)
    return client, model

try:
    client, model = load_resources()
except Exception as e:
    st.error(f"Failed to load AI resources: {e}")
    st.stop()

# Load Stats
@st.cache_data
def load_stats(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception as e:
        return {}

global_stats = load_stats(STATS_PATH)
poem_stats = load_stats(POEM_STATS_PATH)

# Helper: Embedding
def get_embedding(text):
    return model.encode(f"query: {text}", normalize_embeddings=True).tolist()

# Helper: Search
def perform_rag_search(query_text, limit=5):
    embedding = get_embedding(query_text)
    filters = Filter(must=[FieldCondition(key="language", match=MatchValue(value="TELUGU"))])
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=embedding,
        query_filter=filters,
        limit=limit,
        with_payload=True
    ).points
    return results

# Helper: Safe Key Access
def get_keys(stats_dict, key_name):
    data = stats_dict.get(key_name, {})
    if isinstance(data, dict):
        return list(data.keys())
    return []

# Sidebar Navigation
with st.sidebar:
    st.title("🌙 Chandamama Studio")
    app_mode = st.radio("Choose Mode", ["Story Weaver", "Poem Weaver"])
    
    st.divider()
    st.header("Status")
    if os.getenv("OPENAI_API_KEY"):
        st.success("AI Model: Active ✅")
    else:
        st.error("AI Model: Missing Key ❌")
        
    st.divider()
    st.header("Archive Stats")
    if app_mode == "Story Weaver":
        st.markdown(f"**Total Stories:** {global_stats.get('total_stories', 'Unknown')}")
        st.markdown(f"**Unique Characters:** {len(global_stats.get('top_characters', []))}")
    else:
        st.markdown(f"**Total Poems:** {poem_stats.get('total_poems', 0)}")
        st.markdown(f"**Poem Keywords:** {len(poem_stats.get('top_keywords', []))}")

# --- STORY WEAVER ---
if app_mode == "Story Weaver":
    st.title("📖 Story Weaver")
    st.caption("Weave new stories grounded in the Chandamama Archive.")

    col_ctrl, col_preview = st.columns([1, 1], gap="large")

    with col_ctrl:
        st.subheader("1. Design Story")
        
        prompt_input = st.text_area("Plot Idea", height=100, placeholder="e.g. A magic parrot...")
        
        genres = ["Folklore", "Fantasy", "Moral", "Animal Fable", "Mythology", "Humor", "History", "Adventure"]
        sel_genre = st.selectbox("Genre", genres, index=0)
        
        all_keywords = get_keys(global_stats, "top_keywords")
        sel_keywords = st.multiselect("Keywords", all_keywords[:100])
        
        all_chars = get_keys(global_stats, "top_characters")
        sel_chars = st.multiselect("Characters", all_chars[:100])
        
        all_locs = get_keys(global_stats, "top_locations")
        sel_locs = st.multiselect("Locations", all_locs[:100])

        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("✨ Generate Story", type="primary", use_container_width=True):
            if not os.getenv("OPENAI_API_KEY"):
                st.error("Missing API Key")
            else:
                with st.spinner("Searching Archive & Writing..."):
                    # RAG
                    search_q = f"{prompt_input} {sel_genre} {' '.join(sel_keywords)} {' '.join(sel_chars)}"
                    rag_results = perform_rag_search(search_q, limit=3)
                    
                    context_chunks = []
                    for p in rag_results:
                        chunk_id = p.payload.get('chunk_id', 'Unknown ID')
                        context_chunks.append(f"[Excerpt from {p.payload.get('title', 'Unknown')} (Chunk ID: {chunk_id})]: {p.payload.get('text', '')}")
                    context_text = "\n\n".join(context_chunks)
                    
                    facets = {
                        "genre": sel_genre,
                        "prompt_input": prompt_input,
                        "keywords": sel_keywords,
                        "characters": sel_chars,
                        "locations": sel_locs
                    }
                    
                    story_out = generate_story(facets, context_text)
                    st.session_state["gen_story"] = story_out
                    st.session_state["rag_ctx"] = context_chunks

    with col_preview:
        st.subheader("2. Output")
        st.markdown("---")
        if "gen_story" in st.session_state:
            st.markdown(st.session_state["gen_story"])
            st.divider()
            if "rag_ctx" in st.session_state:
                with st.expander("📚 Archive Context Used"):
                    for c in st.session_state["rag_ctx"]:
                        st.text(c[:300] + "...")
        else:
            st.info("Story output will appear here.")

# --- POEM WEAVER ---
elif app_mode == "Poem Weaver":
    st.title("🪕 Poem Weaver")
    st.caption("Compose lyrical Telugu poems and songs.")
    
    col_p1, col_p2 = st.columns([1, 1], gap="large")
    
    with col_p1:
        st.subheader("1. Design Poem")
        
        styles = ["Metric Poem (Padyam)", "Song (Paata)", "Free Verse (Vachana Kavita)"]
        sel_style = st.selectbox("Style", styles)
        
        poem_keywords = get_keys(poem_stats, "top_keywords")
        sel_p_keywords = st.multiselect("Themes / Keywords", poem_keywords[:50], placeholder="Select nature themes...")
        
        if st.button("🎶 Compose Poem", type="primary", use_container_width=True):
            if not os.getenv("OPENAI_API_KEY"):
                st.error("Missing API Key")
            else:
                with st.spinner("Composing..."):
                    facets = {
                        "style": sel_style,
                        "keywords": sel_p_keywords,
                        "theme": ", ".join(sel_p_keywords) if sel_p_keywords else "Nature/Moral"
                    }
                    poem_out = generate_poem(facets)
                    st.session_state["gen_poem"] = poem_out

    with col_p2:
        st.subheader("2. Output")
        st.markdown("---")
        if "gen_poem" in st.session_state:
            st.markdown(st.session_state["gen_poem"])
        else:
            st.info("Poem output will appear here.")
