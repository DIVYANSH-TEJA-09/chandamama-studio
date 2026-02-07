import os
import time

from typing import Dict, Any


# GENRE-SPECIFIC ADDITIONS (conditionally added based on genre)
GENRE_ADDITIONS = {
    "moral_story": """
==================================================
MORAL STORY GUIDELINES
==================================================
- Build toward a clear life lesson
- Let moral emerge from character actions
- State moral explicitly at end in ONE sentence
- Avoid preaching within the story
- Traditional folktale rhythm and pacing
""",
    
    "children_story": """
==================================================
CHILDREN'S STORY GUIDELINES
==================================================
- Simple vocabulary, rich imagery
- Clear good/bad distinction (if applicable)
- Age-appropriate themes and content
- Engaging rhythm that holds attention
- Optional: Include playful elements
""",
    
    "romance": """
==================================================
ROMANCE GUIDELINES
==================================================
- Focus on emotional connection and chemistry
- Build tension through obstacles/misunderstandings
- Show relationship development naturally
- Age-appropriate intimacy level
- Satisfying emotional payoff
""",
    
    "mystery": """
==================================================
MYSTERY GUIDELINES
==================================================
- Plant clues fairly for reader
- Build suspense through pacing
- Red herrings should be logical
- Solution must be earned, not random
- Reveal should satisfy setup
""",
    
    "comedy": """
==================================================
COMEDY GUIDELINES
==================================================
- Humor through character, situation, or wordplay
- Build comic timing through pacing
- Exaggeration should feel natural to story
- Avoid offensive stereotypes
- Land the punchlines/comic moments
""",
    
    "thriller": """
==================================================
THRILLER GUIDELINES
==================================================
- Maintain tension throughout
- Stakes must be clear and escalating
- Quick pacing with strategic slower moments
- Twist/surprises must be logical in hindsight
- Strong sense of danger/urgency
"""
}

# TONE-SPECIFIC ADDITIONS
TONE_ADDITIONS = {
    "traditional": "Use classic Telugu storytelling rhythm. Prefer timeless themes and archetypal characters.",
    "modern": "Contemporary language and settings. Modern social dynamics and realistic dialogue.",
    "mythological": "Maintain reverence for traditional stories. Epic scale and timeless themes.",
    "realistic": "Grounded in everyday life. Authentic character psychology and plausible events.",
    "fantastical": "Establish clear rules for magical elements. Internal consistency in fantasy logic."
}

# KEYWORD INTEGRATION LOGIC (SHARED)
KEYWORD_INTEGRATION_LOGIC = """
==================================================
KEYWORD INTEGRATION (CRITICAL WARNING)
==================================================
**DO NOT MECHANICALLY INCLUDE ALL KEYWORDS.**

Your task is to create a COHERENT story, not a checklist.

**IF YOU HAVE MULTIPLE KEYWORDS/CHARACTERS/SETTINGS:**

OPTION 1: Choose the 2-3 that fit together naturally
- Ignore keywords that don't serve the story
- It's better to skip a keyword than force it

OPTION 2: Find ONE unifying concept that connects them
- Ask: "What single story could naturally include these?"
- If you can't find one, go back to Option 1

**EXAMPLE - BAD APPROACH:**
Keywords: మోసం, సాహసం, శాపం
Characters: రాజు, మంత్రి, రైతు
Result: Throws all into one story → overstuffed, incoherent

**EXAMPLE - GOOD APPROACH:**
Keywords: మోసం, సాహసం, శాపం
Choose: సాహసం + శాపం (adventure + curse work together)
Skip: మోసం (doesn't fit naturally)
Or: మోసం causes శాపం, requires సాహసం to fix (connected)

**CHARACTERS:**
- If given 3+ characters, ask: "Does each have a CLEAR role?"
- If a character has no purpose, DON'T include them
- Better to have 2 well-developed characters than 4 doing nothing

**SETTINGS:**
- Don't visit all locations just because they're listed
- Only include settings that serve the plot
- Each location should have a PURPOSE in the story

**THE GOLDEN RULE:**
Story coherence > keyword inclusion
A simple story using 60% of keywords well
is MUCH BETTER than
a confused story forcing 100% of keywords badly
"""

