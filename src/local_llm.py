import os
from huggingface_hub import InferenceClient
from typing import Optional
from src import config
from src.local_llm_multi import generate_response_multi

# --- WRAPPER FOR SINGLE MODEL ---
# This file is maintained for backward compatibility.
# It now redirects to local_llm_multi for robust handling of both HF and OpenAI.

def get_client():
    """Deprecated: Use local_llm_multi.get_client instead."""
    from src.local_llm_multi import get_client as get_client_multi
    return get_client_multi(config.LLM_MODEL_ID)

def generate_response(
    prompt: str, 
    system_prompt: Optional[str] = None, 
    max_tokens: int = config.LLM_MAX_TOKENS,
    temperature: float = config.LLM_TEMPERATURE
) -> str:
    """
    Wrapper for local_llm_multi to maintain compatibility.
    Uses config.LLM_MODEL_ID as the default model.
    """
    return generate_response_multi(
        model_id=config.LLM_MODEL_ID,
        prompt=prompt,
        system_prompt=system_prompt,
        max_tokens=max_tokens,
        temperature=temperature
    )
        
    except Exception as e:
        return f"HF API Error: {str(e)}"
