from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List

class TrendAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are a visionary Academic Forecaster and Technology Trends Analyst. Your mission is to look at a set of academic papers spanning multiple years, evaluate their technological trajectories, and forecast the growth rate, emerging subfields, and predicted 3-5 year future research directions.
        Focus on concrete, futuristic, yet scientifically grounded trends (e.g. projecting agentic workflows, dynamic memory architectures, or self-correcting reasoning loops).
        """
        super().__init__(agent_name="TrendAgent", system_prompt=system_prompt)

    def forecast_trends(self, topic: str, paper_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculates growth trends and future projections for the research topic."""
        papers_text = ""
        for i, paper in enumerate(paper_summaries):
            papers_text += f"""
            Paper #{i+1}: {paper.get('title', 'Unknown')}
            - Year: {paper.get('year', 2026)}
            - Methodology: {paper.get('proposed_methodology', 'N/A')}
            - Unique Contributions: {', '.join(paper.get('contributions', []))}
            """
        
        prompt = f"""
        Analyze the technological trajectory across the following papers on the research topic: "{topic}".
        Calculate the field's momentum, identify the primary growth rate, and project emerging research directions.
        
        Context:
        {papers_text}
        
        ---
        Extract and return:
        1. "growth_rate": Estimated growth trajectory of this specific subfield (e.g., "Exponential Growth", "Rapid Acceleration", "Incremental Steady", "Maturing").
        2. "emerging_directions": A list of 3-4 specific emerging subfields or techniques that are gaining significant momentum across these papers (e.g., "Agentic LLM Orchester", "Socio-linguistic counterfactual alignment").
        3. "predictions": A list of 3 concrete, 3-5 year future research predictions detailing what variables or methods will become the next major research frontiers.
        
        Return ONLY a valid JSON object matching this schema:
        {{
          "growth_rate": "Trajectory summary",
          "emerging_directions": ["Emerging area 1", "Emerging area 2"],
          "predictions": ["Future prediction 1", "Future prediction 2"]
        }}
        """
        schema = {
            "growth_rate": "Growth trajectory rating...",
            "emerging_directions": ["Emerging area 1", "Emerging area 2"],
            "predictions": ["Futuristic prediction 1", "Futuristic prediction 2"]
        }
        
        return self.call_llm(prompt, schema_template=schema)