# ANTI-REPETITION & HALLUCINATION RULES (SHARED)
ANTI_REPETITION_RULES = """
==================================================
STRICT WRITING RULES (ANTI-REPETITION)
==================================================
1. **NO REPETITIVE TAGS:** 
   - STRICTLY AVOID repetitive dialogue tags like "అని అన్నది" (she said), "అని చెప్పాడు" (he said), "అని అడిగాడు" (he asked).
   - Use action beats instead. 
     *Bad:* "వస్తావా?" అని అన్నాడు రాము. 
     *Good:* రాము తల తిప్పి చూశాడు. "వస్తావా?"

2. **SENTENCE VARIETY:**
   - Do NOT start every sentence with a subject or name.
   - Vary sentence length. Mix short, punchy sentences with longer, flowing descriptions.

3. **NO ENGLISH WORDS:**
   - STRICT PROHIBITION: Do NOT use any English words. Use pure Telugu vocabulary.
   - Example: Instead of "Time ayindi", use "సమయం అయ్యింది".

4. **NO HALLUCINATIONS:**
   - Do not invent non-existent cultural details unless it's fantasy.
   - Keep character actions logically consistent.
"""


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

    # Determine derived variables (Shared logic)
    genre_key = genre.lower().replace(" ", "_")
    
    # Add Tone if present in facets
    tone = facets.get("tone", "traditional")
    tone_instruction = TONE_ADDITIONS.get(tone.lower(), "")
    
    # Add Genre specific guidelines
    genre_guidelines = GENRE_ADDITIONS.get(genre_key, "")
    
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

{KEYWORD_INTEGRATION_LOGIC}

{genre_guidelines}

**TONE:** {tone_instruction}

{ANTI_REPETITION_RULES}

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
        # SINGLE STORY PROMPT
        
        # Calculate derived variables
        word_count = "400-600" # Default
        
        # Determine format based on genre
        ending_format = ""
        
        if "moral" in genre_key or "children" in genre_key or "folklore" in genre_key:
             ending_format = "Moral:\n<One clear sentence>"

        # CORE SYSTEM PROMPT (always included)
        prompt = f"""
You are an expert Telugu storyteller who writes engaging, well-crafted stories.

==================================================
ARCHIVE CONTEXT (STYLE REFERENCE)
==================================================
Learn narrative rhythm, vocabulary, and flow from these examples.
DO NOT copy plots or characters.

{context_text}

==================================================
STORY REQUEST
==================================================
Genre: {genre}
Themes/Keywords: {keywords_str}
Characters: {chars_str}
Setting: {locations_str}
Additional Instructions: {custom_instruction if custom_instruction else "Create an engaging story."}

Use these as creative inspiration—integrate naturally, don't force.

{genre_guidelines}

**TONE:** {tone_instruction}

==================================================
UNIVERSAL QUALITY STANDARDS
==================================================

**CHARACTER DEVELOPMENT:**
- Give each character distinct personality (2-3 traits)
- Show personality through actions, speech, reactions
- Motivations must be clear and consistent
- Keep cast manageable (3-5 main characters)

**PLOT LOGIC:**
- Every event must have clear cause-effect
- Character choices should make sense from their perspective
- No convenient coincidences solving problems
- Physical actions must be visualizable
- Test: "Can I explain this to someone clearly?"

**NATURAL DIALOGUE:**
- Minimize dialogue tags (aim for 20-30% of lines)
- Use action beats and context to show speakers
- Let characters speak distinctly based on personality
- Mix dialogue with narrative flow

**SHOW, DON'T TELL:**
- Reveal emotions through physical reactions, not statements
- Let actions demonstrate character traits
- Use sensory details to create immersion

**WRITING QUALITY:**
- Vary sentence structure and length
- No phrase repetition (max 2 uses)
- Natural Telugu flow, not translated English
- Appropriate vocabulary for target audience
- Consistent verb tenses

**STRUCTURE:**
- Clear beginning (setup + hook)
- Rising tension (conflict/challenge)
- Climax (decision/turning point)
- Resolution (earned consequences)
- Satisfying conclusion

{KEYWORD_INTEGRATION_LOGIC}

{ANTI_REPETITION_RULES}

==================================================
SELF-REVISION CHECKLIST
==================================================
Before finalizing:
□ Plot logic is sound and visualizable?
□ Each character has distinct personality?
□ Less than 30% dialogue has tags?
□ Emotions shown through action, not stated?
□ No repeated phrases or patterns?
□ Story flows naturally when read aloud?
□ Genre and tone appropriate throughout?

==================================================
OUTPUT FORMAT
==================================================
Title:
<Appropriate to genre and tone>

Story:
<Full Telugu story, {word_count} words>

{ending_format}

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
            time.sleep(0.005) # Slightly faster streaming
            
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
