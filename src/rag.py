import os
import openai
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


def answer_question(question: str, context: str) -> str:
    """
    Generates an answer using an LLM with a strict, extensive prompt.
    """
    if not context:
        return "ఈ సమాచారం అందించిన కథలలో లేదు."

    # EXACT PROMPT (DO NOT MODIFY)
    prompt = f"""
PROMPT:
You are answering questions using a Telugu literature archive (Chandamama).

IMPORTANT RULES:
- Use ONLY the provided context.
- Do NOT use outside knowledge.
- Do NOT invent facts or stories.
- If the answer is NOT found in the context, say clearly:
  "ఈ సమాచారం అందించిన కథలలో లేదు."

Language:
- Answer in Telugu.

Context:
{context}

Question:
{question}

Answer:
"""
    return _call_llm_isolated(prompt)

def _call_llm_isolated(prompt: str) -> str:
    """
    Calls OpenAI API with strict deterministic settings.
    Requires OPENAI_API_KEY environment variable.
    """
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "ERROR: OPENAI_API_KEY not found in environment. Please check .env file."

    try:
        openai.api_key = api_key
        
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based strictly on the provided context."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1000
        )
        
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content.strip()
        else:
            return "No text returned from LLM."
            
    except Exception as e:
        return f"LLM Error: {str(e)}"
