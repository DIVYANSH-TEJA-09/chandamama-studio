import streamlit as st
import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import Modules
from src.story_gen import generate_story, generate_poem
from src.retrieval_logics_test.story_embeddings_retrieval import StoryEmbeddingsRetriever
from src import config

# Page Config
st.set_page_config(
    page_title="Chandamama Studio",
    page_icon="🌙",
    layout="wide"
)

# --- Initialization ---
@st.cache_resource
def load_retriever():
    return StoryEmbeddingsRetriever(top_k=2)

try:
    retriever = load_retriever()
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

global_stats = load_stats(config.STATS_PATH)
poem_stats = load_stats(config.POEM_STATS_PATH)

# Helper: Safe Key Access
def get_keys(stats_dict, key_name):
    data = stats_dict.get(key_name, {})
    if isinstance(data, dict):
        return list(data.keys())
    return []

# Helper: Safe Key Access
def get_keys(stats_dict, key_name):
    data = stats_dict.get(key_name, {})
    if isinstance(data, dict):
        return list(data.keys())
    return []

# Sidebar Navigation
with st.sidebar:
    st.title("🌙 Chandamama Studio")
    app_mode = st.radio("Choose Mode", ["Story Weaver", "Poem Weaver", "Settings"])
    
    st.divider()
    
    # Initialize Settings in Session State if not present
    if "llm_settings" not in st.session_state:
        st.session_state["llm_settings"] = {
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 3000
        }

    st.header("Status")
    # Show current model
    st.info(f"Model: {st.session_state['llm_settings']['model']}")
        
    st.divider()
    st.header("Archive Stats")
    if app_mode == "Story Weaver":
        st.markdown(f"**Total Stories:** {global_stats.get('total_stories', 'Unknown')}")
        st.markdown(f"**Unique Characters:** {len(global_stats.get('top_characters', []))}")
    elif app_mode == "Poem Weaver":
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
            with st.spinner(f"Searching Archive & Writing using {st.session_state['llm_settings']['model']}..."):
                # RAG
                search_q = f"{prompt_input} {sel_genre} {' '.join(sel_keywords)} {' '.join(sel_chars)}"
                rag_results = retriever.retrieve_points(search_q)
                    
                context_story_excerpts = []
                # Build context from Full Stories
                full_texts = []
                for p in rag_results:
                    title = p.payload.get('title', 'Unknown')
                    story_id = p.payload.get('story_id', 'Unknown ID')
                    text = p.payload.get('text', '')
                    
                    # For UI display
                    context_story_excerpts.append(f"### {title} (ID: {story_id})\n{text[:200]}...")
                    
                    # For LLM Context
                    full_texts.append(f"Title: {title}\nStory: {text}")

                context_text = "\n\n".join(full_texts)
                
                facets = {
                    "genre": sel_genre,
                    "prompt_input": prompt_input,
                    "keywords": sel_keywords,
                    "characters": sel_chars,
                    "locations": sel_locs
                }
                
                # Using configured settings
                story_out = generate_story(facets, context_text, llm_params=st.session_state["llm_settings"])
                
                st.session_state["gen_story"] = story_out
                st.session_state["rag_ctx"] = context_story_excerpts

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
            with st.spinner("Composing... (This may take time)..."):
                    facets = {
                        "style": sel_style,
                        "keywords": sel_p_keywords,
                        "theme": ", ".join(sel_p_keywords) if sel_p_keywords else "Nature/Moral"
                    }
                    # Using configured settings
                    poem_out = generate_poem(facets, llm_params=st.session_state["llm_settings"])
                    st.session_state["gen_poem"] = poem_out

    with col_p2:
        st.subheader("2. Output")
        st.markdown("---")
        if "gen_poem" in st.session_state:
            st.markdown(st.session_state["gen_poem"])
        else:
            st.info("Poem output will appear here.")

# --- SETTINGS ---
elif app_mode == "Settings":
    st.title("⚙️ AI Configuration")
    st.caption("Customize the models and generation parameters.")
    
    st.divider()
    
    col_s1, col_s2 = st.columns([1, 1], gap="large")
    
    with col_s1:
        st.subheader("Model Selection")
        
        # Load Council Models from Config
        available_models = config.COUNCIL_MODELS
        
        # Current Value
        curr_model = st.session_state["llm_settings"]["model"]
        try:
            curr_idx = available_models.index(curr_model)
        except ValueError:
            curr_idx = 0
            
        sel_model = st.selectbox("LLM Model", available_models, index=curr_idx)
        st.session_state["llm_settings"]["model"] = sel_model
        
        if "groq" in sel_model.lower() or "llama" in sel_model.lower() or "mixtral" in sel_model.lower():
             st.success("⚡ Groq / Fast Inference Enabled")
        
        st.markdown("---")
        
    with col_s2:
        st.subheader("Generation Parameters")
        
        curr_temp = st.session_state["llm_settings"]["temperature"]
        sel_temp = st.slider("Temperature (Creativity)", 0.0, 1.0, curr_temp, 0.1)
        st.session_state["llm_settings"]["temperature"] = sel_temp
        
        curr_max = st.session_state["llm_settings"]["max_tokens"]
        sel_max = st.number_input("Max Tokens", 100, 8192, curr_max, 100)
        st.session_state["llm_settings"]["max_tokens"] = sel_max
        
    st.divider()
    st.info("Settings are automatically saved for this session.")
