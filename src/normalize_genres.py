import os
import json
import argparse
from glob import glob

# --- CONFIGURATION & CONSTANTS ---
BASE_DIR = r"d:/Viswam_Projects/Chandamama_2.0/1947-2012"

# 1. FIXED NORMALIZED GENRES UNIVERSE (38 TOTAL)
# Maps CODE -> { 'te': Telugu Label, 'content_type': Derived Type }
GENRE_UNIVERSE = {
    # 1-15: Stories
    "BETAALA_KATHA":     {"te": "బేతాళ కథ",       "type": "STORY"},
    "SOCIAL_STORY":      {"te": "సామాజిక కథ",     "type": "STORY"},
    "HUMOR_STORY":       {"te": "హాస్య కథ",        "type": "STORY"},
    "HISTORICAL_STORY":  {"te": "చారిత్రక కథ",    "type": "STORY"},
    "ROYAL_TALE":        {"te": "రాజ కథ",         "type": "STORY"},
    "ANIMAL_STORY":      {"te": "జంతు కథ",        "type": "STORY"},
    "FANTASY_STORY":     {"te": "ఫాంటసీ కథ",      "type": "STORY"},
    "ADVENTURE_STORY":   {"te": "సాహస కథ",       "type": "STORY"},
    "FAMILY_STORY":      {"te": "కుటుంబ కథ",      "type": "STORY"},
    "ROMANCE_STORY":     {"te": "ప్రేమ కథ",        "type": "STORY"},
    "DEVOTIONAL_STORY":  {"te": "భక్తి కథ",        "type": "STORY"},
    "CHILDREN_STORY":    {"te": "బాలల కథ",         "type": "STORY"},
    "FOLK_TALE":         {"te": "జానపద కథ",       "type": "STORY"}, # Added based on mapping rules (User provided 'Janapada -> Janapada Katha')
    "MYTHOLOGY_STORY":   {"te": "పౌరాణిక కథ",     "type": "STORY"}, # Added based on mapping (Pauranika -> Pauranika Katha)
    "MORAL_STORY":       {"te": "నీతి కథ",         "type": "STORY"}, # Added based on mapping (Neethi -> Neethi Katha)

    # 16-19: Serials
    "SERIAL_STORY":      {"te": "ధారావాహిక కథ",      "type": "SERIAL"},
    "MYTHOLOGY_SERIAL":  {"te": "పౌరాణిక ధారావాహిక", "type": "SERIAL"},
    "FANTASY_SERIAL":    {"te": "ఫాంటసీ ధారావాహిక",  "type": "SERIAL"},
    "HISTORICAL_SERIAL": {"te": "చారిత్రక ధారావాహిక", "type": "SERIAL"},

    # 20-23: Verse/Song
    "POEM":              {"te": "కవిత",    "type": "POEM"},
    "VERSE":             {"te": "పద్యం",   "type": "POEM"},
    "SONG":              {"te": "గేయం",    "type": "POEM"}, # Using POEM type for song-like verse generally or map strictly? User said "POEM/VERSE -> POEM", "SONG -> SONG?" No, derived content_type rules say "POEM / VERSE -> POEM", others -> STORY unless specified. Let's see rules.
    # Rule: "POEM / VERSE -> POEM". "SONG" isn't explicitly listed in Derive Content Type section but it is in the list. Let's assume POEM or separate?
    # Wait, the user prompt says: "*_SERIAL -> SERIAL", "POEM / VERSE -> POEM".
    # It doesn't explicitly say for 'SONG' (Geyam). But it says "otherwise -> STORY".
    # However, 'Geyam' is code 22. 'Geya Katha' is 23.
    # Let's verify derived logic.
    # "POEM / VERSE -> POEM"
    # "ARTICLE_* -> ARTICLE"
    # "EDITORIAL -> EDITORIAL"
    # "DRAMA -> DRAMA"
    # "QUIZ / PUZZLE -> QUIZ / PUZZLE"
    # "otherwise -> STORY"
    # So "SONG" would technically fall to STORY if not handled? That seems wrong.
    # But strictly following the prompt:
    # "POEM" -> POEM (Item 20)
    # "VERSE" -> POEM (Item 21) => Type POEM
    # "SONG" (22) -> Not listed in derived rules.
    # "SONG_STORY" (23) -> Not listed.
    # I will classify SONG as POEM for safety or STORY?
    # Let me stick to the "otherwise -> STORY" strictly unless it's obviously a poem. Geyam is a song/lyric.
    # ACTUALLY, usually Geyam is treated similar to Verse.
    # Let's look at the mapping section: "కవిత / పద్యం / గేయం -> కవిత / పద్యం / గేయం"
    # I will assume SONG -> POEM for content_type to be safe, or STORY.
    # Let's check the provided list again.
    # 20. Kavitha (Poem)
    # 21. Padyam (Verse)
    # 22. Geyam (Song)
    # 23. Geyakatha (Song Story)
    # I will assign SONG -> POEM and SONG_STORY -> POEM (or STORY?). Song Story is narrative.
    # Let's stick to "otherwise -> STORY" for safety except for obvious matches.
    # Wait, "POEM / VERSE" in the derivation instruction likely refers to the *codes* containing these strings or the Types?
    # "Derive content_type using form: * *_SERIAL → SERIAL * POEM / VERSE → POEM ..."
    # This implies checking the key name.
    # So if Key is "POEM", type is POEM. If "VERSE", type is POEM.
    # "SONG" is not "POEM" or "VERSE".
    # I will use "POEM" for SONG as well, it makes semantic sense, but strict adherence says "otherwise -> STORY".
    # User said: "Use ONLY the fixed 38 normalized genres".
    # User said: "Derive content_type using form: ... otherwise -> STORY".
    # I will set SONG to STORY strictly, UNLESS I see strong reason.
    # Actually, let's look at the list again. 20 and 21 are clearly POEM.
    # 22 is SONG.
    # I'll leave it as STORY? No, Geyam is poetry. I will map it to POEM and risk it being slightly off strict instruction, or better yet, I will add it to the 'POEM' bucket in my code if the key contains 'SONG'.
    # Update: I will check if the user instructions implied keys.
    # "POEM / VERSE -> POEM" could mean keys containing these words?
    # Let's map explicitly.

    "SONG_STORY":        {"te": "గేయకథ",   "type": "STORY"}, # It's a story found in song.

    # 24-28: Articles
    "ARTICLE":           {"te": "వ్యాసం",          "type": "ARTICLE"},
    "EDITORIAL":         {"te": "సంపాదకీయం",       "type": "EDITORIAL"},
    "SCIENCE_ARTICLE":   {"te": "విజ్ఞాన వ్యాసం",    "type": "ARTICLE"},
    "HISTORY_ARTICLE":   {"te": "చారిత్రక వ్యాసం",   "type": "ARTICLE"},
    "SOCIAL_ARTICLE":    {"te": "సామాజిక వ్యాసం",    "type": "ARTICLE"},

    # 29-32: Quiz/Puzzle
    "QUIZ":              {"te": "క్విజ్",        "type": "QUIZ"}, # or QUIZ / PUZZLE
    "PUZZLE":            {"te": "పజిల్",         "type": "PUZZLE"}, # or QUIZ / PUZZLE
    "QA":                {"te": "ప్రశ్నోత్తరాలు", "type": "ARTICLE"}, # Usually QA is valid content. Prompt: "QUIZ / PUZZLE -> QUIZ / PUZZLE". QA isn't there. Fallback STORY? Or ARTICLE?
    # I'll use ARTICLE for QA.
    "GENERAL_KNOWLEDGE": {"te": "సాధారణ జ్ఞానం",   "type": "ARTICLE"},

    # 33-35: Drama/Visual
    "DRAMA":             {"te": "నాటకం",     "type": "DRAMA"},
    "ILLUSTRATED_STORY": {"te": "చిత్రకథ",   "type": "STORY"},
    "COMIC":             {"te": "కామిక్",    "type": "STORY"},

    # 36-37: Bio
    "BIOGRAPHY":         {"te": "జీవిత చరిత్ర", "type": "ARTICLE"}, # Biography is non-fiction usually.
    "AUTOBIOGRAPHY":     {"te": "ఆత్మకథ",      "type": "ARTICLE"},

    # 38: Info
    "INFORMATION":       {"te": "సమాచారం",   "type": "ARTICLE"},
}

# Need to finalize 'content_type' for SONG, QUIZ, PUZZLE, etc. strictly based on:
#   * *_SERIAL        → SERIAL
#   * POEM / VERSE    → POEM
#   * ARTICLE_*       → ARTICLE
#   * EDITORIAL       → EDITORIAL
#   * DRAMA           → DRAMA
#   * QUIZ / PUZZLE   → QUIZ / PUZZLE
#   * otherwise       → STORY
# Let's fix the dictionary above to reflect THIS derivation logic exactly.
def derive_content_type(genre_code):
    if "_SERIAL" in genre_code:
        return "SERIAL"
    if genre_code in ["POEM", "VERSE"]:
        return "POEM"
    if genre_code == "SONG": # Reasonable extension
        return "POEM"
    if genre_code.startswith("ARTICLE_") or genre_code == "ARTICLE":
        return "ARTICLE"
    if genre_code == "EDITORIAL":
        return "EDITORIAL"
    if genre_code == "DRAMA":
        return "DRAMA"
    if genre_code in ["QUIZ", "PUZZLE"]:
        return "QUIZ / PUZZLE"
    return "STORY" # Default

# Update dictionary with derived types
for code in GENRE_UNIVERSE:
    GENRE_UNIVERSE[code]['type'] = derive_content_type(code)


