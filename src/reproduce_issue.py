
import sys
import os
from retrieval_logics_test.contextual_retrieval import ContextualRetriever
from retrieval_logics_test.common_utils import get_qdrant_client

print("Initializing Retriever...")
try:
    retriever = ContextualRetriever(top_k=1)
    print("Retriever initialized.")
    
    print("Checking Client methods directly...")
    client = get_qdrant_client()
    print(f"Client type: {type(client)}")
    print(f"Has query_points: {hasattr(client, 'query_points')}")
    print(f"Has search: {hasattr(client, 'search')}")
    
    print("Attempting retrieve...")
    query = "king"
    context = retriever.retrieve(query)
    print("Retrieve success!")
    print(f"Context length: {len(context)}")

except Exception as e:
    print(f"Caught Error: {e}")
    import traceback
    traceback.print_exc()
