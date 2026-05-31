from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List

class QualityAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are a highly demanding Editor-in-Chief and Scientific Peer-Review Auditor. Your role is to critically evaluate a complete proposed research session blueprint—including the reference literature summaries, identified gaps, formal hypothesis statement, and empirical experimental plan.
        You must grade the work across five strict criteria (Novelty, Scientific Rigor, Feasibility, Reproducibility, and Publication/Patent Potential) and output detailed, constructive feedback.
        Additionally, you act as a Reproducibility Checker, issuing explicit "Reviewer Warnings" if key experimental details (e.g., control variables, dataset specifications, baseline parameters, or evaluation protocols) are missing or poorly defined.
        """
        super().__init__(agent_name="QualityAgent", system_prompt=system_prompt)

    def evaluate_research(self, topic: str, gaps: List[Dict[str, Any]], hypothesis: Dict[str, Any], experiment: Dict[str, Any]) -> Dict[str, Any]:
        """Audits the complete session research quality and variable completeness."""
        
        gaps_text = "\n".join([f"- Gap: {g.get('title')}\n  Details: {g.get('description')}" for g in gaps])
        
        prompt = f"""
        Conduct a comprehensive peer-review audit of this proposed research session.
        
        Research Topic: "{topic}"
        
        Discovered Gaps:
        {gaps_text}
        
        Proposed Hypothesis:
        - Statement: {hypothesis.get('statement')}
        - Rationale: {hypothesis.get('rationale')}
        - Citing citations: {', '.join(hypothesis.get('citations', []))}
        
        Experimental Design:
        - Title: {experiment.get('title')}
        - Variables: {experiment.get('variables', {})}
        - Method: {experiment.get('methodology', [])}
        - Metrics: {experiment.get('evaluation_metrics', [])}
        
        ---
        Evaluate the completeness and grade each metric (as an integer score out of 100):
        1. "gap_quality": Analytical strength and literature negligence validation of the gap.
        2. "novelty": Distance from prior work and integration of non-obvious concepts.
        3. "scientific_rigor": Causal relationship clarity between variables.
        4. "reproducibility": Whether datasets, metrics, and steps are clear enough for another lab to replicate.
        5. "feasibility": Real-world deployment difficulty and computation bounds.
        6. "feedback": A comprehensive, constructive, 3-4 sentence anonymous Editor's feedback review.
        7. "warnings": Issue a list of specific "Reviewer Warnings" if details are missing (e.g., "Missing control variables for baseline models", "Unspecified dataset version details"). If everything is perfectly detailed and complete, return an empty list.
        
        Return ONLY a valid JSON object matching this schema:
        {{
          "gap_quality": 85,
          "novelty": 90,
          "scientific_rigor": 80,
          "reproducibility": 75,
          "feasibility": 85,
          "feedback": "Your comprehensive editor audit feedback here...",
          "warnings": ["Warning 1", "Warning 2"]
        }}
        """
        schema = {
            "gap_quality": 85,
            "novelty": 85,
            "scientific_rigor": 85,
            "reproducibility": 85,
            "feasibility": 85,
            "feedback": "Detailed editor-in-chief evaluation audit...",
            "warnings": ["Critical reviewer warning item 1", "Critical reviewer warning item 2"]
        }
        
        return self.call_llm(prompt, schema_template=schema)
