import argparse
import sys
import os

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src.council_of_storytellers.evaluator import run_council_evaluation

def main():
    parser = argparse.ArgumentParser(description="Run the Council of Storytellers Evaluation")
    
    parser.add_argument("--prompt", type=str, required=False, help="Custom plot prompt")
    parser.add_argument("--genre", type=str, default="Folklore", help="Genre of the story")
    parser.add_argument("--keywords", type=str, nargs="+", default=["Magic", "Parrot"], help="List of keywords")
    
    args = parser.parse_args()
    
    facets = {
        "genre": args.genre,
        "keywords": args.keywords,
        "characters": ["Generic Characters"],
        "locations": ["Generic Village"],
        "prompt_input": args.prompt if args.prompt else "A poor farmer finds a parrot that speaks only the truth."
    }
    
    run_council_evaluation(facets)

if __name__ == "__main__":
    main()
