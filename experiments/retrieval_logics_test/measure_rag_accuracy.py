
import os
import sys
import random
import time
import numpy as np
from dotenv import load_dotenv

# Ensure we can import from src
current_file_path = os.path.abspath(__file__)
current_dir = os.path.dirname(current_file_path)
exp_dir = os.path.dirname(current_dir)
project_root = os.path.dirname(exp_dir)

if project_root not in sys.path:
    sys.path.append(project_root)

# Load env vars
load_dotenv()

from src.retrieval.vector_search import StoryEmbeddingsRetriever
from src import config

def extract_query_from_text(text, length=150):
    if len(text) < length: return text
    start_zone = int(len(text) * 0.25)
    end_zone = int(len(text) * 0.75)
    if end_zone - start_zone < length:
        start_index = random.randint(0, len(text) - length)
    else:
        start_index = random.randint(start_zone, end_zone - length)
    return text[start_index : start_index + length]

def main():
    print("Initializing RAG Test...", flush=True)
    
    try:
        retriever = StoryEmbeddingsRetriever(top_k=5)
    except Exception as e:
        print(f"Error: {e}", flush=True)
        return

    client = retriever.client
    collection = config.STORY_COLLECTION_NAME
    
    print(f"Checking collection '{collection}'...", flush=True)
    try:
        count_res = client.count(collection_name=collection)
        print(f"Total points in collection: {count_res.count}", flush=True)
        if count_res.count == 0:
            print("❌ The collection is empty! Please run `rebuild_db.py` to populate it.", flush=True)
            return
    except Exception as e:
        print(f"Error checking count: {e}", flush=True)
        return

    print("Fetching 50 stories...", flush=True)
    response, _ = client.scroll(
        collection_name=collection,
        limit=50,
        with_payload=True,
        with_vectors=False
    )
    
    if not response:
        print(f"Scroll returned no results.", flush=True)
        return

    print(f"Scroll returned {len(response)} points.", flush=True)
    # Debug first payload
    if response:
        print(f"First point Payload keys: {list(response[0].payload.keys())}", flush=True)
    
    test_set = []
    skipped_short = 0
    skipped_no_text = 0
    
    for point in response:
        payload = point.payload
        text = payload.get('text', '')
        
        if not text:
            skipped_no_text += 1
            continue
            
        if len(text) < 300: 
            skipped_short += 1
            continue
            
        test_set.append({
            "id": point.id,
            "query": extract_query_from_text(text),
            "title": payload.get('title', 'Unknown')
        })
    
    print(f"Prepared {len(test_set)} valid test samples.", flush=True)
    print(f"(Skipped: {skipped_no_text} no text, {skipped_short} too short)", flush=True)
    
    if len(test_set) == 0:
        return

    # Limit to 20 for speed
    test_set = test_set[:20]
    
    hits_at_1 = 0
    hits_at_5 = 0
    mrr_score = 0
    latencies = []
    
    print(f"Running {len(test_set)} tests...", flush=True)
    
    for i, case in enumerate(test_set):
        target_id = case['id']
        query = case['query']
        
        start = time.time()
        results = retriever.retrieve_points(query)
        latencies.append(time.time() - start)
        
        rank = float('inf')
        for idx, hit in enumerate(results):
            if str(hit.id) == str(target_id):
                rank = idx + 1
                break
        
        if rank == 1: hits_at_1 += 1
        if rank <= 5: hits_at_5 += 1
        if rank != float('inf'): mrr_score += 1.0 / rank

    total = len(test_set)
    metrics = {
        "N": total,
        "Hit@1": hits_at_1 / total,
        "Hit@5": hits_at_5 / total,
        "MRR": mrr_score / total,
        "Latency": np.mean(latencies)
    }
    
    print("\nRESULTS:", flush=True)
    print(f"Hit Rate @ 1: {metrics['Hit@1']:.2%}", flush=True)
    print(f"Hit Rate @ 5: {metrics['Hit@5']:.2%}", flush=True)
    print(f"MRR: {metrics['MRR']:.4f}", flush=True)
    print(f"Avg Latency: {metrics['Latency']:.4f}s", flush=True)

if __name__ == "__main__":
    main()
