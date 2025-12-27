
import os
import sys

# Add src to path just in case
sys.path.append(os.path.join(os.getcwd(), 'src'))

try:
    from src.populate_qdrant import main
except ImportError as e:
    print(f"Error: Failed to import 'src/populate_qdrant.py'.")
    print(f"Details: {e}")
    print("Ensure you are in the root directory and all dependencies are installed.")
    sys.exit(1)

if __name__ == "__main__":
    print("========================================")
    print("   Starting Chandamama DB Rebuild       ")
    print("========================================")
    print("This script will re-index all chunks from 'd:/Viswam_Projects/chandamama-studio/chunks' into Qdrant.")
    print("This may take 10-20 minutes depending on CPU.")
    print("----------------------------------------")
    
    # Run the ingestion logic
    main()
    
    print("========================================")
    print("   DB Rebuild Complete!                 ")
    print("========================================")
    print("You can now run 'streamlit run app.py' with full RAG support.")
