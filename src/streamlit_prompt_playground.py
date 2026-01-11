import streamlit as st
import sys
import os
import time
import json
import heapq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Ensure src can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src import config
from src.local_llm_multi import generate_response_multi
from src import search_utils
from src import rag
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer

# --- CONFIG & PROMPTS (BACKEND) ---

PROMPT_CONTROL = """You are a classic Chandamama Telugu storyteller.

Your task is to write an ORIGINAL Telugu children’s story that strictly follows
the STYLE, RHYTHM, and MORAL STRUCTURE of traditional Chandamama tales.

==================================================
ARCHIVE CONTEXT (STYLE LEARNING ONLY)
==================================================
The following Telugu stories are provided ONLY to learn:
- sentence rhythm
- vocabulary style
- narrative flow
- moral reasoning

DO NOT copy characters, plots, events, or sentences.
DO NOT retell, adapt, or reference these stories.

{context}

==================================================
STYLE BANK (MANDATORY LINGUISTIC ANCHORS)
==================================================
Use the following Chandamama-style Telugu phrase patterns
to guide your language, rhythm, and tone.

Use them NATURALLY.
Do NOT copy them verbatim.
Do NOT overuse any single phrase.
if you find anyy better ones in the archive use them over the style bank.
OPENING PATTERNS: 
- ఒకప్పుడు ఒక చిన్న గ్రామంలో…
- చాలా కాలం క్రితం…
- అడవుల మధ్యలో ఉన్న ఒక ఊరిలో…
- ఒక రాజ్యంలో…

TRANSITION PHRASES:
- అప్పుడే అతనికి అర్థమైంది…
- కొంతకాలం తరువాత…
- అదే సమయంలో…
- చివరికి…

DIALOGUE MARKERS:
- అని అతను చెప్పాడు
- ఆమె ఆశ్చర్యంగా అడిగింది
- అతను నవ్వుతూ అన్నాడు
- వారు ఆలోచిస్తూ చెప్పారు

MORAL ENDINGS:
- ఈ కథ మనకు నేర్పేది…
- అందుకే మనం ఎప్పుడూ…
- మంచి మనసు ఉన్నవారికి మంచి జరుగుతుంది
- నిజాయితీకి ఎప్పుడూ ఫలితం ఉంటుంది

==================================================
CRITICAL STYLE RULES
==================================================
- Learn ONLY the writing STYLE from the archive.
- The story must be COMPLETELY NEW.
- Gods must remain gods; humans must remain humans.
- Follow traditional Indian moral logic.
- Maintain internal consistency within your story.
- Do NOT mention the archive or inspiration source.

==================================================
STORY INTENT (GUIDANCE ONLY)
==================================================
Genre: {genre}
Themes / Keywords: {keywords}
Characters (optional): {characters}
Setting / Location (optional): {locations}

These are for inspiration only.
They must NOT appear mechanically in the title or story.

User Hint:
{input}

==================================================
TITLE INSTRUCTION (VERY IMPORTANT)
==================================================
- The title must feel like a REAL Chandamama story title.
- Keep it short, natural, and expressive.
- It must NOT be a summary.
- It must NOT combine keywords mechanically.
- It should hint at the story emotionally, not descriptively.

==================================================
WRITING REQUIREMENTS
==================================================
- Write ONLY in Telugu.
- Use simple, child-friendly Telugu.
- Maintain a calm, classic tone.
- Clear beginning, middle, and end.
- Approximate length: 300–500 words.
- Do NOT rush the moral.

==================================================
MORAL RULE (STRICT)
==================================================
- The moral must be CLEAR and EXPLICIT.
- The moral must appear ONLY at the very end.
- Do NOT repeat the moral earlier in the story.

==================================================
INTERNAL PLANNING (DO NOT SHOW)
==================================================
Before writing, internally plan:
1. Setup
2. Conflict
3. Resolution
4. Moral

Do NOT show this plan in the output.

==================================================
OUTPUT FORMAT (STRICT)
==================================================
Title:
<Short Chandamama-style title>

Story:
<Full Telugu story>

Moral:
<One clear moral sentence>

Label:
ఈ కథ కొత్తగా రూపొందించబడింది (Inspired by Archive)."""

PROMPT_31 = """You are a classic Chandamama Telugu storyteller.

Your task is to write a COMPLETELY NEW Telugu children’s story in Chandamama style.

Before writing the story, internally plan (do NOT show):
Who the main character is
What they want
What goes wrong (conflict)
How the conflict is resolved
What moral the child should learn

Use the archive context ONLY to learn:
sentence rhythm
vocabulary
narrative flow
moral reasoning

Do NOT copy plots, characters, or events from the archive.

ARCHIVE CONTEXT (STYLE ONLY):
{context}

Story Guidance:
Genre: {genre}
Themes / Keywords: {keywords}
Characters: {characters}
Setting: {locations}

User Hint:
{input}

Writing Rules:
Simple, child-friendly Telugu
Calm, classic Chandamama tone
Clear beginning, middle, and end
Approx 300–500 words

Title Rule:
Must feel like a real Chandamama title
Must NOT combine keywords mechanically

Output Format (STRICT):
Title:
<Story Title>

Story:
<Full Telugu story>

Moral:
<One clear moral sentence>

Label:
ఈ కథ కొత్తగా రూపొందించబడింది (Inspired by Archive)."""

