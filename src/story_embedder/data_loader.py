import os
import json
from typing import List, Dict, Any, Generator
from . import config

def scan_chunk_files(base_dir: str = config.CHUNKS_DIR) -> List[str]:
    """
    Recursively find all *_chunks.json files in the base directory.
    Returns a sorted list of absolute file paths.
    """
    chunk_files = []
    if not os.path.exists(base_dir):
        print(f"Warning: Chunks directory not found at {base_dir}")
        return []
        
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file.endswith("_chunks.json"):
                chunk_files.append(os.path.join(root, file))
    
    # Sort for deterministic processing order
    return sorted(chunk_files)

def load_raw_chunks(file_path: str) -> List[Dict[str, Any]]:
    """
    Load raw chunk data from a JSON file.
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                print(f"Warning: File {file_path} did not contain a list of chunks.")
                return []
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []
