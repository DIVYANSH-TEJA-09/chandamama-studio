import streamlit as st
import sys
import os
import time
import json
import pandas as pd
from dotenv import load_dotenv

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src import config
from src.local_llm_multi import generate_response_multi
from src.story_inspired_puzzles.puzzle_generator import CrosswordGenerator
from src.story_inspired_puzzles.prompts import PROMPT_SERIAL_INSPIRED_STORY, PROMPT_CROSSWORD_EXTRACTION

# Load environment variables
load_dotenv()

st.set_page_config(layout="wide", page_title="Story & Crossword Lab")

# --- LOAD STATS (For Facets) ---
@st.cache_data
def load_stats(path):
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}
    except Exception:
        return {}

global_stats = load_stats(config.STATS_PATH)

def get_keys(stats_dict, key_name):
    data = stats_dict.get(key_name, {})
    if isinstance(data, dict):
        return list(data.keys())
    return []

st.title("🧩 Story-Inspired Crossword Generator")
st.caption("Generate a Chandamama story, then turn it into a crossword puzzle.")

# --- SIDEBAR CONFIG ---
with st.sidebar:
    st.header("Settings")
    model_options = list(set([config.LLM_MODEL_ID] + config.AVAILABLE_MODELS))
    selected_model = st.selectbox("LLM Model", model_options, index=model_options.index(config.LLM_MODEL_ID) if config.LLM_MODEL_ID in model_options else 0)
    st.divider()
    # Removed Debugging Info JSON as requested

# --- SESSION STATE ---
if 'story_text' not in st.session_state:
    st.session_state.story_text = ""
if 'puzzle_layout' not in st.session_state:
    st.session_state.puzzle_layout = None
if 'puzzle_data' not in st.session_state:
    st.session_state.puzzle_data = None

# --- STEP 1: STORY GENERATION ---
st.header("1. Create the Story")

col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("Design Story")
    
    # Faceted Inputs (Matching Main App)
    prompt_input = st.text_area("Plot Idea", height=100, placeholder="e.g. A king who lost his crown in a magical lake...")
    
    genres = ["Folklore", "Fantasy", "Moral", "Animal Fable", "Mythology", "Humor", "History", "Adventure"]
    sel_genre = st.selectbox("Genre", genres, index=0)
    
    all_keywords = get_keys(global_stats, "top_keywords")
    sel_keywords = st.multiselect("Keywords", all_keywords[:100], placeholder="Select keywords...")
    keywords_str = ", ".join(sel_keywords) if sel_keywords else "None"
    
    all_chars = get_keys(global_stats, "top_characters")
    sel_chars = st.multiselect("Characters", all_chars[:100], placeholder="Select characters...")
    
    all_locs = get_keys(global_stats, "top_locations")
    sel_locs = st.multiselect("Locations", all_locs[:100], placeholder="Select locations...")
    
    if st.button("✨ Generate Story", type="primary", use_container_width=True):
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
                    model_id=selected_model,
                    prompt=prompt,
                    system_prompt="You are a Telugu storyteller.",
                    max_tokens=2500,
                    temperature=0.7,
                    stream=True
                )
                
                # Use st.write_stream to display text in real-time
                # We need to capture it in col2 ideally? 
                # st.write_stream writes to current container. 
                # Let's write to session state first? No, write_stream returns final text.
                
                # To stream into col2, we can't easily do it if button is in col1.
                # Actually we can use `with col2:` context.
                with col2:
                     st.subheader("📖 Generated Story")
                     response_text = st.write_stream(stream)
                
                st.session_state.story_text = response_text
                # Clear old puzzle
                st.session_state.puzzle_layout = None
                st.session_state.puzzle_data = None
                st.rerun()
                
            except Exception as e:
                st.error(f"Error: {e}")

# If not generating, show existing story
if st.session_state.story_text and not st.session_state.get('generating_story'): # pseudo-check
    with col2:
         st.subheader("📖 Generated Story")
         st.markdown(st.session_state.story_text)


