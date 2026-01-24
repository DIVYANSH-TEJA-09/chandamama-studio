import re

def get_telugu_aksharas(text):
    """
    Splits Telugu text into Aksharas (Syllables).
    An Akshara is (Consonant + Vowel Signs + Modifiers) OR (Independent Vowel).
    
    Regex Explanation:
    - [^\\u0C00-\\u0C7F]+ : Non-Telugu characters (spaces, punctuation) - treated as individual units or ignored depending on usage.
    - ...complex grapheme clustering...
    
    A robust approximation for Telugu/Indian languages:
    (Consonant + Virama)* + Consonant + (Vowel Sign)* + (Modifier)*
    OR Independent Vowel + (Modifier)*
    """
    
    # Simple Grapheme Cluster Regex for Telugu
    # Covers: 
    # Vowels/Consonants: [\u0C05-\u0C39\u0C58-\u0C61]
    # Matras/Virama/Modifiers: [\u0C3E-\u0C56\u0C62-\u0C6F\u0C01-\u0C03]
    
    # This regex attempts to grab a base character followed by any number of combining marks.
    # Base: \u0C05-\u0C39\u0C58-\u0C61 (Independent vowels and consonants)
    # Combining: \u0C3E-\u0C56 (Vowel signs), \u0C4D (Virama), \u0C01-\u0C03 (Anusvara/Visarga/Candrabindu), \u0C62-\u0C63
    
    # Rule: Match a Base char, followed by zero or more properties.
    # Note: Consonant clusters (Samayukta aksharas) are C + Virama + C. 
    # Standard Unicode grapheme clusters usually keep these together.
    # \X matches a grapheme cluster in regex module, but Python's re doesn't support \X well in all versions without 'regex' module.
    # We will use a custom constructing regex.
    
    # Ranges:
    # 0C00-0C7F is Telugu
    
    # Pattern:
    # Base Character (C or V)
    # Followed by any sequence of:
    # - Virama (\u0C4D) + Base Character (for conjuncts)
    # - Vowel Signs
    # - Modifiers (Anusvara etc)
    
    # To simplify: We can iterate and join.
    # Or use a logic: start new token if char is a Base, append if char is a mark.
    # EXCEPTION: If char is Base, but previous was Virama, it merges with previous (Conjunct).
    
    aksharas = []
    current = ""
    
    # Telugu Unicode Block: 0C00 - 0C7F
    
    # Set of characters that are independent starts (Vowels, Consonants)
    # 0C05-0C39, 0C58-0C61
    
    # Set of characters that join (Matras, Virama, Modifiers)
    # 0C01-0C03 (Modifiers)
    # 0C3E-0C4C (Vowel Signs)
    # 0C4D (Virama)
    # 0C55-0C56 (Length marks)
    
    for char in text:
        if not current:
            current += char
            continue
            
        codepoint = ord(char)
        
        # Check if char is a combining mark OR a joining consonant (after virama)
        is_telugu = 0x0C00 <= codepoint <= 0x0C7F
        
        if not is_telugu:
            # Non-telugu char (space, punctuation), end current akshara
            aksharas.append(current)
            current = char
            continue
            
        # If it is a combining mark (Matra, Virama, Anusvara)
        # 0C01-0C03, 0C3E-0C56
        is_mark = (0x0C01 <= codepoint <= 0x0C03) or (0x0C3E <= codepoint <= 0x0C56) or (0x0C62 <= codepoint <= 0x0C63)
        
        if is_mark:
            current += char
        elif codepoint == 0x0C4D: # Virama
            current += char
        else:
            # It's a Base Character (Consonant/Vowel)
            # Check if previous char was Virama (halant)
            # If previous was Virama, this consonant is part of the cluster (KA + VIRAMA + KA)
            if current and ord(current[-1]) == 0x0C4D:
                current += char
            else:
                # Start new Akshara
                aksharas.append(current)
                current = char
                
    if current:
        aksharas.append(current)
        
    return aksharas

def clean_and_split_word(word_text):
    """
    Cleans a word (removes whitespace) and splits into Aksharas.
    Usage for Crossword: Each akshara goes into a cell.
    """
    # Remove whitespace
    clean = word_text.strip().replace(" ", "")
    return get_telugu_aksharas(clean)
