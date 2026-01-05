import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HF_TOKEN")
print(f"Token present: {bool(token)}")

models_to_test = [
    "Qwen/Qwen2.5-72B-Instruct" 
]

for model in models_to_test:
    print(f"\n--- Testing {model} ---")
    client = InferenceClient(model=model, token=token)
    try:
        messages = [{"role": "user", "content": "Hello"}]
        resp = client.chat_completion(messages, max_tokens=10)
        print(f"SUCCESS: {resp.choices[0].message.content}")
    except Exception as e:
        print(f"FAILED: {repr(e)}")