# --- STEP 2: CROSSWORD GENERATION ---
if st.session_state.story_text:
    st.divider()
    st.header("2. Generate Crossword")
    
    if st.button("🧩 Create Crossword from Story", type="primary"):
        with st.spinner("Analyzing story and building grid..."):
            try:
                # 1. Extract Words & Clues via LLM
                extract_prompt = PROMPT_CROSSWORD_EXTRACTION.format(
                    story_text=st.session_state.story_text
                )
                
                stream = generate_response_multi(
                    model_id=selected_model,
                    prompt=extract_prompt,
                    system_prompt="You are a puzzle generator. Output JSON only.",
                    max_tokens=4000, # Increased for large stories
                    temperature=0.2, 
                    stream=True
                )
                
                llm_output = ""
                for chunk in stream:
                    llm_output += chunk
                
                # Parse JSON
                cleaned_output = llm_output.strip()
                if not cleaned_output:
                     st.error("The AI returned an empty response. The story might be too long for the context window, or the model failed.")
                     st.stop()
                     
                if "```json" in cleaned_output:
                    cleaned_output = cleaned_output.split("```json")[1].split("```")[0]
                elif "```" in cleaned_output:
                     cleaned_output = cleaned_output.split("```")[1].split("```")[0]
                
                # Attempt to fix truncated JSON if needed (simple check)
                cleaned_output = cleaned_output.strip()
                if not cleaned_output.endswith("]"):
                     # Try to finding the last closing bracket
                     last_bracket = cleaned_output.rfind("]")
                     if last_bracket != -1:
                         cleaned_output = cleaned_output[:last_bracket+1]
                
                import re
                try:
                    words_data = json.loads(cleaned_output)
                except json.JSONDecodeError:
                    # Fallback to Regex extraction
                    # Look for pattern: "answer": "WORD", "clue": "Desc"
                    # We use a robust regex that handles potential whitespace
                    pattern = r'"answer"\s*:\s*"([^"]+)"\s*,\s*"clue"\s*:\s*"([^"]+)"'
                    matches = re.findall(pattern, cleaned_output)
                    
                    if matches:
                        words_data = [{"answer": m[0], "clue": m[1]} for m in matches]
                        st.warning(f"Note: The AI output was slightly malformed, but we recovered {len(words_data)} words.")
                    else:
                        st.error("The AI generated an invalid (or truncated) puzzle format. Please try again.")
                        st.write(f"Received {len(cleaned_output)} characters.")
                        with st.expander("Show Raw Debug Output"):
                            st.text(cleaned_output) # Use st.text to avoid rendering issues
                        st.stop()
                
                # 2. Generate Layout via Python Algorithm
                generator = CrosswordGenerator()
                # Run with 100 attempts for better density
                layout = generator.generate_layout(words_data, attempts=100)
                
                if layout:
                    st.session_state.puzzle_layout = layout
                    st.session_state.puzzle_data = words_data
                    
                    placed = layout.get('placed_count', len(layout['words']))
                    total = layout.get('total_count', len(words_data))
                    
                    st.success(f"Generated puzzle with {placed}/{total} words placed!")
                    if placed < total:
                        st.warning(f"Note: {total - placed} words could not be connected and were omitted.")
                    st.rerun()
                else:
                    st.error("Could not generate a valid grid from these words. Try again.")
                    
            except Exception as e:
                st.error(f"Error generating puzzle: {e}")

    # --- DISPLAY PUZZLE ---
    if st.session_state.puzzle_layout:
        layout = st.session_state.puzzle_layout
        
        st.subheader("Crossword Grid")
        
        grid_w = layout['width']
        grid_h = layout['height']
        
        # CSS for White/Transparent Grid
        # .cw-grid: No background (transparent)
        # .cw-cell: Transparent 
        # .cw-cell-filled: White background, Border
        
        st.markdown(f"""
        <style>
            .cw-grid {{
                display: grid;
                grid-template-columns: repeat({grid_w}, 34px);
                gap: 0px; 
                margin-top: 20px;
                margin-bottom: 20px;
                /* No background color for grid container */
            }}
            .cw-cell {{
                width: 34px;
                height: 34px;
                /* Transparent by default (Empty cells) */
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
        
        # Render
        grid_html = '<div class="cw-grid">'
        
        cell_map = {}
        for w in layout['words']:
            start_x = w['start_x']
            start_y = w['start_y']
            direction = w['direction']
            # answer is now a LIST of aksharas
            answer = w['answer'] 
            number = w['number']
            
            # Label start cell with number
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
                    # char is an Akshara (string)
                    grid_html += f'<div class="cw-cell cw-cell-filled">{num_html}{cell_data["char"]}</div>'
                else:
                    # Star emoji for empty cells (as requested)
                    # Low opacity to not destract
                    grid_html += '<div class="cw-cell" style="opacity:0.2; font-size: 12px;">⭐</div>'
                    
        grid_html += '</div>'
        st.markdown(grid_html, unsafe_allow_html=True)
        
        # Clues
        st.subheader("Clues")
        c1, c2 = st.columns(2)
        
        across_clues = sorted([w for w in layout['words'] if w['direction'] == 'across'], key=lambda x: x['number'])
        down_clues = sorted([w for w in layout['words'] if w['direction'] == 'down'], key=lambda x: x['number'])
        
        with c1:
            st.markdown("**Across**")
            for w in across_clues:
                # w['answer'] is list, join it for debugging length if needed, but clues usually show length in chars?
                # Actually length in boxes (aksharas) is what matters for user.
                length = len(w['answer'])
                st.markdown(f"**{w['number']}.** {w['clue']} ({length})")
                
        with c2:
            st.markdown("**Down**")
            for w in down_clues:
                length = len(w['answer'])
                st.markdown(f"**{w['number']}.** {w['clue']} ({length})")

        # --- REVIEW ANSWERS SECTION ---
        st.markdown("---")
        with st.expander("👁️ Show Answers / Review Key"):
            st.caption("If you are stuck, review the answers below.")
            
            # Create a nice layout for answers
            # We can use a dataframe or just columns
            all_words = sorted(layout['words'], key=lambda x: x['number'])
            
            data = []
            for w in all_words:
                data.append({
                    "Number": w['number'],
                    "Direction": w['direction'].title(),
                    "Clue": w['clue'],
                    "Answer": "".join(w['answer']) # Join list back to string
                })
            
            df = pd.DataFrame(data)
            st.table(df)
