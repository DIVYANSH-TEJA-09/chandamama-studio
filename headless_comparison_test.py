
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# mimic the path setup from streamlit_comparison.py
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path) # project root
src_dir = os.path.join(current_dir, 'src')

if src_dir not in sys.path:
    sys.path.append(src_dir)
if current_dir not in sys.path:
    sys.path.append(current_dir)

from src.retrieval_logics_test.contextual_retrieval import ContextualRetriever
from src.story_gen import generate_story

def test():
    print("Initializing Retriever...")
    retriever = ContextualRetriever(top_k=1)
    
    query = "Magic Parrot"
    print(f"Retrieving context for: {query}")
    context = retriever.retrieve(query)
    print(f"Context length: {len(context)}")
    
    facets = {
        "genre": "Folklore",
        "keywords": ["magic"],
        "prompt_input": query
    }
    
    print("Generating story via API...")
    story = generate_story(facets, context_text=context)
    
    if "HF API Error" in story:
        print("FAILED: API Error detected in output.")
        print(story)
        sys.exit(1)
    else:
        print("SUCCESS: Story generated.")
        print("-" * 50)
        print(story[:200] + "...")
        print("-" * 50)

if __name__ == "__main__":
    test()
