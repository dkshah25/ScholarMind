import os
import json
import re
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
client = None
if GEMINI_API_KEY and len(GEMINI_API_KEY.strip()) > 8 and "Replace" not in GEMINI_API_KEY:
    try:
        client = genai.Client(api_key=GEMINI_API_KEY)
    except Exception as e:
        print(f"Failed to initialize Gemini Client: {e}")

class BaseAgent:
    """Base Agent wrapper providing uniform LLM access, schema parsing, and system rules."""
    
    def __init__(self, agent_name: str, system_prompt: str):
        self.name = agent_name
        self.system_prompt = system_prompt
        self.api_configured = client is not None

    def call_llm(self, prompt: str, schema_template: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Calls Gemini with strict system instructions and schema expectations."""
        if not self.api_configured or client is None:
            # Return dummy stub matching expected fields to avoid crashing when offline
            print(f"[Offline mode] Agent {self.name} returning stub responses.")
            return self._get_offline_stub(schema_template)

        # Enhance prompt with schema instructions if provided
        final_prompt = prompt
        if schema_template:
            final_prompt += f"\n\nIMPORTANT: You must return ONLY a valid JSON object matching this structure:\n{json.dumps(schema_template, indent=2)}\nDo NOT include markdown syntax (like ```json), explanations, or notes. Just return the JSON object."

        try:
            # Use gemini-2.5-pro for high-level reasoning tasks (Gap, Hypothesis, Experiment, Pub)
            model_name = "gemini-2.5-pro"
            try:
                response = client.models.generate_content(
                    model=model_name,
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt
                    )
                )
            except Exception as e:
                print(f"Failed using {model_name}: {e}. Falling back to gemini-2.5-flash.")
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=final_prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=self.system_prompt
                    )
                )

            # Strip possible markdown styling blocks
            clean_text = response.text.strip()
            if clean_text.startswith("```"):
                clean_text = re.sub(r"^```(?:json)?\n", "", clean_text)
                clean_text = re.sub(r"\n```$", "", clean_text)

            try:
                parsed_json = json.loads(clean_text.strip())
                return parsed_json
            except json.JSONDecodeError as je:
                print(f"JSON parsing error for response of {self.name}: {je}. Attempting regex repair.")
                # Basic regex search for JSON block
                json_match = re.search(r"\{.*\}", clean_text, re.DOTALL)
                if json_match:
                    try:
                        return json.loads(json_match.group(0))
                    except:
                        pass
                raise ValueError(f"Failed to parse model output as JSON. Output was: {clean_text}")

        except Exception as e:
            print(f"Agent {self.name} execution failed: {e}. Falling back to stub values.")
            return self._get_offline_stub(schema_template)

    def _get_offline_stub(self, schema_template: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Provides mock data dynamically conforming to the expected JSON schema."""
        if not schema_template:
            return {"output": "LLM offline default output.", "confidence_score": 90}
            
        stub = {}
        for k, v in schema_template.items():
            if isinstance(v, str):
                stub[k] = f"Sample simulated {k} for offline developer trial."
            elif isinstance(v, int):
                stub[k] = 85 if "score" in k or "confidence" in k else 1
            elif isinstance(v, float):
                stub[k] = 8.5
            elif isinstance(v, list):
                if len(v) > 0 and isinstance(v[0], dict):
                    stub[k] = [self._get_offline_stub(v[0])]
                elif len(v) > 0:
                    stub[k] = [self._generate_mock_value(v[0])]
                else:
                    stub[k] = [f"Sample list entry 1", f"Sample list entry 2"]
            elif isinstance(v, dict):
                stub[k] = self._get_offline_stub(v)
            else:
                stub[k] = v
        return stub

    def _generate_mock_value(self, val: Any) -> Any:
        """Helper to generate a mock value based on the type of standard elements."""
        if isinstance(val, str):
            return "Sample simulated string."
        elif isinstance(val, int):
            return 85
        elif isinstance(val, float):
            return 8.5
        elif isinstance(val, list):
            if len(val) > 0:
                return [self._generate_mock_value(val[0])]
            else:
                return ["Sample list entry"]
        elif isinstance(val, dict):
            return {k: self._generate_mock_value(v) for k, v in val.items()}
        else:
            return val
