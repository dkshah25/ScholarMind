import os
from typing import List
from dotenv import load_dotenv
from app.services.ollama_client import OllamaClient

load_dotenv()

def get_embedding(text: str, is_query: bool = False) -> List[float]:
    """Generates a vector embedding for a single string using local Ollama nomic-embed-text."""
    if not OllamaClient.is_online():
        # Fallback Mock Embedding (768 dimensions)
        import random
        random.seed(hash(text))
        return [random.uniform(-0.1, 0.1) for _ in range(768)]

    try:
        # nomic-embed-text natively outputs 768-dimensional float arrays
        return OllamaClient.get_embedding(text)
    except Exception as e:
        print(f"Ollama embedding API failed: {e}. Falling back to deterministic pseudo-vectors.")
        # Graceful fallback
        import random
        random.seed(hash(text))
        return [random.uniform(-0.1, 0.1) for _ in range(768)]

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generates vector embeddings for a list of strings using local Ollama."""
    # Process sequentially for maximum robustness across all Ollama versions
    return [get_embedding(t) for t in texts]
