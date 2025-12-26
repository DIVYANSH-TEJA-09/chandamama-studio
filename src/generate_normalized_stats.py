import os
import json
import collections

BASE_DIR = "d:/Viswam_Projects/Chandamama_2.0/1947-2012"
OUTPUT_FILE = "stats/normalized_stats.json"

def main():
    stats = {
        "total_files": 0,
        "total_stories": 0,
        "genre_counts": collections.defaultdict(int),
        "content_type_counts": collections.defaultdict(int),
        "unmapped_genres": collections.defaultdict(int)
    }

    print(f"Scanning {BASE_DIR}...")
    for root, dirs, filenames in os.walk(BASE_DIR):
        for filename in filenames:
            if filename.startswith("చందమామ_") and filename.endswith(".json"):
                stats["total_files"] += 1
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        
                        # Handle both single object or list of stories (though usually it's list under 'stories')
                        stories = data.get("stories", [])
                        
                        for story in stories:
                            stats["total_stories"] += 1
                            
                            # Count Normalized Genre Code
                            genre_code = story.get("normalized_genre_code", "UNKNOWN")
                            stats["genre_counts"][genre_code] += 1
                            
                            # Count Content Type
                            c_type = story.get("content_type", "UNKNOWN")
                            stats["content_type_counts"][c_type] += 1
                            
                            # Track unmapped/fallback if needed (though map script handles this)
                            if genre_code == "SOCIAL_STORY" and story.get("raw_genre_backup") not in ["సామాజిక కథ", None]:
                                # Use raw genre as key to see what fell back
                                raw = story.get("raw_genre_backup", "None")
                                stats["unmapped_genres"][raw] += 1

                except Exception as e:
                    print(f"Error reading {filename}: {e}")

    # Convert defaultdicts to dicts for JSON serialization and sort descending
    final_stats = {
        "total_files": stats["total_files"],
        "total_stories": stats["total_stories"],
        "genre_counts": dict(sorted(stats["genre_counts"].items(), key=lambda item: item[1], reverse=True)),
        "content_type_counts": dict(sorted(stats["content_type_counts"].items(), key=lambda item: item[1], reverse=True)),
        # Top 50 unmapped for insight
        "top_social_fallbacks": dict(sorted(stats["unmapped_genres"].items(), key=lambda item: item[1], reverse=True)[:50])
    }

    print("Writing stats to", OUTPUT_FILE)
    print(json.dumps(final_stats, indent=2, ensure_ascii=False))

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(final_stats, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    main()
