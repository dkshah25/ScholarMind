from app.agents.base_agent import BaseAgent
from typing import Dict, Any, List

class ContradictionAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are a highly critical, detail-oriented Academic Reviewer and Synthesizer. Your primary task is to identify and analyze direct conflicts, competing findings, methodological clashes, or opposing theoretical conclusions across a set of academic papers.
        Avoid high-level or generic claims. Isolate the exact technical parameters, metrics, or variables where the papers disagree (e.g., Paper A states that method X yields higher performance than Y, whereas Paper B proves method Y is superior under constraint Z).
        """
        super().__init__(agent_name="ContradictionAgent", system_prompt=system_prompt)

    def detect_contradictions(self, topic: str, paper_summaries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyzes paper summaries to discover and articulate scientific contradictions."""
        papers_text = ""
        for i, paper in enumerate(paper_summaries):
            papers_text += f"""
            Paper #{i+1}: {paper.get('title', 'Unknown')}
            - Proposed Methodology: {paper.get('proposed_methodology', 'N/A')}
            - Key Findings: {paper.get('key_findings', 'N/A')}
            - Unique Contributions: {', '.join(paper.get('contributions', []))}
            """
        
        prompt = f"""
        Conduct a rigorous cross-examination of the following papers on the research topic: "{topic}".
        Your goal is to identify up to 3 technical contradictions, methodological clashes, or competing empirical results.
        
        Context:
        {papers_text}
        
        ---
        For each contradiction found, return:
        1. "papers": A list of the EXACT paper titles involved in the clash.
        2. "subject": The specific parameter, variable, or claim they clash on (e.g., "Transformer vs CNN efficiency at scale").
        3. "finding_a": The position, metric, or empirical claim asserted in Paper A.
        4. "finding_b": The opposing position, metric, or empirical claim asserted in Paper B.
        5. "analysis": A highly sophisticated, 2-3 sentence technical root-cause analysis explaining WHY this contradiction likely exists (e.g., due to differences in training parameters, evaluation environments, datasets, or structural assumptions).
        
        Provide your response matching this JSON structure:
        {{
          "contradictions": [
            {{
              "papers": ["Paper Title 1", "Paper Title 2"],
              "subject": "Contradiction subject name",
              "finding_a": "Finding details of Paper A...",
              "finding_b": "Opposing finding details of Paper B...",
              "analysis": "Root cause technical analysis..."
            }}
          ]
        }}
        """
        schema = {
            "contradictions": [
                {
                    "papers": ["Paper 1 title", "Paper 2 title"],
                    "subject": "Parameter or claim under clash...",
                    "finding_a": "Finding of first paper...",
                    "finding_b": "Conflicting finding of second paper...",
                    "analysis": "Granular technical analysis of the clash reasons..."
                }
            ]
        }
        
        return self.call_llm(prompt, schema_template=schema)
