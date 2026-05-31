import os
from typing import List
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 8 and "Replace" not in GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini Client in embeddings: {e}")

def get_embedding(text: str, is_query: bool = False) -> List[float]:
    """Generates a vector embedding for a single string using Gemini API."""
    if not client:
        # Fallback Mock Embedding (768 dimensions)
        import random
        random.seed(hash(text))
        return [random.uniform(-0.1, 0.1) for _ in range(768)]

    try:
        task_type = "RETRIEVAL_QUERY" if is_query else "RETRIEVAL_DOCUMENT"
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=text,
            config={"task_type": task_type}
        )
        return result.embeddings[0].values
    except Exception as e:
        print(f"Gemini embedding API failed: {e}. Falling back to deterministic pseudo-vectors.")
        # Graceful fallback
        import random
        random.seed(hash(text))
        return [random.uniform(-0.1, 0.1) for _ in range(768)]

def get_embeddings(texts: List[str]) -> List[List[float]]:
    """Generates vector embeddings for a list of strings."""
    if not client:
        return [get_embedding(t) for t in texts]

    try:
        result = client.models.embed_content(
            model="gemini-embedding-001",
            contents=texts,
            config={"task_type": "RETRIEVAL_DOCUMENT"}
        )
        return [emb.values for emb in result.embeddings]
    except Exception as e:
        print(f"Gemini batch embedding API failed: {e}. Processing individually.")
        # Fallback to individual calls
        return [get_embedding(t) for t in texts]