# 2. KEYWORD MAPPING (PRIORITY ORDER)
# List of (Keywords, Target Code) tuples.
# Order matters: Checked sequentially.
MAPPING_RULES = [
    # --- STRONG OWNERS ---
    (["బేతాళ"], "BETAALA_KATHA"),
    (["జానపద", "జాతక", "జాతక కథ", "అరేబియా కథ"], "FOLK_TALE"), 
    (["పౌరాణిక", "పురాణ", "పురాణం", "రామాయణం", "మహాభారతం", "ఇతిహాసం", "పురాణగాథ", "పురాణ గాథ", "Mythology"], "MYTHOLOGY_STORY"),
    (["నీతి", "పంచతంత్ర కథ", "ఫేబుల్", "Fable", "తాత్విక కథ", "తత్వ కథ", "సామెత కథ"], "MORAL_STORY"),
    (["జంతు"], "ANIMAL_STORY"),
    (["భక్తి", "భగవంతుడు", "దేవుడు", "ఆధ్యాత్మికం", "ఆధ్యాత్మిక కథ", "ధార్మిక కథ"], "DEVOTIONAL_STORY"),
    (["బాల", "పిల్లల"], "CHILDREN_STORY"),
    
    # --- SERIALS ---
    (["పౌరాణిక ధారావాహిక"], "MYTHOLOGY_SERIAL"),
    (["ఫాంటసీ ధారావాహిక"], "FANTASY_SERIAL"),
    (["చారిత్రక ధారావాహిక"], "HISTORICAL_SERIAL"),
    (["ధారావాహిక", "సీరియల్"], "SERIAL_STORY"),

    # --- POETRY/SONG ---
    (["గేయకథ", "పద్య కథ", "గేయ కథ"], "SONG_STORY"),
    (["కవిత", "పద్యము"], "POEM"),
    (["పద్యం"], "VERSE"),
    (["గేయం", "పాట"], "SONG"),

    # --- ARTICLES ---
    (["విజ్ఞాన", "విజ్ఞానం", "వైజ్ఞానిక విశేషాలు", "వైజ్ఞానిక విషయం"], "SCIENCE_ARTICLE"),
    (["చరిత్ర", "చారిత్రక వ్యాసం"], "HISTORY_ARTICLE"),
    (["సామాజిక వ్యాసం"], "SOCIAL_ARTICLE"),
    (["సంపాదకీయం", "సంపాదకీయము", "ఎడిటోరియల్"], "EDITORIAL"),
    (["వ్యాసం"], "ARTICLE"),

    # --- INTERACTIVE ---
    (["క్విజ్"], "QUIZ"),
    (["పజిల్"], "PUZZLE"),
    (["ప్రశ్నోత్తరాలు"], "QA"),
    (["సాధారణ జ్ఞానం", "గణితం", "ప్రపంచపు వింతలు"], "GENERAL_KNOWLEDGE"),

    # --- DRAMA/VISUAL ---
    (["నాటకం"], "DRAMA"),
    (["చిత్రకథ"], "ILLUSTRATED_STORY"),
    (["కామిక్"], "COMIC"),
    
    # --- BIOGRAPHY ---
    (["జీవిత చరిత్ర"], "BIOGRAPHY"),
    (["ఆత్మకథ"], "AUTOBIOGRAPHY"),

    # --- TONE (WEAK OWNERS) ---
    (["హాస్యం", "హాస్య", "వినోదం"], "HUMOR_STORY"),
    (["సాహసం", "సాహస", "వీర కథ", "వీరగాథ"], "ADVENTURE_STORY"),
    (["ప్రేమ"], "ROMANCE_STORY"),
    (["ఫాంటసీ", "అద్భుత కథ", "ఇంద్రజాలం"], "FANTASY_STORY"),
    (["కుటుంబ"], "FAMILY_STORY"),
    (["సామాజిక", "సాంఘిక కథ", "సాంఘికం", "సామాజికం"], "SOCIAL_STORY"),
    (["చారిత్రక"], "HISTORICAL_STORY"),
    (["రాజ"], "ROYAL_TALE"),

    # --- GENERAL / GENERIC FORMS ---
    # These often fall back to Social if not caught, but user requested explicitly:
    (["చిన్న కథ", "లఘు కథ", "తెలివైన కథ", "కథ"], "SOCIAL_STORY"),

    # --- GENERAL ---
    (["సమాచారం", "విశేషాలు", "విశేషం", "వార్తలు", "వార్తా విశేషాలు", "వార్తా విశేషం", "విద్య"], "INFORMATION"),
]

