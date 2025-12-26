
import os
import json

CHUNKS_DIR = r"d:/Viswam_Projects/chandamama-studio/chunks"

def count_chunks():
    total_chunks = 0
    file_count = 0
    for root, dirs, files in os.walk(CHUNKS_DIR):
        for file in files:
            if file.endswith("_chunks.json"):
                file_count += 1
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        total_chunks += len(data)
                except Exception as e:
                    print(f"Error reading {path}: {e}")
    
    print(f"Total Files Scanned: {file_count}")
    print(f"Total Chunks Found: {total_chunks}")

if __name__ == "__main__":
    count_chunks()
