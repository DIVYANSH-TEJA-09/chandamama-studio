import streamlit as st
import sys
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add src to path
sys.path.append(os.path.abspath("src"))

# Import Modules
from src.retrieval_logics_test.story_embeddings_retrieval import StoryEmbeddingsRetriever
from src import config
from src.graph_utils import build_story_centric_graph
from streamlit_agraph import agraph, Node, Edge, Config

# Page Config
st.set_page_config(
    page_title="Chandamama Knowledge Graph",
    page_icon="🕸️",
    layout="wide"
)

# --- Initialization ---
@st.cache_resource
def load_retriever():
    # Helper to get the client, top_k doesn't matter much for scroll
    return StoryEmbeddingsRetriever(top_k=2)

try:
    retriever = load_retriever()
except Exception as e:
    st.error(f"Failed to load AI resources/Qdrant: {e}")
    st.stop()

# --- Main UI ---
st.title("🕸️ Chandamama Knowledge Graph")
st.caption("Explore the archive through semantic connections. Search for a story to see its universe.")

# Initialize Session State
if "selected_story_id" not in st.session_state:
    st.session_state["selected_story_id"] = None

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

def get_keys(stats_dict, key_name):
    data = stats_dict.get(key_name, {})
    if isinstance(data, dict):
        return list(data.keys())
    return []

col_ctrl, col_graph = st.columns([1, 3], gap="large")

with col_ctrl:
    st.markdown("### 1. Find a Story")
    st.caption("Filter the archive using metadata facets.")
    
    # Facets
    genres = ["Folklore", "Fantasy", "Moral", "Animal Fable", "Mythology", "Humor", "History", "Adventure"]
    sel_genre = st.selectbox("Genre", ["All"] + genres)
    
    all_keywords = get_keys(global_stats, "top_keywords")
    sel_keywords = st.multiselect("Keywords", all_keywords[:100])
    
    all_chars = get_keys(global_stats, "top_characters")
    sel_chars = st.multiselect("Characters", all_chars[:100])
    
    custom_search = st.text_input("Extra Terms", placeholder="e.g. Magic, King...")

    # Build Query
    query_parts = []
    if custom_search: query_parts.append(custom_search)
    if sel_genre != "All": query_parts.append(sel_genre)
    if sel_keywords: query_parts.extend(sel_keywords)
    if sel_chars: query_parts.extend(sel_chars)
    
    search_query = " ".join(query_parts)
    
    if st.button("🔍 Search Archive", use_container_width=True):
        if not search_query.strip():
            st.warning("Please select at least one filter or type a keyword.")
        else:
            # Search for candidates using the retriever
            candidates = retriever.retrieve_points(search_query)[:5] # Top 5 suggestions
            
            st.markdown("### 2. Select Focal Point")
            candidate_map = {f"{p.payload.get('title', 'Unknown')} ({p.payload.get('year', '??')})": p.id for p in candidates}
            
            if candidate_map:
                # Store candidate map in session state to persist selection options
                st.session_state["candidate_map"] = candidate_map
            else:
                st.warning("No stories found. Try a different combination.")
                
    # Selection UI (Persistent)
    if "candidate_map" in st.session_state:
        candidate_map = st.session_state["candidate_map"]
        selected_label = st.radio("Choose a story to focus on:", list(candidate_map.keys()))
        
        if st.button("🚀 Generate Graph", type="primary", use_container_width=True):
            st.session_state["selected_story_id"] = candidate_map[selected_label]
    
    st.markdown("### 3. Settings")
    show_shared = st.checkbox("Show Shared Entities", value=True, help="Connect similar stories to characters/themes.")
    sim_threshold = st.slider("Similarity Threshold", 0.7, 0.95, 0.80, 0.01)

with col_graph:
    sid = st.session_state.get("selected_story_id")
    
    if sid:
        with st.spinner("Weaving Knowledge Graph..."):
            try:
                # 1. Fetch Focal Story (with Vector)
                # We need the vector to find similar stories
                focal_points, _ = retriever.client.scroll(
                    collection_name=config.STORY_COLLECTION_NAME,
                    scroll_filter=None, # Filter by ID technically safer but limit=1 works if we assume unique IDs processing
                    limit=1,
                    with_payload=True,
                    with_vectors=True
                )
                
                # Fetch exact by ID 
                focal_point = retriever.client.retrieve(
                    collection_name=config.STORY_COLLECTION_NAME,
                    ids=[sid],
                    with_payload=True,
                    with_vectors=True
                )[0]
                
                focal_payload = focal_point.payload
                focal_payload["story_id"] = sid
                focal_vector = focal_point.vector
                
                # 2. Find Similar Stories (Semantic Search)
                similar_points = retriever.client.query_points(
                    collection_name=config.STORY_COLLECTION_NAME,
                    query=focal_vector,
                    limit=6, # Top 5 similar + 1 self (deduplicate later)
                    with_payload=True,
                    score_threshold=sim_threshold
                ).points
                
                similar_stories = []
                for p in similar_points:
                    if p.id == sid:
                        continue # Skip self
                    s_pl = p.payload
                    s_pl["story_id"] = p.id
                    s_pl["score"] = p.score
                    similar_stories.append(s_pl)
                
                # 3. Build Graph
                from src.graph_utils import build_story_centric_graph
                nodes, edges, config_agraph = build_story_centric_graph(
                    focal_story=focal_payload,
                    similar_stories=similar_stories,
                    config_options={"show_shared_entities": show_shared}
                )
                
                # 4. Render
                st.success(f"Visualizing Universe of: **{focal_payload.get('title')}**")
                return_value = agraph(nodes=nodes, edges=edges, config=config_agraph)
                
                # Legend
                st.caption("🔵 Story | 🟢 Character | 🟠 Theme | 🟣 Location")
                
                # --- Handle Interaction ---
                if return_value:
                    if return_value.startswith("CHAR_") or return_value.startswith("THEME_") or return_value.startswith("LOC_"):
                       try:
                           entity_type, entity_name = return_value.split("_", 1)
                           st.toast(f"Finding stories with {entity_type}: {entity_name}...", icon="🕵️")
                           st.info(f"Clicked Entity: **{entity_name}**. (Pivot logic requiring session refresh not fully implemented yet in this turn)")
                       except:
                           pass
                    elif return_value != sid:
                        # Similar Story Clicked
                         st.toast(f"Switching Focus...", icon="🔄")
                         st.session_state["selected_story_id"] = return_value
                         st.rerun()
                
            except Exception as e:
                st.error(f"Error generating graph: {e}")
                
    else:
        st.info("👈 Search and select a story to begin.")
        
        # Placeholder / Empty State Visual
        # Maybe show a static image or generic text
        st.markdown(
            """
            <div style="text-align: center; color: #666; padding: 50px;">
                <h3>🕸️ Your Archive Knowledge Graph</h3>
                <p>Search for a story on the left to see how it connects to the rest of the Chandamama universe.</p>
            </div>
            """, unsafe_allow_html=True
        )
