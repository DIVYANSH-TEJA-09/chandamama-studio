import os
from huggingface_hub import InferenceClient
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("HF_TOKEN")
print(f"Token loaded: {'Yes' if token else 'No'}")
if token:
    print(f"Token length: {len(token)}")
    print(f"Token start: {token[:4]}...")

model = "Qwen/Qwen2.5-72B-Instruct"
client = InferenceClient(model=model, token=token)

print(f"Testing {model}...")
try:
    messages = [{"role": "user", "content": "Hello"}]
    resp = client.chat_completion(messages, max_tokens=10)
    print(f"SUCCESS: {resp.choices[0].message.content}")
except Exception as e:
    print(f"FAILED: {e}")
