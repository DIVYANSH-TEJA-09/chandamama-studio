import os
import sys
import time
from datetime import datetime

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from src import config
from src.local_llm_multi import generate_response_multi
from src.retrieval_logics_test.story_embeddings_retrieval import StoryEmbeddingsRetriever
from src.story_gen import generate_story # We will mock the internal call or reuse logic

def run_council_evaluation(facets):
    """
    Runs the Council of Storytellers evaluation.
    """
    
    print("\n--- 🏰 Convening the Council of Storytellers 🏰 ---")
    print(f"Goal: '{facets.get('prompt_input', 'Unknown')}'")
    
    # 1. Retrieve Context (Once for all)
    print("\n1. Retrieving Full Story Context (Mechanism 5)...")
    retriever = StoryEmbeddingsRetriever(top_k=2) # 2 Full stories as context
    
    search_query = f"{facets.get('prompt_input', '')} {facets.get('genre', '')} {' '.join(facets.get('keywords', []))} {' '.join(facets.get('characters', []))}"
    context_text = retriever.retrieve(search_query)
    
    print(f"   Context Retrieved ({len(context_text)} chars).")
    
    # 2. Iterate Models
    results_dir = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(results_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    for model_id in config.COUNCIL_MODELS:
        print(f"\n2. Summoning {model_id}...")
        start_time = time.time()
        
        # We need to use generate_story BUT force it to use our specific model.
        # Since generate_story calls _call_llm_creative which calls local_llm.generate_response...
        # We will reimplement the prompt construction here to leverage local_llm_multi directly.
        # This avoids hacking story_gen.py
        
        prompt = _construct_prompt(facets, context_text)
        
        try:
            story_output = generate_response_multi(
                model_id=model_id,
                prompt=prompt,
                system_prompt="You are a creative storyteller.",
                max_tokens=3500,
                temperature=0.7
            )
            elapsed = time.time() - start_time
            print(f"   ✨ Story Generated in {elapsed:.1f}s")
            
            # Save Result
            safe_model_name = model_id.replace("/", "_").replace("-", "_")
            filename = f"{timestamp}_{safe_model_name}.md"
            filepath = os.path.join(results_dir, filename)
            
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(f"# Council Evaluation: {model_id}\n\n")
                f.write(f"**Date:** {timestamp}\n")
                f.write(f"**Model:** `{model_id}`\n")
                f.write(f"**Time Taken:** {elapsed:.2f}s\n")
                f.write(f"**Prompt:** {facets.get('prompt_input')}\n\n")
                f.write("---\n\n")
                f.write(story_output)
                f.write("\n\n---\n")
                f.write("### Context Used\n")
                f.write(context_text)
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

def _construct_prompt(facets, context_text):
    """
    Reconstructs the story_gen prompt. 
    Duplicate logic from story_gen.py to ensure identical prompting.
    """
    genre = facets.get("genre", "Folklore")
    keywords = facets.get("keywords", [])
    chars = facets.get("characters", [])
    locations = facets.get("locations", [])
    custom_instruction = facets.get("prompt_input", "").strip()
    
    keywords_str = ", ".join(keywords) if keywords else "None"
    chars_str = ", ".join(chars) if chars else "Generic Characters"
    locations_str = ", ".join(locations) if locations else "Generic Village"

    return f"""
You are a classic Chandamama Telugu storyteller.

Your task is to write an ORIGINAL Telugu children’s story that strictly follows
the STYLE, RHYTHM, and MORAL STRUCTURE of traditional Chandamama tales.

==================================================
ARCHIVE CONTEXT (STYLE LEARNING ONLY)
==================================================
The following Telugu stories are provided ONLY to learn:
- sentence rhythm
- vocabulary style
- narrative flow
- moral reasoning

DO NOT copy characters, plots, events, or sentences.
DO NOT retell, adapt, or reference these stories.

{context_text}

==================================================
STYLE BANK (MANDATORY LINGUISTIC ANCHORS)
==================================================
Use the following Chandamama-style Telugu phrase patterns
to guide your language, rhythm, and tone.

Use them NATURALLY.
Do NOT copy them verbatim.
Do NOT overuse any single phrase.
if you find anyy better ones in the archive use them over the style bank.
OPENING PATTERNS: 
- ఒకప్పుడు ఒక చిన్న గ్రామంలో…
- చాలా కాలం క్రితం…
- అడవుల మధ్యలో ఉన్న ఒక ఊరిలో…
- ఒక రాజ్యంలో…

TRANSITION PHRASES:
- అప్పుడే అతనికి అర్థమైంది…
- కొంతకాలం తరువాత…
- అదే సమయంలో…
- చివరికి…

DIALOGUE MARKERS:
- అని అతను చెప్పాడు
- ఆమె ఆశ్చర్యంగా అడిగింది
- అతను నవ్వుతూ అన్నాడు
- వారు ఆలోచిస్తూ చెప్పారు

MORAL ENDINGS:
- ఈ కథ మనకు నేర్పేది…
- అందుకే మనం ఎప్పుడూ…
- మంచి మనసు ఉన్నవారికి మంచి జరుగుతుంది
- నిజాయితీకి ఎప్పుడూ ఫలితం ఉంటుంది

==================================================
CRITICAL STYLE RULES
==================================================
- Learn ONLY the writing STYLE from the archive.
- The story must be COMPLETELY NEW.
- Gods must remain gods; humans must remain humans.
- Follow traditional Indian moral logic.
- Maintain internal consistency within your story.
- Do NOT mention the archive or inspiration source.

==================================================
STORY INTENT (GUIDANCE ONLY)
==================================================
Genre: {genre}
Themes / Keywords: {keywords_str}
Characters (optional): {chars_str}
Setting / Location (optional): {locations_str}

These are for inspiration only.
They must NOT appear mechanically in the title or story.

User Hint:
{custom_instruction}

==================================================
TITLE INSTRUCTION (VERY IMPORTANT)
==================================================
- The title must feel like a REAL Chandamama story title.
- Keep it short, natural, and expressive.
- It must NOT be a summary.
- It must NOT combine keywords mechanically.
- It should hint at the story emotionally, not descriptively.

==================================================
WRITING REQUIREMENTS
==================================================
- Write ONLY in Telugu.
- Use simple, child-friendly Telugu.
- Maintain a calm, classic tone.
- Clear beginning, middle, and end.
- Approximate length: 300–500 words.
- Do NOT rush the moral.

==================================================
MORAL RULE (STRICT)
==================================================
- The moral must be CLEAR and EXPLICIT.
- The moral must appear ONLY at the very end.
- Do NOT repeat the moral earlier in the story.

==================================================
INTERNAL PLANNING (DO NOT SHOW)
==================================================
Before writing, internally plan:
1. Setup
2. Conflict
3. Resolution
4. Moral

Do NOT show this plan in the output.

==================================================
OUTPUT FORMAT (STRICT)
==================================================
Title:
<Short Chandamama-style title>

Story:
<Full Telugu story>

Moral:
<One clear moral sentence>

Label:
ఈ కథ కొత్తగా రూపొందించబడింది (Inspired by Archive).
"""

if __name__ == "__main__":
    # Default Test Case
    test_facets = {
        "genre": "Folklore",
        "keywords": ["Magic", "Parrot", "Honesty"],
        "characters": ["Poor Farmer", "King"],
        "locations": ["Ancient Village"],
        "prompt_input": "A poor farmer finds a parrot that speaks only the truth, but it gets him into trouble with the King."
    }
    run_council_evaluation(test_facets)
