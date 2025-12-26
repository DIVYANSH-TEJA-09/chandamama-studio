import os
import sys
from dotenv import load_dotenv

# Load env vars
load_dotenv()

# Check key
api_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY present: {bool(api_key)}")
if api_key == "placeholder_please_replace":
    print("WARNING: OPENAI_API_KEY is still the placeholder!")

# Add src to path
sys.path.append("d:/Viswam_Projects/chandamama-studio/src")

try:
    from story_gen import generate_story
    from rag import answer_question
    print("Imports successful.")
except ImportError as e:
    print(f"ImportError: {e}")
    sys.exit(1)

print("-" * 20)
print("Testing Story Gen (Mock call if key invalid)...")
# We don't want to actually crash if key is invalid, just check structure
# But if user put key, this verifies it works.
if api_key and api_key != "placeholder_please_replace":
    try:
        story = generate_story({"genre": "Test", "moral": "Test"})
        print("Story Gen Result:")
        print(story[:100] + "...")
    except Exception as e:
        print(f"Story Gen Error: {e}")
else:
    print("Skipping actual API call due to missing/placeholder key.")

print("-" * 20)
print("Testing RAG Answer (Mock call if key invalid)...")
if api_key and api_key != "placeholder_please_replace":
    try:
        ans = answer_question("Test question", "Context: Test context")
        print("RAG Answer Result:")
        print(ans)
    except Exception as e:
        print(f"RAG Answer Error: {e}")
else:
    print("Skipping actual API call due to missing/placeholder key.")
