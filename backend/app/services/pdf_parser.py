import os
import re
import json
import uuid
import pypdf
from typing import Dict, Any, Tuple
from google import genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 8 and "Replace" not in GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini Client in pdf_parser: {e}")

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
    """Uses Gemini 2.5 Flash to extract clean, structured metadata from first 2 pages of paper text."""
    default_metadata = {
        "title": "Unknown Title",
        "authors": "Unknown Authors",
        "journal": "Unknown Journal/Conference",
        "year": 2026,
        "abstract": "No abstract extracted."
    }

    if not GEMINI_API_KEY or len(GEMINI_API_KEY) < 10 or "Replace" in GEMINI_API_KEY:
        print("Gemini API key not configured or invalid. Skipping LLM-based metadata extraction.")
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
        if not client:
            print("Gemini Client not initialized in pdf_parser. Returning default placeholders.")
            return default_metadata
        # We try gemini-2.5-flash, and fallback to gemini-1.5-flash or gemini-pro if needed
        model_name = "gemini-2.5-flash"
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt
            )
        except Exception as e:
            print(f"Failed calling model {model_name}: {e}. Trying gemini-1.5-flash fallback.")
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt
            )

        # Parse JSON
        clean_json_str = response.text.strip()
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
        print(f"Gemini metadata extraction failed: {e}. Returning default placeholders.")
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
