import random
from typing import List, Dict, Any, Tuple
from streamlit_agraph import Node, Edge, Config

def get_random_color():
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

GENRE_COLORS = {
    "Folklore": "#FF9999",
    "Fantasy": "#99CCFF",
    "Moral": "#99FF99",
    "Animal Fable": "#FFFF99",
    "Mythology": "#FFCC99",
    "Humor": "#FF99CC",
    "History": "#D3D3D3",
    "Adventure": "#FF6666",
    "Unknown": "#E0E0E0"
}


def build_story_centric_graph(
    focal_story: Dict[str, Any], 
    similar_stories: List[Dict[str, Any]], 
    config_options: Dict[str, Any] = None
) -> Tuple[List[Node], List[Edge], Config]:
    """
    Builds a professional, star-topology graph centered on one 'Focal Story'.
    
    Schema:
    - CENTER: Focal Story (Book Icon, Large)
    - RING 1: Metadata Entities (Characters, Themes, Locations) connected to Focal.
    - RING 2: Similar Stories connected to Focal (via Similarity Edge).
    - RING 3 (Optional): Shared Entities connecting Similar Stories to existing Entity Nodes.
    
    Styling:
    - Story: Blue, fa-book
    - Character: Green, fa-user
    - Theme: Orange, fa-lightbulb
    - Location: Purple, fa-map-marker
    """
    nodes = []
    edges = []
    
    # --- Configuration & Styles ---
    # Using FontAwesome 5.x codes if supported, or generic shapes
    # streaming-agraph supports 'image', 'circularImage', 'diamond', 'dot', 'star', 'triangle', 'triangleDown', 'square', 'icon'
    
    STYLE = {
        "focal": {"color": "#2E86C1", "size": 40, "icon": "book"},     # Strong Blue
        "story": {"color": "#5DADE2", "size": 25, "icon": "book-open"},# Lighter Blue
        "char":  {"color": "#27AE60", "size": 20, "icon": "user"},     # Green
        "theme": {"color": "#F39C12", "size": 20, "icon": "lightbulb"},# Orange
        "loc":   {"color": "#8E44AD", "size": 15, "icon": "map-marker"}# Purple
    }

    seen_ids = set()

    def add_node(nid, label, group, title=None):
        if nid in seen_ids:
            return
        seen_ids.add(nid)
        
        style = STYLE.get(group, STYLE["story"])
        
        # Tooltip
        tooltip = title if title else label
        
        # Create Node
        # Note: Icon support depends on the font loaded in the frontend. 
        # Standard shapes are safer if font not guaranteed, but let's try strict shapes + colors first for "Clean Professional" look.
        # We will use 'dot' with distinguishing colors to be safe and clean.
        
        nodes.append(Node(
            id=nid,
            label=label,
            title=tooltip,
            color=style["color"],
            size=style["size"],
            shape="dot", # Professional standard
            font={"size": 14, "face": "Roboto", "color": "#333333"},
            borderWidth=2,
            shadow=True
        ))

    # --- 1. Focal Story (Center) ---
    f_id = focal_story.get("story_id", "FOCAL")
    f_title = focal_story.get("title", "Selected Story")
    add_node(f_id, f_title, "focal", title=f"FOCAL STORY\nTitle: {f_title}\nAuthor: {focal_story.get('author','')}")
    
    # --- 2. Extract & Add Entities for Focal Story ---
    # Helper to process lists
    def process_entities(story_doc, source_id):
        # Characters (Normalize to Title Case for better merging)
        for char in story_doc.get("characters", [])[:5]: # Limit 5
            norm_char = char.strip().title()
            c_id = f"CHAR_{norm_char}"
            add_node(c_id, norm_char, "char", title=f"Character: {norm_char}")
            edges.append(Edge(source=source_id, target=c_id, color="#ABEBC6", width=2, label="has_char"))
            
        # Themes/Keywords
        for kw in story_doc.get("keywords", [])[:5]: # Limit 5
            norm_kw = kw.strip().title()
            k_id = f"THEME_{norm_kw}"
            add_node(k_id, norm_kw, "theme", title=f"Theme: {norm_kw}")
            edges.append(Edge(source=source_id, target=k_id, color="#F9E79F", width=2, label="has_theme"))
            
        # Locations
        for loc in story_doc.get("locations", [])[:3]: # Limit 3
            norm_loc = loc.strip().title()
            l_id = f"LOC_{norm_loc}"
            add_node(l_id, norm_loc, "loc", title=f"Location: {norm_loc}")
            edges.append(Edge(source=source_id, target=l_id, color="#D2B4DE", width=2, label="in"))

    process_entities(focal_story, f_id)
    
    # --- 3. Similar Stories ---
    for sim in similar_stories:
        s_id = sim.get("story_id")
        if not s_id or s_id == f_id:
            continue
            
        s_title = sim.get("title", "Untitled")
        score = sim.get("score", 0.0)
        
        add_node(s_id, s_title, "story", title=f"SIMILAR STORY\nTitle: {s_title}\nMatch: {score:.2f}")
        
        # Add Edge (Focal -> Similar)
        # Thickness/Length could vary by score
        edges.append(Edge(
            source=f_id, 
            target=s_id, 
            label=f"{score:.2f}", 
            color="#AED6F1", 
            dashes=True,
            width=3 if score > 0.85 else 1
        ))
        
        # Optional: Add shared entities? 
        # If we process entities for similar stories, they might auto-connect to existing entity nodes
        # This creates the "Graph" effect (triangulation)
        if config_options and config_options.get("show_shared_entities"):
             process_entities(sim, s_id)

    # --- 4. Configuration ---
    config = Config(
        width=1200,
        height=800,
        directed=False, 
        physics=True, 
        hierarchical=False,
        # Physics tuning/stabilization
        layout={"improvedLayout": True},
        physicsOptions={
            "barnesHut": {
                "gravitationalConstant": -3000,
                "centralGravity": 0.3,
                "springLength": 150,
                "springConstant": 0.05,
                "damping": 0.09,
                "avoidOverlap": 0.5
            },
            "stabilization": {"iterations": 100} # Pre-stabilize
        },
        # Enable dynamic scaling
        nodes={
            "scaling": {
                "label": {
                    "enabled": True,
                    "min": 14,
                    "max": 30
                }
            }
        },
        nodeHighlightBehavior=True,
        highlightColor="#F7A7A6",
        collapsible=False
    )
    
    return nodes, edges, config