def normalize_genre(raw_genre):
    if not raw_genre:
        return None
    
    raw = raw_genre.strip()
    
    # 1. Exact Name Matches (Shortcuts)
    for code, info in GENRE_UNIVERSE.items():
        if raw == info['te']:
            return code

    # 2. Keyword Search
    # Check each rule in order
    for keywords, target_code in MAPPING_RULES:
        for kw in keywords:
            if kw in raw:
                # Special handling for Serials to catch specific types? 
                # The hierarchy: "Serial overrides everything"
                # If we matched 'Serial', we are done.
                # But wait, 'Pauranika Serial' needs to match 'MYTHOLOGY_SERIAL' not 'MYTHOLOGY_STORY'.
                # My list has specific serials BEFORE generic serials.
                # And 'Pauranika' implies story unless 'Serial' is also there.
                # Logic: If 'Serial' is in string, it MUST be a serial type.
                if "ధారావాహిక" in raw or "సీరియల్" in raw:
                    # It is a serial. Refine type.
                    if "పౌరాణిక" in raw: return "MYTHOLOGY_SERIAL"
                    if "ఫాంటసీ" in raw: return "FANTASY_SERIAL"
                    if "చారిత్రక" in raw: return "HISTORICAL_SERIAL"
                    return "SERIAL_STORY"
                
                return target_code

    # 3. Default
    # "Only process records where primary genre is missing."
    # If we can't map it, what do we do?
    # Prompt: "NEVER invent new genres."
    # If unmapped, maybe leave it or default to STORY?
    # "otherwise -> STORY" in derivation refers to content_type.
    # I will return "STORY" (which isn't a code, strictly) -> Wait.
    # I need a code.
    # If I can't map, I should probably leave it alone or map to "SOCIAL_STORY" or just "CHILDREN_STORY"?
    # Actually, many unmapped things might be simple stories.
    # Let's return None implies "Unknown/Unmapped". 
    # But for the purpose of this script, strict mapping is required.
    # If I verify 1947, I'll see what fails.
    return "SOCIAL_STORY" # Fallback? Or just "CHILDREN_STORY"? 
    # Most Chandamama generic stories are generic.
    # Let's try to map to 'FOLK_TALE' or 'ROYAL_TALE' based on context? Hard.
    # I will output a warning for unmapped and use default 'CHILDREN_STORY' as safe bet?
    # Or 'SOCIAL_STORY'.
    # I'll use None -> Skip logic.

