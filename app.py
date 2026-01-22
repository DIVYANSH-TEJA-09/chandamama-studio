import streamlit as st
import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import Modules
from src.story_gen import generate_story, generate_poem
from src.retrieval.vector_search import StoryEmbeddingsRetriever
from src import config

# Page Config
st.set_page_config(
    page_title="Classic Telugu Studio",
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



# Sidebar Navigation
with st.sidebar:
    st.title("🌙 Classic Telugu Studio")
    # Sidebar - Mode Selection
    st.sidebar.title("Telugu Studio")
    app_mode = st.sidebar.radio("Choose Mode", ["Story Generator", "Serial Generator", "Poem Generator", "Settings"])
    
    # Global Sidebar Stats (Optional)
    st.sidebar.markdown("---")
    st.sidebar.caption(f"📚 Total Stories: {global_stats['total_stories']}")
    
    # Initialize Settings in Session State if not present
    if "llm_settings" not in st.session_state:
        st.session_state["llm_settings"] = {
            "model": config.AVAILABLE_MODELS[0],
            "temperature": 0.7,
            "max_tokens": 3000
        }
    
    if "serial_settings" not in st.session_state:
        st.session_state["serial_settings"] = {
             "max_tokens": 6000,
             "temperature": 0.75
        }
    

        
    # Validation: Logic to auto-fix stale session state (e.g. user had gpt-4o-mini selected)
    if st.session_state["llm_settings"]["model"] not in config.AVAILABLE_MODELS:
        # Silently switch to default
        st.session_state["llm_settings"]["model"] = config.AVAILABLE_MODELS[0]

    st.header("Status")
    st.success("AI System: Online ✅")
        


# --- STORY GENERATOR ---
if app_mode == "Story Generator":
    st.title("📖 Story Generator")
    st.caption("Generate new stories grounded in Classic Telugu Literature.")

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
            with st.spinner("Writing Story..."):
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
                    "locations": sel_locs,
                    "content_type": "SINGLE"
                }

                # Using configured settings
                # story_out is now a Generator
                story_generator = generate_story(facets, context_text, llm_params=st.session_state["llm_settings"])
                
                with col_preview:
                    st.subheader("2. Output")
                    st.markdown("---")
                    # STREAMING OUTPUT
                    full_response = st.write_stream(story_generator)
                    st.divider()
                    
                    # Persist final result
                    st.session_state["gen_story"] = full_response
                    st.session_state["rag_ctx"] = context_story_excerpts



