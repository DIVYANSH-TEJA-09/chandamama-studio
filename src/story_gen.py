import os
import openai
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
You are a creative Telugu storyteller inspired by the STYLE of classic Chandamama tales.

ARCHIVE CONTEXT (For Style & Tone Inspiration):
{context_text}
--------------------------------------------------

IMPORTANT:
- The story must be COMPLETELY NEW and ORIGINAL.
- Do NOT retell the stories in the context above.
- Use the context ONLY to understand the vocabulary, sentence structure, and moral reasoning of Chandamama.
- Gods must remain gods; humans must remain humans.
- Use traditional Indian moral-logic.
-Do not introduce characters, events, or relationships that contradict the provided archive context
- Title must be creative and not just putting keywords together.
Goal:
Write a NEW Telugu story inspired by the context and parameters.

Story Parameters:
- Genre: {genre}
- Keywords / Themes: {keywords_str}
- Characters (optional): {chars_str}
- Setting / Location (optional): {locations_str}

User Instructions:
{custom_instruction if custom_instruction else "Create an engaging story using the parameters above."}

Writing Requirements:
- Clear beginning, middle, and end
- Simple, classic Telugu (child-friendly)
- Calm moral tone
- Approx length: 300–500 words

Moral Rule:
- The moral must be CLEAR, EXPLICIT, and appear ONLY at the end.

Output Format (STRICT):
Title: <Story Title>

<Story Content>

Moral: <One clear moral sentence>

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
    Calls OpenAI API for creative storytelling.
    Requires OPENAI_API_KEY environment variable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "ERROR: OPENAI_API_KEY not found in environment. Please check .env file."

    try:
        openai.api_key = api_key
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a creative storyteller."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=2000
        )
        
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            return "No text returned from LLM."
            
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