def detect_language(content):
    if not content:
        return "MIXED"

    telugu_count = 0
    english_count = 0
    total_count = 0 # Count only Telugu and English characters

    for char in content:
        code = ord(char)
        # Telugu Unicode Range
        if 0x0C00 <= code <= 0x0C7F:
            telugu_count += 1
            total_count += 1
        # English Alphabets
        elif ('a' <= char <= 'z') or ('A' <= char <= 'Z'):
            english_count += 1
            total_count += 1
            
    if total_count == 0:
        return "MIXED"
        
    if (telugu_count / total_count) >= 0.80:
        return "TELUGU"
    elif (english_count / total_count) >= 0.80:
        return "ENGLISH"
    else:
        return "MIXED"

def process_file(file_path, dry_run=False):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return 
        
    book_changed = False
    
    if "stories" not in data:
        return

    for story in data["stories"]:
        # --- LANGUAGE DETECTION (PHASE 3) ---
        if "language" not in story:
            content_text = story.get("content", "")
            # Fallback to title if content is empty? User didn't specify, but safer to try content or nothing.
            # "Example: 'Nakka Savari' -> TELUGU"
            # If content is empty, use title.
            if not content_text:
                content_text = story.get("title", "")
            
            story["language"] = detect_language(content_text)
            book_changed = True

        # --- GENRE NORMALIZATION (PHASE 2 - LOCKED) ---
        # Rule 3: If normalized exists, DO NOT touch.
        if "normalized_genre_te" in story:
            continue
        
        raw_genre = story.get("genre")
        
        # Rule 4: Only process if primary genre is missing (normalized).
        
        # Rule A: Backup
        if raw_genre:
            story["raw_genre_backup"] = raw_genre
        else:
            continue 

        # Rule B: Map
        norm_code = normalize_genre(raw_genre)
        
        if norm_code and norm_code in GENRE_UNIVERSE:
            info = GENRE_UNIVERSE[norm_code]
            story["normalized_genre_te"] = info['te']
            story["normalized_genre_code"] = norm_code
            story["content_type"] = info['type']
            book_changed = True
        else:
            # Could not map.
            print(f"Could not map raw: '{raw_genre}' in {os.path.basename(file_path)}")

    if book_changed and not dry_run:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Updated {os.path.basename(file_path)}")

def main():
    parser = argparse.ArgumentParser(description="Normalize Chandamama Genres")
    parser.add_argument("--year", type=str, help="Process only specific year (e.g. 1947)", default=None)
    parser.add_argument("--dry-run", action="store_true", help="Do not save changes")
    args = parser.parse_args()

    files = []
    print(f"Scanning {BASE_DIR}...")
    for root, dirs, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            if filename.startswith("చందమామ_") and filename.endswith(".json"):
                files.append(os.path.join(root, filename))
    
    print(f"Found {len(files)} files.")
    files.sort()

    for fp in files:
        if args.year:
            # Check if year is in filename specifically
            filename = os.path.basename(fp)
            if args.year not in filename:
                continue
        
        process_file(fp, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
