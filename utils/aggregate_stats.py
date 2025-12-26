import json
import os
import glob
from collections import Counter
from pathlib import Path

def aggregate_stats(base_dir="d:/Viswam_Projects/Chandamama_2.0/1947-2012", global_stats_path="stats/global_stats.json"):
    print(f"Scanning {base_dir}...")
    
    character_counts = Counter()
    location_counts = Counter()
    keyword_counts = Counter()  # Also aggregate keywords while we are at it

    files = glob.glob(os.path.join(base_dir, "**/*.json"), recursive=True)
    print(f"Found {len(files)} JSON files.")

    for file_path in files:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            if "stories" in data:
                for story in data["stories"]:
                    # Aggregate Characters
                    if "characters" in story:
                        for char in story["characters"]:
                            if char:
                                character_counts[char.strip()] += 1
                    
                    # Aggregate Locations
                    if "locations" in story:
                        for loc in story["locations"]:
                            if loc:
                                location_counts[loc.strip()] += 1
                                
                    # Aggregate Keywords
                    if "keywords" in story:
                         for kw in story["keywords"]:
                            if kw:
                                keyword_counts[kw.strip()] += 1

        except Exception as e:
            print(f"Error reading {file_path}: {e}")

    # Load existing global stats
    try:
        with open(global_stats_path, "r", encoding="utf-8") as f:
            global_stats = json.load(f)
    except FileNotFoundError:
        print("global_stats.json not found, creating new one.")
        global_stats = {}

    # Update global stats
    global_stats["top_characters"] = dict(character_counts.most_common(100)) # Top 100
    global_stats["top_locations"] = dict(location_counts.most_common(100))   # Top 100
    global_stats["top_keywords"] = dict(keyword_counts.most_common(100))     # Top 100
    
    # Save back
    with open(global_stats_path, "w", encoding="utf-8") as f:
        json.dump(global_stats, f, ensure_ascii=False, indent=4)
        
    print(f"Updated global_stats.json with {len(character_counts)} unique characters and {len(location_counts)} unique locations.")

if __name__ == "__main__":
    aggregate_stats()