PROMPT_32 = """You are a Telugu storyteller writing in traditional Chandamama style.

This is a NEW, ORIGINAL story.

STRICT CONSTRAINTS:
ALL listed characters must appear meaningfully
ALL keywords must influence the plot
The setting must affect events (not decorative)

ARCHIVE CONTEXT (STYLE LEARNING ONLY):
{context}

Story Inputs:
Genre: {genre}
Keywords: {keywords}
Characters: {characters}
Setting: {locations}

User Hint:
{input}

Language & Style:
Simple Telugu for children
Classic rhythm
Natural dialogues

Title Rule:
Emotional hint, not a summary

Output Format:
Title:
Story:
Moral:
Label:
ఈ కథ కొత్తగా రూపొందించబడింది (Inspired by Archive)."""

PROMPT_33 = """You are a storyteller for Chandamama magazine.

The following stories are given ONLY to understand:
how stories begin
how conflicts unfold
how morals are delivered

Do NOT reuse characters, plots, or events.

ARCHIVE CONTEXT (STYLE ONLY):
{context}

Now write a NEW Telugu story with the SAME FEEL but a DIFFERENT story.

Story Parameters:
Genre: {genre}
Themes: {keywords}
Characters: {characters}
Setting: {locations}

Rules:
Child-friendly Telugu
Slow, graceful narration
Moral revealed only at the end

Output Format:
Title:
Story:
Moral:
Label:
ఈ కథ కొత్తగా రూపొందించబడింది (Inspired by Archive)."""

PROMPT_34 = """You are a disciplined Telugu storyteller.

INTERNAL STEP (DO NOT SHOW):
Plan the story as:
Setup
Conflict
Turning point
Resolution
Moral

Then write the story.

ARCHIVE CONTEXT (STYLE ONLY):
{context}

Story Guidance:
Genre: {genre}
Themes: {keywords}
Characters: {characters}
Setting: {locations}

Rules:
Gods remain gods, humans remain humans
Traditional Indian moral logic
No rushed moral

Output Format:
Title:
Story:
Moral:
Label:
ఈ కథ కొత్తగా రూపొందించబడింది (Inspired by Archive)."""

PROMPT_35 = """You are writing a NEW Telugu children’s story.

STYLE SOURCE (HOW TO WRITE):
Learn rhythm, vocabulary, and tone from:
{context}

CONTENT SOURCE (WHAT TO WRITE):
Genre: {genre}
Themes: {keywords}
Characters: {characters}
Setting: {locations}

IMPORTANT:
Style must NOT control the plot
Content must NOT copy archive events

Writing Rules:
Simple Telugu
Clear conflict
Emotional resolution
Moral only at the end

Output Format:
Title:
Story:
Moral:
Label:
ఈ కథ కొత్తగా రూపొందించబడింది (Inspired by Archive)."""

# List of variants
VARIANTS = [
    {"name": "00: CONTROL (Original)", "template": PROMPT_CONTROL},
    {"name": "31: Plot-First", "template": PROMPT_31},
    {"name": "32: Constraint-Locked", "template": PROMPT_32},
    {"name": "33: Pure Chandamama", "template": PROMPT_33},
    {"name": "34: Two-Pass Hidden", "template": PROMPT_34},
    {"name": "35: Hybrid", "template": PROMPT_35},
]

# --- APP LOGIC ---

# Cache resources
@st.cache_resource
def get_qdrant_client():
    return QdrantClient(path=config.QDRANT_PATH)

@st.cache_resource
def get_embedding_model():
    return SentenceTransformer(config.EMBEDDING_MODEL_NAME)

