import os
import sys
from dotenv import load_dotenv

# Load env vars from .env immediately
load_dotenv()

# Add src to path just in case
sys.path.append(os.path.join(os.getcwd(), 'src'))

if __name__ == "__main__":
    print("Using 75% CPU Multiprocessing for fast ingestion.")
    print("----------------------------------------")
    
    # [STRICT MODE] Run ONLY Story Embeddings (Mechanism 5)
    # We completely bypass the legacy 'populate_qdrant' (Chunking) 
    # and go straight to the high-context story embeddings.
    
    try:
        from src.story_embedder.main import main as story_main
        story_main()
        
        print("\n========================================")
        print("   ✅ Full Story Database Rebuilt")
        print("========================================")
        print("Ready for 'The Council' and 'Contextual Search'.")
        
    except ImportError as e:
        print(f"Error importing story embedder: {e}")
    except Exception as e:
        print(f"Error running story embedder: {e}")

