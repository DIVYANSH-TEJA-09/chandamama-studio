import os

from typing import Dict, Any

def generate_story(facets: Dict[str, Any], context_text: str = "") -> str:
    """
    Generates a NEW, ORIGINAL Telugu story based on user facets and RAG context.
    """
    
    # Extract facets with defaults
    genre = facets.get("genre", "Folklore")
    keywords = facets.get("keywords", [])
    chars = facets.get("characters", [])
    locations = facets.get("locations", [])
    
    # Format lists for prompt
    keywords_str = ", ".join(keywords) if keywords else "None"
    chars_str = ", ".join(chars) if chars else "Generic Characters"
    locations_str = ", ".join(locations) if locations else "Generic Village"

    # User's custom prompt
    custom_instruction = facets.get("prompt_input", "").strip()
    
    # Construct strictly formatted prompt
    prompt = f"""
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
{custom_instruction if custom_instruction else "Create a meaningful Chandamama-style story using the above guidance."}

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

    
    # Call isolated LLM function
    try:
        story_text = _call_llm_creative(prompt)
    except Exception as e:
        return f"Error generating story: {str(e)}"

    # Append Mandatory Label
    final_output = f"{story_text}\n\n(ఈ కథ కొత్తగా రూపొందించబడింది - AI Generated)"
    
    return final_output


def _call_llm_creative(prompt: str) -> str:
    """
    Calls Local Qwen-72B for creative storytelling.
    """
    try:
        from src.local_llm import generate_response
        return generate_response(prompt, system_prompt="You are a creative storyteller.", temperature=0.7, max_tokens=3500)
    except Exception as e:
        return f"LLM Error: {str(e)}"

def generate_poem(facets: Dict[str, Any]) -> str:
    """
    Generates a Telugu POEM/SONG based on facets.
    """
    theme = facets.get("theme", "Nature")
    keywords = facets.get("keywords", [])
    style = facets.get("style", "Metric Poem (Padyam)")
    
    keywords_str = ", ".join(keywords) if keywords else "None"
    
    prompt = f"""
You are a playful Telugu Poet (Kavi) writing for Chandamama children's magazine.

Goal: Write a {style} in Telugu.

Parameters:
- Theme: {theme}
- Keywords: {keywords_str}

Requirements:
- Simple, rhythmic Telugu.
- Child-friendly content.
- 4 to 8 lines (or 2 stanzas).
- If 'Padyam', try to follow a simple meter (like Aata Veladi or Teta Geeti style implies).
- If 'Paata' (Song), make it rhythmic and catchy.

Output Format:
Title: <Title>

<Poem Content>

(Meaning/Bhavam - Optional but good for children)
"""
    try:
        return _call_llm_creative(prompt)
    except Exception as e:
        return f"Error generating poem: {str(e)}"
