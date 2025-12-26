import os
import json
import sys

print("Start...", flush=True)

BASE_DIR = r"d:/Viswam_Projects/Chandamama_2.0/1947-2012"
OUTPUT_DIR = r"d:/Viswam_Projects/Chandamama_2.0/chunks"
TEST_FILE = r"d:/Viswam_Projects/Chandamama_2.0/1947-2012/1957/చందమామ_1957_02.json"

TARGET_MIN = 300
TARGET_MAX = 500
HARD_MIN = 150
HARD_MAX = 700

print("Config done. Defining functions...", flush=True)

def get_token_count(text):
    if not text:
        return 0
    return len(text.split()) * 2

def split_large_paragraph(text, max_tokens):
    sentences = text.replace(".", ".|").replace("?", "?|").replace("!", "!|").split("|")
    sub_chunks = []
    current_sub = ""
    for sent in sentences:
        if not sent.strip():
            continue
        proposed = current_sub + sent
        if get_token_count(proposed) > max_tokens:
            if current_sub:
                sub_chunks.append(current_sub)
            current_sub = sent
        else:
            current_sub = proposed
    if current_sub:
        sub_chunks.append(current_sub)
    return sub_chunks

print("Functions 1 done...", flush=True)

def create_chunk_object(story, chunk_text, index, year, month, source_path):
    return {
        "story_id": story.get("story_id", "UNKNOWN"),
        "chunk_id": f"{story.get('story_id', 'UNKNOWN')}_{index:02d}",
        "chunk_index": index,
        "year": int(year) if year.isdigit() else 0,
        "month": int(month) if month.isdigit() else 0,
        "source_path": source_path,
        "title": story.get("title", ""),
        "author": story.get("author", ""),
        "normalized_genre_code": story.get("normalized_genre_code", ""),
        "content_type": story.get("content_type", ""),
        "keywords": story.get("keywords", []),
        "language": story.get("language", ""),
        "text": chunk_text
    }

def chunk_story(story, year, month, source_path):
    content = story.get("content", "")
    if not content:
        return []
    paragraphs = [p.strip() for p in content.split('\n') if p.strip()]
    chunks = []
    current_chunk_paras = []
    current_tokens = 0
    i = 0
    while i < len(paragraphs):
        para = paragraphs[i]
        para_tokens = get_token_count(para)
        
        if para_tokens > HARD_MAX:
            if current_chunk_paras:
                chunks.append("\n".join(current_chunk_paras))
                current_chunk_paras = []
                current_tokens = 0
            sub_parts = split_large_paragraph(para, HARD_MAX)
            chunks.extend(sub_parts)
            i += 1
            continue

        if current_tokens + para_tokens > TARGET_MAX:
             # Logic to close chunk
             if current_tokens + para_tokens > HARD_MAX or current_tokens >= TARGET_MIN:
                 if current_chunk_paras:
                     chunks.append("\n".join(current_chunk_paras))
                     last = current_chunk_paras[-1]
                     current_chunk_paras = [last, para]
                     current_tokens = get_token_count(last) + para_tokens
                 else:
                     current_chunk_paras = [para]
                     current_tokens = para_tokens
             else:
                 current_chunk_paras.append(para)
                 current_tokens += para_tokens
        else:
             current_chunk_paras.append(para)
             current_tokens += para_tokens
        i += 1
    
    if current_chunk_paras:
        chunks.append("\n".join(current_chunk_paras))
        
    final_objs = []
    final_objs = []
    for idx, text in enumerate(chunks):
        final_objs.append(create_chunk_object(story, text, idx+1, year, month, source_path))
    return final_objs

print("Functions 2 done. processing...", flush=True)

def process_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading {file_path}: {e}", flush=True)
        return

    # Path logic
    norm_path = file_path.replace("\\", "/")
    parts = norm_path.split("/")
    year = "Unknown"
    for part in parts:
        if part.isdigit() and len(part) == 4:
            year = part
            
    out_year_dir = os.path.join(OUTPUT_DIR, year)
    if not os.path.exists(out_year_dir):
        os.makedirs(out_year_dir, exist_ok=True)
        
    filename = os.path.basename(file_path)
    # Extract year/month from filename "చందమామ_YYYY_MM.json"
    month = "00"
    try:
        parts = filename.replace(".json", "").split("_")
        if len(parts) >= 3:
            # parts[0] = చందమామ, parts[1] = YYYY, parts[2] = MM
            # Validate extracted year matches directory year for sanity
            if parts[1] == year:
                 month = parts[2]
            else:
                 # Fallback if filename extraction fails but directory year is known
                 pass 
    except:
        pass

    # Calculate source_path relative to BASE_DIR (e.g., "1947/చందమామ_1947_07.json")
    try:
        source_path = os.path.relpath(file_path, BASE_DIR).replace("\\", "/")
    except ValueError:
        source_path = os.path.basename(file_path) # Fallback if path issue

    out_filename = filename.replace(".json", "_chunks.json")
    out_path = os.path.join(out_year_dir, out_filename)
    
    # Check if exists to skip? No, overwrite.
    
    book_chunks = []
    if "stories" in data:
        for story in data["stories"]:
            book_chunks.extend(chunk_story(story, year, month, source_path))
            
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(book_chunks, f, ensure_ascii=False, indent=4)
    # print(f"Saved {len(book_chunks)} chunks to {out_filename}", flush=True) # Reduce spam

def main():
    print("Starting Full Rollout...", flush=True)
    files = []
    for root, dirs, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            if filename.startswith("చందమామ_") and filename.endswith(".json"):
                files.append(os.path.join(root, filename))
    
    files.sort()
    print(f"Found {len(files)} files.", flush=True)
    
    for i, fp in enumerate(files):
        process_file(fp)
        if (i+1) % 50 == 0:
            print(f"Processed {i+1}/{len(files)} files...", flush=True)
            
    print("Done.", flush=True)

if __name__ == "__main__":
    main()
