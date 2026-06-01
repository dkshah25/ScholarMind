import os
import re
import json
import uuid
import pypdf
from typing import Dict, Any, Tuple
from dotenv import load_dotenv
from app.services.ollama_client import OllamaClient

load_dotenv()

def extract_raw_text(file_path: str) -> str:
    """Extracts raw text from a PDF file using pypdf."""
    text = ""
    try:
        reader = pypdf.PdfReader(file_path)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    except Exception as e:
        print(f"Error reading PDF {file_path}: {e}")
    return text

def parse_metadata_with_gemini(raw_text: str) -> Dict[str, Any]:
    """Uses local Ollama Qwen3:8B to extract clean, structured metadata from first 2 pages of paper text."""
    default_metadata = {
        "title": "Unknown Title",
        "authors": "Unknown Authors",
        "journal": "Unknown Journal/Conference",
        "year": 2026,
        "abstract": "No abstract extracted."
    }

    if not OllamaClient.is_online():
        print("Ollama server offline. Skipping LLM-based metadata extraction.")
        return default_metadata

    # Take the first ~8000 characters which usually contain the header, authors, and abstract
    header_text = raw_text[:8000]

    prompt = f"""
You are an expert research ingestion assistant. Extract structured metadata from the academic paper's header text below.

Header Text:
{header_text}

---
Extract the following fields and return ONLY a valid JSON object matching this schema:
{{
  "title": "Full paper title",
  "authors": "Comma-separated authors",
  "journal": "Journal, Conference name or arXiv if applicable",
  "year": YYYY (Integer representing publication year),
  "abstract": "Full paper abstract paragraph"
}}
Do NOT include any markdown block ticks (like ```json) or explanation, return only raw valid JSON.
"""
    try:
        # Call local Qwen3 model with formatting forced as json
        clean_json_str = OllamaClient.generate(
            prompt=prompt,
            format_json=True,
            temperature=0.1
        )

        # Clean any markdown wrapper if the model added it despite instructions
        if clean_json_str.startswith("```"):
            clean_json_str = re.sub(r"^```(?:json)?\n", "", clean_json_str)
            clean_json_str = re.sub(r"\n```$", "", clean_json_str)
        
        parsed = json.loads(clean_json_str.strip())
        
        # Validate data types
        if not isinstance(parsed.get("year"), int):
            try:
                parsed["year"] = int(parsed["year"])
            except:
                parsed["year"] = 2026

        # Fill defaults for missing keys
        for k in default_metadata:
            if k not in parsed or not parsed[k]:
                parsed[k] = default_metadata[k]
                
        return parsed

    except Exception as e:
        print(f"Ollama metadata extraction failed: {e}. Returning default placeholders.")
        return default_metadata

def parse_and_ingest_pdf(file_path: str) -> Tuple[str, Dict[str, Any]]:
    """
    Parses a PDF file.
    Returns: (raw_text, metadata_dict)
    """
    raw_text = extract_raw_text(file_path)
    if not raw_text.strip():
        # Fallback for empty/scanned PDFs
        print(f"Warning: Extracted empty text from {file_path}.")
        metadata = {
            "title": os.path.basename(file_path).replace(".pdf", ""),
            "authors": "Unknown",
            "journal": "Local Upload",
            "year": 2026,
            "abstract": "Empty or scanned PDF document."
        }
        return "", metadata

    metadata = parse_metadata_with_gemini(raw_text)
    
    # Check if Title extraction returned empty or fallback
    if metadata["title"] == "Unknown Title":
        # Fallback title as filename
        metadata["title"] = os.path.basename(file_path).replace(".pdf", "")

    return raw_text, metadata
