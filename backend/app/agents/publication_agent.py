from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List
import json

class PublicationAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
You are an elite Academic Copywriter and Academic Editor. Your role is to take all synthesized inputs (summaries, literature reviews, discovered gaps, hypotheses, and experimental blueprints) and draft highly formal, publication-ready academic manuscript sections in standard academic Markdown.
Use formal, precise language (e.g. passive/objective voices, proper formatting). Do NOT include casual remarks or placeholder strings. Output publication-grade text.
"""
        super().__init__(agent_name="PublicationAgent", system_prompt=system_prompt)

    def write_manuscript_draft(
        self, 
        topic: str, 
        papers_summary: str,
        lit_review: Dict[str, Any], 
        gaps: List[Dict[str, Any]], 
        hypothesis: Dict[str, Any], 
        experiment: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generates the publication drafts based on complete session state."""
        prompt = f"""
Compile a publication-ready academic manuscript draft for the research topic: "{topic}".

Inputs:
- Paper Summaries & Methodology Contexts: {papers_summary}
- Synthesized Comparative Literature: {lit_review.get('comparative_synthesis', 'N/A')}
- Identified Critical Gaps: {json.dumps(gaps, indent=2) if isinstance(gaps, list) else str(gaps)}
- Formulated Hypothesis: {hypothesis.get('statement', 'N/A')} (Novelty: {hypothesis.get('novelty_score', 'N/A')}/10)
- Designed Experimental Study: {experiment.get('title', 'N/A')} (Variables: {json.dumps(experiment.get('variables', {}))})

---
You MUST generate 4 separate academic sections and return a JSON matching this schema:
{{
  "abstract": "A 200-word highly compressed, high-impact Abstract summarizing the problem, the open research gap, the proposed methodology, and expected empirical significance.",
  "literature_review": "A detailed, rigorous 2-paragraph Literature Review section contrasting existing works, highlighting common themes, and pinpointing the exact gap in literature.",
  "methodology": "A comprehensive, 2-paragraph Methodology section detailing the formal hypothesis, variables, and step-by-step technical implementation to test the blueprint.",
  "future_work": "A forward-looking paragraph summarizing secondary extensions, dataset scaling, or model configurations for future studies."
}}
Return ONLY valid raw JSON.
"""
        # Python json library import inside prompt for robustness in mock responses
        schema = {
            "abstract": "Abstract content...",
            "literature_review": "Literature Review content...",
            "methodology": "Methodology content...",
            "future_work": "Future Work content..."
        }
        
        return self.call_llm(prompt, schema_template=schema)
