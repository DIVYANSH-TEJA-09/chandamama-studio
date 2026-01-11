
import os
import sys
import textwrap

# Ensure we can import from src
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from retrieval_logics_test.contextual_retrieval import ContextualRetriever
from retrieval_logics_test.full_story_retrieval import FullStoryRetriever
from story_gen import generate_story

def print_split_screen(title1, text1, title2, text2, width=120):
    """
    Prints two texts side-by-side.
    """
    col_width = (width - 5) // 2
    
    wrapper1 = textwrap.TextWrapper(width=col_width)
    wrapper2 = textwrap.TextWrapper(width=col_width)
    
    lines1 = text1.splitlines()
    lines2 = text2.splitlines()
    
    # Wrap all lines
    wrapped_lines1 = []
    for line in lines1:
        wrapped_lines1.extend(wrapper1.wrap(line) if line.strip() else [""])
        
    wrapped_lines2 = []
    for line in lines2:
        wrapped_lines2.extend(wrapper2.wrap(line) if line.strip() else [""])
    
    max_lines = max(len(wrapped_lines1), len(wrapped_lines2))
    
    print("-" * width)
    print(f"{title1:<{col_width}} | {title2:<{col_width}}")
    print("-" * width)
    
    for i in range(max_lines):
        l1 = wrapped_lines1[i] if i < len(wrapped_lines1) else ""
        l2 = wrapped_lines2[i] if i < len(wrapped_lines2) else ""
        print(f"{l1:<{col_width}} | {l2:<{col_width}}")
        
    print("-" * width)

def main():
    print("Initializing Retrieval Strategies...")
    try:
        retriever1 = ContextualRetriever(top_k=3)
        retriever2 = FullStoryRetriever(top_k=3) # Limit stories to top 3, hydration gets full text
    except Exception as e:
        print(f"Initialization Error: {e}")
        return

    print("\n--- Retrieval Logic Comparator ---")
    
    while True:
        query = input("\nEnter prompt/query (or 'exit'): ").strip()
        if query.lower() in ['exit', 'quit']:
            break
        if not query:
            continue
            
        print(f"\nProcessing: '{query}'...\n")
        
        # 1. Fetch Contexts
        print("Fetching Context 1 (Contextual Chunks)...")
        context1 = retriever1.retrieve(query)
        
        print("Fetching Context 2 (Full Story)...")
        context2 = retriever2.retrieve(query)
        
        # 2. Generate Stories
        facets = {
            "prompt_input": query,
            "genre": "Folklore", # Default
            # We can ask user for more but let's keep it simple for testing
        }
        
        print("Generating Story 1...")
        story1 = generate_story(facets, context_text=context1)
        
        print("Generating Story 2...")
        story2 = generate_story(facets, context_text=context2)
        
        # 3. Display
        print("\n\n" + "="*50 + " RESULTS " + "="*50 + "\n")
        
        # Print Metadata (Context Length)
        print(f"Strategy 1 Context Length: {len(context1)} chars")
        print(f"Strategy 2 Context Length: {len(context2)} chars")
        print("\n")
        
        print_split_screen("STRATEGY 1: Contextual Chunks", story1, "STRATEGY 2: Full Story", story2)

if __name__ == "__main__":
    main()
