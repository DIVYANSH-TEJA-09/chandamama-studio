import os
from huggingface_hub import InferenceClient
from typing import Optional

# Configuration
MODEL_ID = "Qwen/Qwen2.5-7B-Instruct"
# Using the InferenceClient which handles the API calls
_client_instance = None

def get_client() -> InferenceClient:
    global _client_instance
    if _client_instance is None:
        token = os.getenv("HF_TOKEN")
        if not token:
            raise ValueError("HF_TOKEN not found in environment variables. Please add it to your .env file.")
        
        print(f"Initializing HF Inference Client for {MODEL_ID}...", flush=True)
        _client_instance = InferenceClient(model=MODEL_ID, token=token)
        
    return _client_instance

def generate_response(
    prompt: str, 
    system_prompt: Optional[str] = None, 
    max_tokens: int = 3000,
    temperature: float = 0.7
) -> str:
    """
    Generates response using Hugging Face Inference API (Chat Completion via Serverless).
    """
    client = get_client()
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    
    messages.append({"role": "user", "content": prompt})
    
    try:
        response = client.chat_completion(
            messages,
            max_tokens=max_tokens,
            temperature=temperature,
            top_p=0.9,
            frequency_penalty=0.5  # Reduce repetition
        )
        if response.choices and response.choices[0].message.content:
            return response.choices[0].message.content
        return ""
        
    except Exception as e:
        return f"HF API Error: {str(e)}"
