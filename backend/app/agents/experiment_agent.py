from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class ExperimentAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
You are an expert Experimental Physicist and Empirical Computer Scientist. Your role is to take a formal research hypothesis and design a rigorous, publication-grade experimental blueprint to test it.
Your layouts must specify precise variables, control setups, benchmark datasets, baseline methodologies, and mathematical evaluation metrics.
Avoid vague instructions; define exact execution steps.
"""
        super().__init__(agent_name="ExperimentAgent", system_prompt=system_prompt)

    def design_experiment(self, hypothesis_statement: str, hypothesis_rationale: str) -> Dict[str, Any]:
        """Designs a highly structured experimental plan to validate a hypothesis."""
        prompt = f"""
Based on the following formal hypothesis, design an empirical testing blueprint:

Hypothesis Statement: {hypothesis_statement}
Causal Mechanism: {hypothesis_rationale}

---
Analyze and return:
1. "hypothesis_statement": Reference the statement.
2. "title": A professional, technical title for this experimental trial.
3. "variables": A dictionary mapping "independent", "dependent", and "controlled" variables to their exact operational descriptions.
4. "suggested_datasets": List 2-3 specific real-world benchmark datasets or open-source environments suitable for this evaluation.
5. "methodology": A step-by-step sequential list of technical actions (e.g. data preprocessing, baseline model training, parameter sweeps, statistical tests).
6. "evaluation_metrics": A list of exact mathematical metrics to track and validate the outcomes (e.g. MSE, Macro-F1, Latency 95th-percentile, statistical p-values).
7. "confidence_score": (Integer between 0 and 100) Feasibility score of the research design.
"""
        schema = {
            "hypothesis_statement": hypothesis_statement,
            "title": "Empirical Evaluation of [Method] under [Environment]",
            "variables": {
                "independent": "What is manipulated...",
                "dependent": "What is measured...",
                "controlled": "What is kept constant..."
            },
            "suggested_datasets": ["Dataset Name 1 (e.g. GLUE Benchmark)", "Dataset Name 2"],
            "methodology": [
                "Step 1: Set up the virtual environment and fetch the benchmark...",
                "Step 2: Train a standard baseline model..."
            ],
            "evaluation_metrics": ["Metric 1 (e.g. BLEU-4)", "Metric 2"],
            "confidence_score": 85
        }
        
        return self.call_llm(prompt, schema_template=schema)
