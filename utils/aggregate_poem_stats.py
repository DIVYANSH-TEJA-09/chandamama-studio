import json
import os
import glob
from collections import Counter

def aggregate_poem_stats(base_dir="d:/Viswam_Projects/Chandamama_2.0/1947-2012", output_file="stats/poem_stats.json"):
    print(f"Scanning {base_dir} for Poems/Songs...")
    
    poem_keywords = Counter()
    poem_themes = Counter() # Using genre as proxy if needed, or specific keywords
    
    # Target types
    target_types = ["POEM", "SONG", "VERSE", "LYRIC"]
    
    files = glob.glob(os.path.join(base_dir, "**/*.json"), recursive=True)
    count = 0 
    
    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if "stories" in data:
                for story in data["stories"]:
                    c_type = story.get("content_type", "UNKNOWN").upper()
                    
                    if c_type in target_types:
                        count += 1
                        # Aggregate Keywords
                        if "keywords" in story:
                             for kw in story["keywords"]:
                                if kw:
                                    poem_keywords[kw.strip()] += 1
                                    
        except Exception as e:
            # print(f"Error reading {file_path}: {e}")
            pass

    stats = {
        "total_poems": count,
        "top_keywords": dict(poem_keywords.most_common(50))
    }
    
    # Save back
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(stats, f, ensure_ascii=False, indent=4)
        
    print(f"Aggregated {count} poems. Stats saved to {output_file}.")

if __name__ == "__main__":
    aggregate_poem_stats()
