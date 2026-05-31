from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List

class GapAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
You are a world-class academic Reviewer and Research Gap Strategist. Your primary mission is to identify profound, non-obvious, and critical research gaps across a collection of scientific papers.
Instead of surface-level or generic claims (like "more data is needed" or "more computing power would help"), you must evaluate structural engineering blind spots, restrictive mathematical assumptions, narrow evaluation conditions, scale thresholds, or unexplored cooperative paradigms.
You must be highly critical, detail-oriented, and logically rigorous.
"""
        super().__init__(agent_name="GapAgent", system_prompt=system_prompt)

    def discover_gaps(self, topic: str, literature_comparison: Dict[str, Any], paper_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Discovers highly robust and sophisticated research gaps across papers."""
        papers_text = ""
        for i, paper in enumerate(paper_summaries):
            papers_text += f"""
Paper #{i+1}: {paper.get('title', 'Unknown')}
- Methodology: {paper.get('proposed_methodology', 'N/A')}
- Findings: {paper.get('key_findings', 'N/A')}
- Unique Contributions: {', '.join(paper.get('contributions', []))}
"""
        
        prompt = f"""
Perform a critical, multi-dimensional review of the following publications on the research topic: "{topic}".
Synthesize their limitations to uncover 3 highly sophisticated, novel research gaps.

Context:
{papers_text}

Comparative Review Context:
{literature_comparison.get('comparative_synthesis', 'N/A')}
Clashes: {', '.join(literature_comparison.get('methodological_clashes', []))}

---
Analyze the technical architecture and experimental limits to propose 3 research gaps. 

For EACH gap, you MUST provide:
1. "title": A short, impactful, academic-grade title (e.g. "Scalability Constraints in Decentralized Multi-Agent Synchronization").
2. "description": A highly rigorous explanation of what exact research question, technical combination, or empirical evaluation is completely neglected in these works.
3. "contribution": A specific potential architectural or theoretical contribution that would fill this gap (e.g. "A lightweight hierarchical consensus mechanism utilizing predictive filtering").
4. "confidence_score": (Integer between 0 and 100) Representing how strongly the literature validates that this gap is genuinely open and neglected (e.g., if all 5 papers make single-agent assumptions, your confidence in the "multi-agent collaborative gap" is high).
5. "rationale": Logical proof citing the papers' specific boundary limits to justify this score.
6. "evidence_papers": List of exact paper titles/names cited in this gap analysis as proof of negligence.
7. "supporting_passages": List of exact, verbatim text paragraphs or sentences extracted from the paper text that support the claim of this limitation.

Return a JSON containing:
- "gaps": List of 3 gap items matching the schema below.
- "overall_analysis": A high-level critique of the state of the art.
"""
        schema = {
            "gaps": [
                {
                    "title": "Title of research gap",
                    "description": "Granular, technical description of the neglected boundary...",
                    "contribution": "Proposed architectural or mathematical design blueprint to resolve it...",
                    "confidence_score": 85,
                    "rationale": "Logical proof based on Paper #1's dataset limit and Paper #2's model constraints...",
                    "evidence_papers": ["Citing Paper Title 1", "Citing Paper Title 2"],
                    "supporting_passages": [" Verbatim sentence extracted from paper text supporting this gap..."]
                }
            ],
            "overall_analysis": "An overarching critique summarizing the architectural paradigms under review..."
        }
        
        return self.call_llm(prompt, schema_template=schema)
