import os

from typing import List, Dict, Any

def build_rag_context(grouped_stories: List[Dict[str, Any]], max_stories: int = 3) -> str:
    """
    Formats the top stories into a strict context string for RAG.
    """
    selected_stories = grouped_stories[:max_stories]
    context_parts = []
    
    for story in selected_stories:
        title = story.get("title", "Unknown")
        year = story.get("year", "Unknown")
        month = story.get("month", "Unknown")
        story_id = story.get("story_id", "Unknown")
        
        # Header with ID
        context_parts.append(f"### Story: {title} (ID: {story_id}, Date: {year}-{month})")
        
        # Chunks (use 'text' field)
        for chunk in story.get("chunks", []):
            text = chunk.get("text", "").strip()
            if text:
                context_parts.append(text)
        
        context_parts.append("") # Separator
        
    return "\n".join(context_parts).strip()



# def answer_question(question: str, context: str) -> str:
#     """
#     Generates an answer using an LLM with a strict, extensive prompt.
#     """
#     if not context:
#         return "ఈ సమాచారం అందించిన కథలలో లేదు."
#
#     # EXACT PROMPT (DO NOT MODIFY)
#     prompt = f"""
# PROMPT:
# You are answering questions using a Telugu literature archive (Chandamama).
#
# IMPORTANT RULES:
# - Use ONLY the provided context.
# - Do NOT use outside knowledge.
# - Do NOT invent facts or stories.
# - If the answer is NOT found in the context, say clearly:
#   "ఈ సమాచారం అందించిన కథలలో లేదు."
#
# Language:
# - Answer in Telugu.
#
# Context:
# {context}
#
# Question:

def generate_answer(query: str, context: str) -> str:
    """
    Generates an answer using Local Qwen-72B based on the retrieved context.
    """
    
    # Construct System Prompt
    system_prompt_text = """
    You are a helpful assistant for the Chandamama Children's Magazine archive.
    Use the provided context to answer the user's question accurately.
    If the answer is not in the context, say "I don't know based on the archive."
    Do not hallucinate.
    """
    
    # Construct User Prompt
    user_prompt = f"""
    Context:
    {context}
    
    Question: {query}
    
    Answer (in English or Telugu as asked):
    """
    
    try:
        from src.local_llm import generate_response
        return generate_response(user_prompt, system_prompt=system_prompt_text)
    except Exception as e:
        return f"Error generating answer: {str(e)}"


