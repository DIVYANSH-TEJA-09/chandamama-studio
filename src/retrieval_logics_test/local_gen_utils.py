import os
import openai
from typing import Dict, Any

# Import the original generate_story to verify we can wrap it or duplicate needed logic
# We need to replicate _call_llm_creative or import it
from story_gen import _call_llm_creative

def generate_hybrid_story(facets: Dict[str, Any], style_context: str, content_context: str) -> str:
    """
    Generates a story using the 2-Channel Hybrid approach.
    """
    
    genre = facets.get("genre", "Folklore")
    keywords = facets.get("keywords", [])
    chars = facets.get("characters", [])
    locations = facets.get("locations", [])
    prompt_input = facets.get("prompt_input", "")

    keywords_str = ", ".join(keywords) if keywords else "None"
    chars_str = ", ".join(chars) if chars else "Generic Characters"
    locs_str = ", ".join(locations) if locations else "Generic Village"

    prompt = f"""
You are an expert Telugu Author for Chandamama, famous for your specific narrative voice.

### CRITICAL INSTRUCTION:
You have two distinct inputs:
1. **STYLE TEMPLATE (Channel A)**: A full story. **IGNORE the plot, characters, and events of this story entirely.** Use it DIFFERENTLY: Adopt its *tone*, *vocabulary*, *sentence structure*, *pacing*, and *narrative voice*.
2. **PLOT SOURCE (Channel B)**: A set of fragmented facts/excerpts. **This is your ACTUAL STORY CONTENT.** You must stitch these facts together into a cohesive narrative.

### INPUTS:

[CHANNEL A: STYLE TEMPLATE]
(Use the WRITING STYLE from here like how the author would write and take the story from start to end maintaing the sense of the genre and they way the author would add the elements evetually to it and shape the story to a gold standard chandamama story, but IGNORE the story events the style is only meant to guide you to take inspiration from but not to exactly copy it on to the output story)
\"\"\"
{style_context}
\"\"\"

[CHANNEL B: PLOT SOURCE]
(Use the CHARACTERS, SETTING, and PLOT EVENTS from here and take inspiration from the {style_context} but never copy paste it as we mentioned above.)
\"\"\"
{content_context}
\"\"\"

### STORY PARAMETERS:
- Genre: {genre}
- Keywords: {keywords_str}
- Characters: {chars_str}
- Locations: {locs_str}
- User Layout: {prompt_input}

### WRITING TASK:
Write a NEW Telugu story that integrates the **PLOT details from Channel B** using the **NARRATIVE VOICE from Channel A**.
- **NEGATIVE CONSTRAINT**: Do NOT use characters or events from Channel A. (e.g. If Channel A has a "Lion", and Channel B has a "Rabbit", do NOT put the Lion in the story unless Channel B also has it).
- Ensure a proper beginning, middle, and climax.
- Ensure the story is a gold standard chandamama story.
- make sure that the characters are given enough time to grow and develop and the story has the essence of the genre.
- The story must not be too bland and donot jump direclty to the climax rather character development is very important.
- animals must be animals and people must be people, god must be gods and thing must be things do not mess with their roles and also address them accordingly, do not address animals as people or gods or things and do not address gods casually also maintain the roles of the characters and do not mix them up.
- End with a traditional Chandamama moral.

### OUTPUT FORMAT:
Title: <Methodical Title>

<Story Body in Telugu>

Moral: <Moral Sentence>

Label:
ఈ కథ హైబ్రిడ్ పద్ధతిలో రూపొందించబడింది (Hybrid Generation).
"""
    try:
        return _call_llm_creative(prompt)
    except Exception as e:
        return f"Error generating hybrid story: {str(e)}"
