import sys
import os

# Add backend directory to system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.ollama_client import OllamaClient

def run_tests():
    print("=== OLLAMA SANITY VERIFICATION ===")
    
    print("\n1. Testing Connection Status...")
    online = OllamaClient.is_online()
    print(f"Ollama Online: {online}")
    if not online:
        print("ERROR: Ollama server appears to be offline. Make sure it is running on http://localhost:11434.")
        return

    print("\n2. Testing Generation (Qwen3:8B)...")
    prompt = "Return a JSON object containing a key 'status' with value 'active' and 'message' with value 'hello from ollama'. Do not include markdown ticks."
    try:
        response = OllamaClient.generate(prompt=prompt, format_json=True, temperature=0.1)
        print(f"Response: {response}")
    except Exception as e:
        print(f"ERROR: Qwen3 generation failed: {e}")

    print("\n3. Testing Embeddings (Nomic Embed Text)...")
    try:
        embedding = OllamaClient.get_embedding("This is a semantic research passage.")
        print(f"Embedding Success: Vector length = {len(embedding)}")
        if len(embedding) > 0:
            print(f"First 5 dimensions: {embedding[:5]}")
    except Exception as e:
        print(f"ERROR: Embedding generation failed: {e}")

if __name__ == "__main__":
    run_tests()
