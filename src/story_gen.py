import os
import time

from typing import Dict, Any

def generate_story(facets: Dict[str, Any], context_text: str = "", llm_params: Dict[str, Any] = None) -> str:
    """
    Generates a NEW, ORIGINAL Telugu story based on user facets and RAG context.
    """
    
    # Extract facets with defaults
    genre = facets.get("genre", "Folklore")
    keywords = facets.get("keywords", [])
    chars = facets.get("characters", [])
    locations = facets.get("locations", [])
    
    # New facets
    content_type = facets.get("content_type", "SINGLE")
    num_chapters = facets.get("num_chapters", 1)

    # Format lists for prompt
    keywords_str = ", ".join(keywords) if keywords else "None"
    chars_str = ", ".join(chars) if chars else "Generic Characters"
    locations_str = ", ".join(locations) if locations else "Generic Village"

    # User's custom prompt
    custom_instruction = facets.get("prompt_input", "").strip()
    
    if content_type == "SERIAL":
        prompt = f"""
You are a master Telugu storyteller (Katha Rachayita) specializing in SERIAL STORIES (ధారావాహికలు).

Your task is to write a MULTI-CHAPTER SERIAL STORY in Telugu based on the user's request.

==================================================
CONFIG
==================================================
Genre: {genre}
Number of Chapters to Generate: {num_chapters}
Keywords: {keywords_str}
Characters: {chars_str}
Locations: {locations_str}
User Plot Idea: {custom_instruction if custom_instruction else "Create a gripping serial story."}

==================================================
SERIAL STORY RULES (STRICT)
==================================================
1. You MUST generate EXACTLY {num_chapters} chapters in this single response.
2. Label each chapter clearly as:
   ## అధ్యాయం 1: [Chapter Title]
   [Story Content...]
   
   ## అధ్యాయం 2: [Chapter Title]
   [Story Content...]
   
   (and so on...)

3. CONTINUITY: 
   - The story MUST be continuous. Chapter 2 must start exactly where Chapter 1 ended.
   - Do NOT restart the story in each chapter.
   - if too many characters are given introduce them slowly over the chapters but maintain logic over the stories.
   - squeeze the full dramatic potential of its premise.
   - No Rushed execution. 
   - All chapters need not have same token count. count may vary based on the story.
   -Each chapter must justify the existence of the next chapter.
   - Maintain consistent characters and setting throughout.
   -Each chapter must increase at least one of these: stakes, risk, moral cost, emotional pressure
   -If a chapter only: travels, explains, reveals without resistance then it must introduce a new problem by the end.
   -Concrete enforcement: Any test / puzzle / challenge must: fail once OR cost something (time, safety, trust, emotion)
   -❌ No instant success
   -❌ No back-to-back victories
   -Every major action must leave a residue.
   -Show the value through action, not explanation.
   -Enforce: Characters act according to values, Narrator does not explain the lesson directly
   -❌ Avoid:“ఈ కథ మనకు నేర్పింది…” or “అలా ధర్మం గెలిచింది…”

4. CLIFFHANGERS & CONCLUSION (CRITICALLY IMPORTANT):
   - Chapters 1 to {num_chapters - 1}: MUST end with a SUSPENSE HOOK or CLIFFHANGER. The reader must feel "What happens next?"
   - FINAL CHAPTER (Chapter {num_chapters}): MUST RESOLVE everything.
     - PROHIBITED: Do NOT end the last chapter with a cliffhanger.
     - REQUIRED: Tie up all loose ends. Solve the mystery. complete the character arcs.
     - It must feel like a satisfying CONCLUSION to the serial.

5. STYLE:
   - Use classical/magazine style Telugu (Chandamama style).
   - Descriptive, engaging, and emotional.
   - Avoid English words.

6. Before finalizing each chapter, ask internally:

“What is still unresolved?”

“Why must the reader continue?”

“What did this chapter cost the characters?”

==================================================
ARCHIVE CONTEXT (STYLE SOURCES)
==================================================
Use these only for style inspiration:
{context_text}

==================================================
OUTPUT FORMAT
==================================================
Title: [Serial Title - Big and Catchy]

## అధ్యాయం 1: [Title]
[Content...]

## అధ్యాయం 2: [Title]
[Content...]

...

(Moral is optional for serials, but if applicable, add at the very end).

Label:
ఈ ధారావాహిక కథ కొత్తగా రూపొందించబడింది (AI Generated Serial).
"""
    else:
        # SINGLE STORY PROMPT (Legacy)
        prompt = f"""
You are a classic Telugu storyteller.

Your task is to write an ORIGINAL Telugu children’s story that strictly follows
the STYLE, RHYTHM, and MORAL STRUCTURE of traditional Telugu folktales.

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
Use the following Classic Telugu phrase patterns
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
{custom_instruction if custom_instruction else "Create a meaningful classic-style story using the above guidance."}

==================================================
TITLE INSTRUCTION (VERY IMPORTANT)
==================================================
- The title must feel like a REAL Classic Folktale title.
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
<Short Classic Folktale-style title>

Story:
<Full Telugu story>

Moral:
<One clear moral sentence>

Label:
ఈ కథ కొత్తగా రూపొందించబడింది (Inspired by Archive).
"""

    
    # Call isolated LLM function with streaming
    try:
        stream = _call_llm_creative(prompt, llm_params)
        
        full_text = ""
        for chunk in stream:
            full_text += chunk
            yield chunk
            time.sleep(0.02) # Slower streaming speed
            
        # Append Mandatory Label
        if content_type == "SERIAL":
             if "AI Generated Serial" not in full_text:
                  label = "\n\n(ఈ ధారావాహిక కథ కొత్తగా రూపొందించబడింది - AI Generated Serial)"
                  yield label
        else:
            label = "\n\n(ఈ కథ కొత్తగా రూపొందించబడింది - AI Generated)"
            yield label

    except Exception as e:
        yield f"Error generating story: {str(e)}"


def _call_llm_creative(prompt: str, params: Dict[str, Any] = None):
    """
    Calls Multi-LLM backend (OpenAI, Groq, HF) with streaming.
    """
    try:
        from src.local_llm_multi import generate_response_multi, config
        
        # Default Params
        if not params:
            params = {}
            
        model_id = params.get("model", config.AVAILABLE_MODELS[0])
        temp = params.get("temperature", 0.7)
        max_tok = params.get("max_tokens", 3500)

        return generate_response_multi(
            model_id=model_id, 
            prompt=prompt, 
            system_prompt="You are a creative storyteller.", 
            temperature=temp, 
            max_tokens=max_tok,
            stream=True
        )
    except Exception as e:
        return f"LLM Error: {str(e)}"

def generate_poem(facets: Dict[str, Any], llm_params: Dict[str, Any] = None) -> str:
    """
    Generates a Telugu POEM/SONG based on facets.
    """
    theme = facets.get("theme", "Nature")
    keywords = facets.get("keywords", [])
    style = facets.get("style", "Metric Poem (Padyam)")
    
    keywords_str = ", ".join(keywords) if keywords else "None"
    
    prompt = f"""
You are a playful Telugu Poet (Kavi) writing for a children's magazine.

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
        # Pass params correctly
        stream = _call_llm_creative(prompt, llm_params)
        for chunk in stream:
            yield chunk
            time.sleep(0.02) # Slower streaming speed
    except Exception as e:
        yield f"Error generating poem: {str(e)}"
