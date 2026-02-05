import os
import sys
from dotenv import load_dotenv

# Load env vars from .env immediately
load_dotenv()

# Add src to path just in case
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from src.scripts.populate_qdrant import main
except ImportError as e:
    print(f"Error: Failed to import 'src/populate_qdrant.py'.")
    print(f"Details: {e}")
    print("Ensure you are in the root directory and all dependencies are installed.")
    sys.exit(1)

if __name__ == "__main__":
    print("========================================")
    print("   Starting Chandamama DB Rebuild       ")
    print("========================================")
    print(f"This script will re-index all chunks from '{os.path.join(os.getcwd(), 'data/chunks')}' into Qdrant.")
    print("This may take 10-20 minutes depending on CPU.")
    print("----------------------------------------")
    
    # Run the ingestion logic (Chunks)
    main()
    
    print("========================================")
    print("   Chunk Indexing Complete!             ")
    print("========================================")

    # Ask user if they want to build Story Embeddings (Mechanism 5)
    print("\n[Optional] Do you want to build 'Full Story Embeddings' (Mechanism 5)?")
    print("This is required for 'The Council' and 'Story Search' features.")
    print("Note: This uses the 'Alibaba-NLP/gte-multilingual-base' model.")
    
    response = input("Build Story Embeddings? (y/n): ").strip().lower()
    
    if response == 'y':
        print("\nStarting Story Embedding Pipeline...")
        print("----------------------------------------")
        try:
            from src.story_embedder.main import main as story_main
            story_main()
            print("========================================")
            print("   Story Embedding Complete!            ")
            print("========================================")
        except ImportError as e:
            print(f"Error importing story embedder: {e}")
        except Exception as e:
            print(f"Error running story embedder: {e}")
    else:
        print("Skipping Story Embeddings.")

    print("\n========================================")
    print("   All Done!                            ")
    print("========================================")
    print("You can now run 'streamlit run app.py' with full RAG support.")
