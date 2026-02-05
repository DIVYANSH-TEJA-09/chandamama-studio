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

# --- PUZZLE IMPORTS ---
from src.local_llm_multi import generate_response_multi
from src.story_inspired_puzzles.puzzle_generator import CrosswordGenerator
from src.story_inspired_puzzles.prompts import PROMPT_SERIAL_INSPIRED_STORY, PROMPT_CROSSWORD_EXTRACTION
import pandas as pd
import re
# ----------------------

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
    # Added "Puzzle Generator" to the options
    app_mode = st.sidebar.radio("Choose Mode", ["Story Generator", "Serial Generator", "Poem Generator", "Puzzle Generator", "Settings"])
    
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

# --- PUZZLE GENERATOR ---
elif app_mode == "Puzzle Generator":
    st.title("🧩 Story-Inspired Puzzle Generator")
    st.caption("Generate a high-quality story and convert it into a crossword puzzle.")

    # --- PUZZLE SESSION STATE ---
    if 'puzzle_story_text' not in st.session_state:
        st.session_state.puzzle_story_text = ""
    if 'puzzle_layout' not in st.session_state:
        st.session_state.puzzle_layout = None
    if 'puzzle_data' not in st.session_state:
        st.session_state.puzzle_data = None
    
    # ----------------------------

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.subheader("1. Design Story")
        
        # Faceted Inputs (Matching Main App)
        prompt_input = st.text_area("Plot Idea", height=100, placeholder="e.g. A king who lost his crown in a magical lake...", key="puz_prompt")
        
        genres = ["Folklore", "Fantasy", "Moral", "Animal Fable", "Mythology", "Humor", "History", "Adventure"]
        sel_genre = st.selectbox("Genre", genres, index=0, key="puz_genre")
        
        all_keywords = get_keys(global_stats, "top_keywords")
        sel_keywords = st.multiselect("Keywords", all_keywords[:100], placeholder="Select keywords...", key="puz_kw")
        keywords_str = ", ".join(sel_keywords) if sel_keywords else "None"
        
        all_chars = get_keys(global_stats, "top_characters")
        sel_chars = st.multiselect("Characters", all_chars[:100], placeholder="Select characters...", key="puz_ch")
        
        all_locs = get_keys(global_stats, "top_locations")
        sel_locs = st.multiselect("Locations", all_locs[:100], placeholder="Select locations...", key="puz_loc")
        
        st.markdown("<br>", unsafe_allow_html=True)

        if st.button("✨ Generate Story", type="primary", use_container_width=True, key="puz_gen_btn"):
            with st.spinner("Writing a classic Telugu story..."):
                try:
                    # Prepare Prompt
                    # We append facets to user input for the prompt logic
                    full_input = f"{prompt_input} Characters: {', '.join(sel_chars)}. Locations: {', '.join(sel_locs)}."
                    
                    prompt = PROMPT_SERIAL_INSPIRED_STORY.format(
                        genre=sel_genre,
                        keywords=keywords_str,
                        input=full_input
                    )
                    
                    # Stream Response
                    stream = generate_response_multi(
                        model_id=st.session_state["llm_settings"]["model"], # Use Global Settings
                        prompt=prompt,
                        system_prompt="You are a Telugu storyteller.",
                        max_tokens=2500,
                        temperature=0.7,
                        stream=True
                    )
                    
                    with col2:
                         st.subheader("📖 Generated Story")
                         response_text = st.write_stream(stream)
                    
                    st.session_state.puzzle_story_text = response_text
                    # Clear old puzzle
                    st.session_state.puzzle_layout = None
                    st.session_state.puzzle_data = None
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"Error: {e}")

    # If already generated, show story
    if st.session_state.puzzle_story_text and not st.session_state.get('puz_gen_btn'): # Pseudo check
         with col2:
             st.subheader("📖 Generated Story")
             st.markdown(st.session_state.puzzle_story_text)


    # --- STEP 2: CROSSWORD GENERATION ---
    if st.session_state.puzzle_story_text:
        st.divider()
        st.header("2. Generate Crossword")
        
        if st.button("🧩 Create Crossword from Story", type="primary", key="puz_create_btn"):
            with st.spinner("Analyzing story and building grid..."):
                try:
                    # 1. Extract Words & Clues via LLM
                    extract_prompt = PROMPT_CROSSWORD_EXTRACTION.format(
                        story_text=st.session_state.puzzle_story_text
                    )
                    
                    stream = generate_response_multi(
                        model_id=st.session_state["llm_settings"]["model"],
                        prompt=extract_prompt,
                        system_prompt="You are a puzzle generator. Output JSON only.",
                        max_tokens=4000,
                        temperature=0.2, 
                        stream=True
                    )
                    
                    llm_output = ""
                    for chunk in stream:
                        llm_output += chunk
                    
                    # Parse JSON
                    cleaned_output = llm_output.strip()
                    if not cleaned_output:
                         st.error("The AI returned an empty response.")
                         st.stop()
                         
                    if "```json" in cleaned_output:
                        cleaned_output = cleaned_output.split("```json")[1].split("```")[0]
                    elif "```" in cleaned_output:
                         cleaned_output = cleaned_output.split("```")[1].split("```")[0]
                    
                    cleaned_output = cleaned_output.strip()
                    # Basic JSON fix
                    if not cleaned_output.endswith("]"):
                         last_bracket = cleaned_output.rfind("]")
                         if last_bracket != -1:
                             cleaned_output = cleaned_output[:last_bracket+1]
                    
                    try:
                        words_data = json.loads(cleaned_output)
                    except json.JSONDecodeError:
                        # Fallback Regex
                        pattern = r'"answer"\s*:\s*"([^"]+)"\s*,\s*"clue"\s*:\s*"([^"]+)"'
                        matches = re.findall(pattern, cleaned_output)
                        
                        if matches:
                            words_data = [{"answer": m[0], "clue": m[1]} for m in matches]
                            st.warning(f"Recovered {len(words_data)} words via regex.")
                        else:
                            st.error("Invalid puzzle format from AI.")
                            st.stop()
                    
                    # 2. Generate Layout via Python Algorithm
                    generator = CrosswordGenerator() 
                    # 2-Phase Clustering Approach is built into CrosswordGenerator now? 
                    # Note: Existing implementation uses `generate_layout`. 
                    # If we improved it in the playground, we rely on `CrosswordGenerator` class having those improvements.
                    # We updated `puzzle_generator.py` earlier so it should be good.
                    
                    layout = generator.generate_layout(words_data, attempts=100)
                    
                    if layout:
                        st.session_state.puzzle_layout = layout
                        st.session_state.puzzle_data = words_data
                        st.rerun()
                    else:
                        st.error("Could not generate a valid grid. Try again.")
                        
                except Exception as e:
                    st.error(f"Error generating puzzle: {e}")

        # --- DISPLAY PUZZLE ---
        if st.session_state.puzzle_layout:
            layout = st.session_state.puzzle_layout
            
            st.subheader("Crossword Grid")
            
            grid_w = layout['width']
            grid_h = layout['height']
            
            st.markdown(f"""
            <style>
                .cw-grid {{
                    display: grid;
                    grid-template-columns: repeat({grid_w}, 34px);
                    gap: 0px; 
                    margin-top: 20px;
                    margin-bottom: 20px;
                }}
                .cw-cell {{
                    width: 34px;
                    height: 34px;
                    background-color: transparent; 
                    display: flex;
                    align-items: center;
                    justify_content: center;
                    position: relative;
                }}
                .cw-cell-filled {{
                    background-color: #ffffff;
                    color: #000000;
                    border: 1px solid #000;
                    font-weight: bold;
                    font-size: 16px; 
                }}
                .cw-num {{
                    position: absolute;
                    top: 1px;
                    left: 2px;
                    font-size: 9px;
                    color: #555;
                }}
            </style>
            """, unsafe_allow_html=True)
            
            # Render Grid
            grid_html = '<div class="cw-grid">'
            cell_map = {}
            for w in layout['words']:
                start_x = w['start_x']
                start_y = w['start_y']
                direction = w['direction']
                answer = w['answer'] 
                number = w['number']
                
                # Number the start
                if (start_x, start_y) not in cell_map:
                    cell_map[(start_x, start_y)] = {'char': answer[0], 'num': number}
                else:
                     cell_map[(start_x, start_y)]['num'] = number
                
                for i, char in enumerate(answer):
                    cx = start_x + i if direction == 'across' else start_x
                    cy = start_y if direction == 'across' else start_y + i
                    if (cx, cy) not in cell_map:
                        cell_map[(cx, cy)] = {'char': char, 'num': None}
            
            for y in range(grid_h):
                for x in range(grid_w):
                    cell_data = cell_map.get((x, y))
                    if cell_data:
                        num_html = f'<span class="cw-num">{cell_data["num"]}</span>' if cell_data['num'] else ''
                        grid_html += f'<div class="cw-cell cw-cell-filled">{num_html}{cell_data["char"]}</div>'
                    else:
                        grid_html += '<div class="cw-cell" style="opacity:0.2; font-size: 12px;">⭐</div>'
            
            grid_html += '</div>'
            st.markdown(grid_html, unsafe_allow_html=True)
            
            # Clues & Answers
            st.subheader("Clues")
            c1, c2 = st.columns(2)
            
            across_clues = sorted([w for w in layout['words'] if w['direction'] == 'across'], key=lambda x: x['number'])
            down_clues = sorted([w for w in layout['words'] if w['direction'] == 'down'], key=lambda x: x['number'])
            
            with c1:
                st.markdown("**Across**")
                for w in across_clues:
                    st.markdown(f"**{w['number']}.** {w['clue']} ({len(w['answer'])})")
            with c2:
                st.markdown("**Down**")
                for w in down_clues:
                    st.markdown(f"**{w['number']}.** {w['clue']} ({len(w['answer'])})")

            st.markdown("---")
            with st.expander("👁️ Show Answers / Review Key"):
                all_words = sorted(layout['words'], key=lambda x: x['number'])
                data = [{"Number": w['number'], "Direction": w['direction'].title(), "Clue": w['clue'], "Answer": "".join(w['answer'])} for w in all_words]
                st.table(pd.DataFrame(data))




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

        st.subheader("Embedding Model")
        st.info(f"Current Model: **{config.STORY_EMBEDDING_MODEL_NAME}**")
        st.caption("Used for RAG context retrieval.")

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
