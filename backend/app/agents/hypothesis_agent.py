from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class HypothesisAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
You are a visionary Academic Architect and Theoretical Synthesizer. Your role is to take a validated research gap and formulate a highly formal, scientifically grounded, and testable research hypothesis.
You must construct the hypothesis around clear causal variables (independent, dependent) and provide a deep logical mechanism.
Additionally, you are responsible for critically self-evaluating the hypothesis and assigning a Novelty Score (0.0 to 10.0) that measures its intellectual and structural distance from established works.
"""
        super().__init__(agent_name="HypothesisAgent", system_prompt=system_prompt)

    def generate_hypothesis(self, gap_title: str, gap_description: str, gap_contribution: str) -> Dict[str, Any]:
        """Generates a formal testable hypothesis and estimates its novelty score."""
        prompt = f"""
Based on the following research gap, formulate a publication-grade testable hypothesis.

Gap Title: {gap_title}
Gap Details: {gap_description}
Proposed Contribution: {gap_contribution}

---
Analyze this gap and return:
1. "gap_title": Reference the gap title.
2. "statement": A clear, formal, mathematical or empirical "If-Then" hypothesis statement (e.g. "If a multi-agent routing model uses predictive queuing, then network throughput increases by over 15% with zero packet drop").
3. "rationale": A detailed logical and physical mechanism explaining the scientific reason why this hypothesis should hold true.
4. "novelty_score": (Float between 0.0 and 10.0) A critical assessment of how novel this hypothesis is compared to standard literature.
   - 9.0+ = Structural paradigm shift (e.g., completely new cooperative framework).
   - 7.0 - 8.9 = High novel integration of diverse concepts (e.g., merging two unrelated mathematical areas).
   - < 7.0 = incremental extension of existing models.
5. "novelty_rationale": A rigorous justification for the novelty score, explaining the conceptual delta from existing works.
6. "confidence_score": (Integer between 0 and 100) Feasibility confidence representing whether this hypothesis can actually be tested in a standard lab environment.
7. "citations": List of exact paper titles cited as foundation for this hypothesis.
8. "suggested_datasets": List of 2 recommended open-source testing datasets to evaluate this hypothesis.
9. "suggested_benchmarks": List of 2 recommended standard evaluation benchmarks (e.g., MMLU, StereoSet, WinoBias).
10. "suggested_metrics": List of 2 recommended mathematical evaluation metrics (e.g., BLEU, Accuracy, Refusal Symmetry).
11. "baselines": List of 2 baseline models to evaluate against (e.g., GPT-4o, Gemini 2.5 Pro).
12. "lineage": A structured traceability dictionary linking this hypothesis back to its supporting gap and findings.

Return ONLY a valid JSON object matching this schema:
{{
  "gap_title": "{gap_title}",
  "statement": "If [independent variable manipulation], then [dependent variable behavior] under [conditions]...",
  "rationale": "Deep theoretical justification based on physical/computational mechanisms...",
  "novelty_score": 8.2,
  "novelty_rationale": "Critique of why this specific causal link has never been tested in this formulation...",
  "confidence_score": 85,
  "citations": ["Paper Citing Title 1"],
  "suggested_datasets": ["Dataset Name 1", "Dataset Name 2"],
  "suggested_benchmarks": ["Benchmark 1", "Benchmark 2"],
  "suggested_metrics": ["Metric 1", "Metric 2"],
  "baselines": ["Model 1", "Model 2"],
  "lineage": {{
    "gap_title": "{gap_title}",
    "supporting_findings": ["Finding description segment 1", "Finding description segment 2"],
    "evidence_papers": [
      {{
        "paper_id": "86d23221",
        "title": "Citing reference paper title",
        "passage": "Specific extracted limitation sentence from paper context..."
      }}
    ]
  }}
}}
"""
        schema = {
            "gap_title": gap_title,
            "statement": "If [independent variable manipulation], then [dependent variable behavior] under [conditions]...",
            "rationale": "Deep theoretical justification based on physical/computational mechanisms...",
            "novelty_score": 8.2,
            "novelty_rationale": "Critique of why this specific causal link has never been tested in this formulation...",
            "confidence_score": 85,
            "citations": [gap_title],
            "suggested_datasets": ["Suggested Dataset 1"],
            "suggested_benchmarks": ["Suggested Benchmark 1"],
            "suggested_metrics": ["Suggested Metric 1"],
            "baselines": ["Baseline Model 1"],
            "lineage": {
                "gap_title": gap_title,
                "supporting_findings": ["Finding statement 1"],
                "evidence_papers": [
                    {
                        "paper_id": "86d23221",
                        "title": "Reference Paper Title",
                        "passage": "Supporting extracted verbatim sentence..."
                    }
                ]
            }
        }
        
        return self.call_llm(prompt, schema_template=schema)
