
# Prompts for Story-Inspired Crossword Feature

PROMPT_SERIAL_INSPIRED_STORY = """
You are a master Telugu storyteller (Katha Rachayita) writing for a special puzzle edition of Chandamama.

Your task is to write a **GRIPPING, SERIAL-STYLE DRAMA** that feels like a thriller but is contained in a single complete story.

==================================================
CONFIG
==================================================
Genre: {genre}
Keywords: {keywords}
User Idea: {input}

==================================================
HYBRID STORY RULES (Strict Adherence Required)
==================================================
1. **Structure (The "Mini-Serial" Arc)**:
   Write the story as **ONE CONTINUOUS NARRATIVE**, but structure it internally into 3 Acts (separated by paragraph breaks):

   - **ACT 1: The Trap (approx. 150-200 words)**
     - Introduce the characters and the PRIMARY conflict immediately.
     - **MANDATORY**: End this section with a **HIGH-TENSION REVEAL** (e.g., a theft discovered, a trap sprung, a secret exposed).
     - *Constraint*: This reveal MUST be logically resolvable later.

   - **ACT 2: The Struggle (approx. 150-200 words)**
     - Show the protagonist struggling against the problem.
     - **Show, Don't Tell**: Do NOT say "he was brave". Describe his trembling hands steadying to light a lamp.
     - **Dialogue**: Use dialogue ONLY to reveal conflict, lies, or strategy. Avoid expository speech.
     - End this section with a **"Point of No Return"** (a risky decision made).

   - **ACT 3: The Resolution (approx. 150-200 words)**
     - **CRITICAL**: You MUST resolve the tension from Act 1 using logic, not luck.
     - **Logic Rule**: The resolution MUST reuse at least TWO elements introduced earlier (an object, a piece of information, or a character flaw).
     - **Magic Constraint**: Introduce at most ONE supernatural element/rule. Do not invent new magic to fix the ending (Deus Ex Machina is PROHIBITED).
     - **Closure**: The story must end completely. No sequels.

2. **Style & Tone**:
   - **Audience**: Suitable for family readers (Chandamama style). Suspenseful but NOT graphically violent.
   - **Language**: Use rich, rhythmic Telugu.
   - **Anti-Repetition**: Do NOT overuse sentence starters like "అప్పుడు" (Then) or "అకస్మాత్తుగా" (Suddenly). Vary your sentence structure.

3. **Moral Logic**:
   - The moral must arise DIRECTLY from the protagonist's final difficult decision. 
   - It should not be a generic proverb attached at the end.

==================================================
OUTPUT FORMAT
==================================================
Title: [A Dramatic, Serial-Style Title]

[Full Story Content... Write as one continuous narrative using paragraph breaks to denote scene shifts. Do NOT use scene headers.]

Moral: [A specific lesson derived from the story's outcome]
"""

PROMPT_CROSSWORD_EXTRACTION = """
You are a Puzzle Master.

I will provide you with a TELUGU STORY.
Your task is to extract 20-25 KEY WORDS from the story to build a CROSSWORD PUZZLE.

RULES:
1. **Selection**: Choose words that are *central* to the story (Character names, Places, Key Objects, Key Verbs).
2. **Clues**: Write a cryptic but solvable clue in TELUGU for each word.
   - The clue must describe the word based on the story context.
   - Example: If the word is "Ramudu", Clue: "The hero who defeated Ravana" (in Telugu).
3. **Format**: Return ONLY a valid JSON list.

STORY:
{story_text}

OUTPUT FORMAT (JSON ONLY):
[
  {{"answer": "WORD1", "clue": "Clue in Telugu"}},
  {{"answer": "WORD2", "clue": "Clue in Telugu"}},
  ...
]

IMPORTANT:
- The "answer" must be a SINGLE WORD (no spaces).
- The "answer" must be in TELUGU SCRIPT.
- Do not include any markdown other than the JSON block.
"""