@st.cache_data
def get_stats_facets():
    """
    Loads global_stats.json and extracts Top 100 items for facets.
    """
    stats_path = config.STATS_PATH
    if not os.path.exists(stats_path):
        return [], [], []
    
    try:
        with open(stats_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Helper to get top 100 keys from a frequency dict
        def get_top_n(d, n=100):
            if not isinstance(d, dict): return []
            # Sort by frequency desc
            sorted_items = sorted(d.items(), key=lambda x: x[1], reverse=True)
            return [k for k, v in sorted_items[:n]]
            
        keywords = get_top_n(data.get("top_keywords", {}))
        characters = get_top_n(data.get("top_characters", {}))
        locations = get_top_n(data.get("top_locations", {}))
        
        return keywords, characters, locations
    except Exception as e:
        print(f"Error loading stats: {e}")
        return [], [], []

st.set_page_config(layout="wide", page_title="Prompt Playground")

st.title("🧪 Prompt Playground & Story Lab")
st.caption("A/B Testing Laboratory with Data-Driven Facets")

# Model Selection
model_options = list(set([config.LLM_MODEL_ID] + config.COUNCIL_MODELS))
selected_model = st.selectbox("Select Model", model_options, index=model_options.index(config.LLM_MODEL_ID) if config.LLM_MODEL_ID in model_options else 0)

# --- Faceted Inputs ---
st.header("1. Faceted Inputs")
st.caption("Select inputs based on Top 100 archive statistics.")

# Load facets
top_kw, top_char, top_loc = get_stats_facets()

col_facets_1, col_facets_2, col_facets_3 = st.columns(3)

with col_facets_1:
    genre = st.selectbox("Genre ({genre})", ["Folklore", "Mythology", "Adventure", "Moral Story", "Fantasy"], index=0)
    
with col_facets_2:
    # Use multiselect for Keywords but allow typing? 
    # Streamlit multiselect allows searching.
    # We combine user typed + top list? Streamlit multiselect is fixed options usually.
    # Let's just use top list for now.
    keywords_sel = st.multiselect("Keywords ({keywords})", top_kw, placeholder="Select keywords...")
    keywords_str = ", ".join(keywords_sel)
    
with col_facets_3:
    # For Char/Loc, maybe selectbox + text input for custom found in archive?
    # Let's use selectbox with "Custom" option? Or just multiselect.
    # Multiselect is safer.
    chars_sel = st.multiselect("Characters ({characters})", top_char)
    chars_str = ", ".join(chars_sel)
    
    locs_sel = st.multiselect("Locations ({locations})", top_loc)
    locs_str = ", ".join(locs_sel)

user_input = st.text_area("User Instruction / Hint ({input})", height=70, placeholder="e.g. Write a story about a brave mouse who saves the forest.")

# --- Retrieval Section ---
st.header("2. Context Retrieval (RAG)")

if 'context_text' not in st.session_state:
    st.session_state.context_text = ""

col_rag_1, col_rag_2 = st.columns([1, 3])

with col_rag_1:
    st.caption("Generate Context from Facets")
    if st.button("🔍 Fetch Context (Qdrant)"):
        try:
            client = get_qdrant_client()
            model = get_embedding_model()
            
            # Formulate query
            query_parts = [genre, keywords_str, user_input]
            query_text = f"query: {' '.join([p for p in query_parts if p])}"
            embedding = model.encode(query_text, normalize_embeddings=True)
            
            with st.spinner("Querying Qdrant..."):
                # USE query_points as requested
                results = client.query_points(
                    collection_name=config.COLLECTION_NAME,
                    query=embedding,
                    limit=20, # Fetch more to group
                    with_payload=True
                ).points
                
                # Group and Format
                grouped = search_utils.group_results_by_story(results, max_stories=3)
                hydrated = search_utils.hydrate_stories(client, config.COLLECTION_NAME, grouped)
                context_str = rag.build_rag_context(hydrated)
                
                st.session_state.context_text = context_str
                st.success(f"Fetched {len(hydrated)} stories.")
                
        except Exception as e:
            st.error(f"Retrieval Error: {e}")

with col_rag_2:
    context_input = st.text_area("Context Content ({context})", value=st.session_state.context_text, height=150)
    # Update session state if user manually edits
    st.session_state.context_text = context_input

# --- RUN SECTION ---
st.header("3. Execution (6-Way Parallel)")
st.caption("Prompts (00, 31-35) are configured in the backend.")

if st.button("🚀 Run All Prompts", type="primary"):
    # Prepare Variables
    kw_final = keywords_str if keywords_str else "None"
    ch_final = chars_str if chars_str else "Generic Characters"
    loc_final = locs_str if locs_str else "Generic Village"
    ctx_final = st.session_state.context_text
    inp_final = user_input if user_input else "Create a story."
    
    variables = {
        "genre": genre,
        "keywords": kw_final,
        "characters": ch_final,
        "locations": loc_final,
        "input": inp_final,
        "context": ctx_final
    }
    
    st.divider()
    
    # Layout: 2 Rows of 3 Cols
    res_r1 = st.columns(3)
    res_r2 = st.columns(3)
    all_res_cols = res_r1 + res_r2
    
    for i, variant in enumerate(VARIANTS):
        with all_res_cols[i]:
            st.info(f"Generating {variant['name']}...")
            
            final_user_prompt = variant["template"]
            
            try:
                # Robust replacement
                for k, v in variables.items():
                    key = "{" + k + "}"
                    if key in final_user_prompt:
                        final_user_prompt = final_user_prompt.replace(key, str(v))
                
                start_time = time.time()
                response = generate_response_multi(
                    model_id=selected_model,
                    prompt=final_user_prompt,
                    system_prompt="You are a creative storyteller.",
                    max_tokens=2500,
                    temperature=0.7
                )
                end_time = time.time()
                duration = end_time - start_time
                
                st.success(f"Time: {duration:.2f}s")
                st.text_area(f"Output ({variant['name']})", value=response, height=600, key=f"out_{i}")
                
            except Exception as e:
                st.error(f"Error: {e}")
