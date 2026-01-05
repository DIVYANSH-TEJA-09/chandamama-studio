import os
import sys
from dotenv import load_dotenv

# Load env variables
load_dotenv()

def verify():
    print("--- Verifying AI Setup ---")
    
    # Check HF Token
    token = os.getenv("HF_TOKEN")
    print(f"HF_TOKEN present: {bool(token)}")
    
    if not token:
        print("ERROR: HF_TOKEN is missing in .env file.")
        print("Please add: HF_TOKEN=hf_xxxx...")
        return

    print("Trying to initialize HF Client...")
    try:
        from src.local_llm import get_client
        client = get_client()
        print("Client initialized successfully.")
        
        print("Testing connectivity with Qwen-72B...", flush=True)
        try:
            resp = client.text_generation("Hello", max_new_tokens=5)
            print(f"Connectivity Verified. Response: {resp}")
        except Exception as e:
            print(f"API CALL FAILED: {repr(e)}")
            print(f"Error Type: {type(e)}")
            if hasattr(e, 'response'):
                print(f"Response Headers: {e.response.headers}")
                print(f"Response Content: {e.response.content}")
            raise e
        
    except ImportError:
        print("ERROR: Could not import src.local_llm. Make sure you are in the project root.")
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    # Ensure src is in path
    sys.path.append(os.path.abspath("src"))
    verify()