elif app_mode == "Serial Generator":
    st.title("📚 Serial Generator (ధారావాహిక)")
    st.caption("Generate continuous multi-chapter serial stories with cliffhangers!")

    # Use settings from session state
    ser_max_tokens = st.session_state["serial_settings"]["max_tokens"]
    ser_temp = st.session_state["serial_settings"]["temperature"]
        
    serial_llm_settings = st.session_state["llm_settings"].copy()
    serial_llm_settings["max_tokens"] = ser_max_tokens
    serial_llm_settings["temperature"] = ser_temp
    # ---------------------------------------------------------

    col_ctrl, col_preview = st.columns([1, 1], gap="large")

    with col_ctrl:
        st.subheader("1. Design Serial")

        prompt_input = st.text_area("Serial Plot Idea", height=100, placeholder="e.g. A treasure hunt across ancient kingdoms...")
        
        genres = ["Folklore", "Fantasy", "Mystery", "Adventure", "Mythology", "Historical Fiction", "Family Drama"]
        sel_genre = st.selectbox("Genre", genres, index=3) # Default Adventure

        # Chapter Slider
        num_chapters = st.slider("Number of Chapters", min_value=2, max_value=5, value=3)

        all_keywords = get_keys(global_stats, "top_keywords")
        sel_keywords = st.multiselect("Keywords", all_keywords[:100], key="ser_key")
        
        all_chars = get_keys(global_stats, "top_characters")
        sel_chars = st.multiselect("Characters", all_chars[:100], key="ser_char")
        
        all_locs = get_keys(global_stats, "top_locations")
        sel_locs = st.multiselect("Locations", all_locs[:100], key="ser_loc")

        st.markdown("<br>", unsafe_allow_html=True)

        serial_gen_clicked = st.button("✨ Start Serial", type="primary", use_container_width=True)
        if serial_gen_clicked:
            with st.spinner("Generating Serial Story... (This may take a while)"):
                 # RAG Logic (Same as Story, but biased if possible - implicitly via prompt)
                search_q = f"Serial Story {prompt_input} {sel_genre} {' '.join(sel_keywords)}"
                rag_results = retriever.retrieve_points(search_q)
                
                context_story_excerpts = []
                full_texts = []
                for p in rag_results:
                    title = p.payload.get('title', 'Unknown')
                    text = p.payload.get('text', '')
                    context_story_excerpts.append(f"### {title}\n{text[:200]}...")
                    full_texts.append(f"Title: {title}\nStory: {text}")

                context_text = "\\n\\n".join(full_texts)

                facets = {
                    "genre": sel_genre,
                    "prompt_input": prompt_input,
                    "keywords": sel_keywords,
                    "characters": sel_chars,
                    "locations": sel_locs,
                    "content_type": "SERIAL",
                    "num_chapters": num_chapters
                }

                # Use Serial Settings
                # story_out is now a Generator
                story_generator = generate_story(facets, context_text, llm_params=serial_llm_settings)
                
                with col_preview:
                     st.subheader("2. Your Serial")
                     st.markdown("---")
                     # STREAMING OUTPUT
                     full_serial = st.write_stream(story_generator)
                     st.divider()
                     
                     st.session_state["gen_serial"] = full_serial
                     st.session_state["rag_ctx_serial"] = context_story_excerpts
                     
                     st.download_button("Download Serial", full_serial, file_name="serial_story.txt")
    
    if not serial_gen_clicked:
        with col_preview:
            st.subheader("2. Your Serial")
            if "gen_serial" in st.session_state and st.session_state["gen_serial"]:
                 st.markdown(st.session_state["gen_serial"])
                 st.divider()
                 st.download_button("Download Serial", st.session_state["gen_serial"], file_name="serial_story.txt")
            else:
                 st.info("Design your serial and click correct 'Start Serial'!")




# --- POEM GENERATOR ---
elif app_mode == "Poem Generator":
    st.title("🪕 Poem Generator")
    st.caption("Compose lyrical Telugu poems and songs.")
    
    col_p1, col_p2 = st.columns([1, 1], gap="large")
    
    with col_p1:
        st.subheader("1. Design Poem")
        
        styles = ["Metric Poem (Padyam)", "Song (Paata)", "Free Verse (Vachana Kavita)"]
        sel_style = st.selectbox("Style", styles)
        
        poem_keywords = get_keys(poem_stats, "top_keywords")
        sel_p_keywords = st.multiselect("Themes / Keywords", poem_keywords[:50], placeholder="Select nature themes...")
        
        poem_clicked = st.button("🎶 Compose Poem", type="primary", use_container_width=True)
        if poem_clicked:
            with st.spinner("Composing... (This may take time)..."):
                    facets = {
                        "style": sel_style,
                        "keywords": sel_p_keywords,
                        "theme": ", ".join(sel_p_keywords) if sel_p_keywords else "Nature/Moral"
                    }
                    # Using configured settings
                    poem_generator = generate_poem(facets, llm_params=st.session_state["llm_settings"])
                    
                    with col_p2:
                         st.subheader("2. Output")
                         st.markdown("---")
                         full_poem = st.write_stream(poem_generator)
                         st.session_state["gen_poem"] = full_poem

    if not poem_clicked:
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
        available_models = config.AVAILABLE_MODELS
        
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
    st.divider()
    
    st.subheader("Serial Story Settings")
    st.caption("Specific settings for multi-chapter serials.")

    ser_tokens = st.slider("Serial Max Tokens", 2000, 12000, st.session_state["serial_settings"]["max_tokens"], step=500, key="set_ser_tok")
    ser_temp_val = st.slider("Serial Connectivity", 0.0, 1.0, st.session_state["serial_settings"]["temperature"], key="set_ser_temp")

    if st.button("Save Serial Settings"):
         st.session_state["serial_settings"]["max_tokens"] = ser_tokens
         st.session_state["serial_settings"]["temperature"] = ser_temp_val
         st.success("Serial settings updated!")
         
    st.info("Settings are automatically saved for this session.")
