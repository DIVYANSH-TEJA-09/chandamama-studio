import os

from typing import Optional
from openai import OpenAI
from src import config

# Singleton to hold client instances
_client_instances = {}

def get_client(model_id: str):
    """
    Returns an authenticated client for the specified model_id.
    Handles both Hugging Face and OpenAI models.
    """
    global _client_instances
    
    if model_id in _client_instances:
        return _client_instances[model_id]
        
    # Determine which env var to use for the key
    # config.MODEL_API_KEY_MAP can contain either the Env Var NAME or the direct KEY
    config_value = config.MODEL_API_KEY_MAP.get(model_id, "HF_TOKEN")
    
    # 1. Try to load from Environment
    api_key = os.getenv(config_value)
    
    # 2. If not found in Env:
    if not api_key:
        # If the config value looks like an Env Var name (UPPERCASE with underscores), assume it's missing.
        if config_value.isupper() and "_" in config_value and " " not in config_value:
             print(f"ERROR: Environment variable '{config_value}' is missing from .env file.", flush=True)
             raise ValueError(f"Missing Environment Variable: {config_value}. Please add it to your .env file.")
        
        # Otherwise, assume config_value might be the key itself (fallback)
        api_key = config_value
    
    if not api_key or (len(api_key) < 10): # Basic validation
         raise ValueError(f"API Key not found for {model_id}. Checked env var '{config_value}' and direct value.")

    # Groq Models
    if config_value == "GROQ_API_KEY":
        print(f"Initializing Groq Client for {model_id}...", flush=True)
        from groq import Groq
        client = Groq(api_key=api_key)
        _client_instances[model_id] = ("groq", client)

    # OpenAI Models
    elif "gpt" in model_id.lower():
        print(f"Initializing OpenAI Client for {model_id}...", flush=True)
        client = OpenAI(api_key=api_key)
        _client_instances[model_id] = ("openai", client)
        
    # Hugging Face Models
    else:
        print(f"Initializing HF Inference Client for {model_id}...", flush=True)
        # Using huggingface_hub.InferenceClient
        from huggingface_hub import InferenceClient
        client = InferenceClient(model=model_id, token=api_key)
        _client_instances[model_id] = ("hf", client)
        
    return _client_instances[model_id]

def generate_response_multi(
    model_id: str,
    prompt: str, 
    system_prompt: Optional[str] = None, 
    max_tokens: int = config.LLM_MAX_TOKENS,
    temperature: float = config.LLM_TEMPERATURE,
    stream: bool = False
):
    """
    Generates response using the specified model.
    If stream=True, returns a generator yielding chunks of text.
    Otherwise, returns the full string.
    """
    try:
        client_type, client = get_client(model_id)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        # OPENAI & GROQ (Compatible APIs)
        if client_type in ["openai", "groq"]:
            # Streaming Mode
            if stream:
                response_stream = client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=True
                )
                for chunk in response_stream:
                    if chunk.choices and len(chunk.choices) > 0:
                        delta = chunk.choices[0].delta
                        if delta.content:
                            yield delta.content
            # Non-Streaming Mode
            else:
                response = client.chat.completions.create(
                    model=model_id,
                    messages=messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    stream=False
                )
                return response.choices[0].message.content or ""

        # HUGGING FACE
        elif client_type == "hf":
            # Streaming Mode
            if stream:
                response_stream = client.chat_completion(
                    messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    stream=True
                )
                for chunk in response_stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        yield chunk.choices[0].delta.content
            # Non-Streaming Mode
            else:
                response = client.chat_completion(
                    messages,
                    max_tokens=max_tokens,
                    temperature=temperature,
                    top_p=0.9,
                    stream=False
                )
                if response.choices and response.choices[0].message.content:
                    return response.choices[0].message.content
                return ""
            
    except Exception as e:
        if stream:
             yield f"Error ({model_id}): {str(e)}"
        else:
             return f"Error ({model_id}): {str(e)}"
