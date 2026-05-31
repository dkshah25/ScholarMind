from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class ResearchAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
You are an elite, highly detailed Academic Research Ingestion Agent. Your role is to read parsed paper text, analyze its structured layout, extract the exact scientific contributions, and create a comprehensive academic summary.
Be rigorous, precise, and objective. Avoid high-level generalizations; identify the exact models, mathematics, datasets, or theoretical findings described in the text.
"""
        super().__init__(agent_name="ResearchAgent", system_prompt=system_prompt)

    def summarize_paper(self, paper_title: str, text: str) -> Dict[str, Any]:
        """Summarizes the paper text and identifies contributions."""
        prompt = f"""
Analyze this academic research paper text and extract key structural summaries.

Paper Title: {paper_title}

Parsed Content excerpt:
{text[:15000]}

---
Provide:
1. "problem_statement": The exact scientific/engineering bottleneck the paper addresses.
2. "proposed_methodology": Algorithmic, architectural, mathematical, or empirical details of their solution.
3. "key_findings": Quantitative and qualitative results achieved.
4. "contributions": A list of unique contributions (e.g. new dataset, new optimizer, theorem proof).
5. "confidence_score": (Integer between 0 and 100) How confident you are in this summary based on text coverage.
6. "rationale": Reasoning for the confidence score (e.g. text was complete, sections were clear).
"""
        schema = {
            "problem_statement": "string describing the research question or bottleneck",
            "proposed_methodology": "string describing the technical implementation",
            "key_findings": "string describing experimental outcomes",
            "contributions": ["contribution item 1", "contribution item 2"],
            "confidence_score": 85,
            "rationale": "Reasoning for summary completeness..."
        }
        
        return self.call_llm(prompt, schema_template=schema)
