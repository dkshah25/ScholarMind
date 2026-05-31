from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List

class LiteratureAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
You are an expert Literature Synthesis and Citation Agent. Your role is to analyze summaries and vector matches across MULTIPLE academic papers, contrast their technical approaches, identify overlapping paradigms, and compile a rigorous comparative literature review.
Be analytical and critical. Structure comparisons around methodological choices, dataset scopes, and empirical boundaries.
"""
        super().__init__(agent_name="LiteratureAgent", system_prompt=system_prompt)

    def compare_papers(self, topic: str, paper_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compares and contrasts multiple papers based on their metadata and summaries."""
        papers_context = ""
        for i, paper in enumerate(paper_summaries):
            papers_context += f"""
Paper #{i+1}: {paper.get('title', 'Unknown')}
- Authors: {paper.get('authors', 'Unknown')}
- Year: {paper.get('year', 2026)}
- Methodology: {paper.get('proposed_methodology', 'N/A')}
- Findings: {paper.get('key_findings', 'N/A')}
- Contributions: {', '.join(paper.get('contributions', []))}
"""
        
        prompt = f"""
Synthesize and compare these academic publications regarding the topic: "{topic}".

Papers Under Review:
{papers_context}

---
Analyze and return:
1. "comparative_synthesis": A critical analysis contrasting their methodologies and dataset assumptions.
2. "common_themes": Overlapping approaches or general consensus among the authors.
3. "methodological_clashes": Areas where the papers disagree (e.g. model speed vs accuracy, heuristic vs proof).
4. "confidence_score": (Integer between 0 and 100) Confidence in the completeness of comparison.
5. "confidence_rationale": Rationale behind your confidence score.
"""
        schema = {
            "comparative_synthesis": "An analytical comparative essay...",
            "common_themes": ["theme 1", "theme 2"],
            "methodological_clashes": ["clash 1", "clash 2"],
            "confidence_score": 85,
            "confidence_rationale": "Rationale..."
        }
        
        return self.call_llm(prompt, schema_template=schema)
