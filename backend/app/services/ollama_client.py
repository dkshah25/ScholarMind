import os
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()

OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434").rstrip("/")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3:8b")
OLLAMA_EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text")

class OllamaClient:
    """Centralized client for communication with local Ollama service."""
    
    @staticmethod
    def is_online() -> bool:
        """Pings the Ollama server to verify availability."""
        try:
            resp = requests.get(f"{OLLAMA_BASE_URL}/", timeout=1.5)
            return resp.status_code == 200
        except Exception:
            return False

    @staticmethod
    def generate(
        prompt: str,
        system_prompt: Optional[str] = None,
        format_json: bool = False,
        temperature: float = 0.1,
        num_ctx: int = 16384
    ) -> str:
        """
        Sends a generation request to Ollama's /api/generate endpoint.
        Returns the raw string output from the LLM.
        """
        payload = {
            "model": OLLAMA_MODEL,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_ctx": num_ctx
            }
        }
        
        if system_prompt:
            payload["system"] = system_prompt
            
        if format_json:
            payload["format"] = "json"
            
        try:
            resp = requests.post(
                f"{OLLAMA_BASE_URL}/api/generate",
                json=payload,
                timeout=300.0  # 5-minute timeout to support slower CPU-based local runs
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("response", "").strip()
        except Exception as e:
            print(f"[Ollama Error] generation failed: {e}")
            raise e

    @staticmethod
    def get_embedding(text: str) -> List[float]:
        """
        Generates a vector embedding for a single text using /api/embeddings.
        """
        payload = {
            "model": OLLAMA_EMBED_MODEL,
            "prompt": text
        }
        try:
            resp = requests.post(
                f"{OLLAMA_BASE_URL}/api/embeddings",
                json=payload,
                timeout=15.0
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("embedding", [])
        except Exception as e:
            print(f"[Ollama Error] embedding generation failed: {e}")
            raise e
