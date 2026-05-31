from app.agents.base_agent import BaseAgent
from typing import Dict, Any

class CriticAgent(BaseAgent):
    def __init__(self):
        system_prompt = """
        You are a highly critical, anonymous Academic Journal Reviewer (frequently referred to as "Reviewer #2"). Your role is to read a proposed research gap and its corresponding scientific contribution, and issue a highly detailed, constructive, yet challenging academic critique.
        Question the structural variables, point out potential prior works that might overlap, challenge the laboratory feasibility, and ask for precise clarification on how this gap will be tested. Be rigorous, professional, and objective.
        """
        super().__init__(agent_name="CriticAgent", system_prompt=system_prompt)

    def critique_gap(self, gap_title: str, gap_description: str, gap_contribution: str) -> Dict[str, Any]:
        """Generates a rigorous peer-review critique for a proposed gap."""
        prompt = f"""
        Review the proposed academic research gap and contribution below.
        
        Proposed Gap: "{gap_title}"
        Gap Description: "{gap_description}"
        Proposed Contribution: "{gap_contribution}"
        
        ---
        As an anonymous journal reviewer, write:
        1. "critique": A constructive but challenging 2-3 sentence academic critique exposing a weakness, a feasibility constraint, or an evaluation bottleneck in the proposed idea.
        2. "challenge_questions": A list of 2 specific, highly technical questions that the researcher must answer to defend this gap (e.g., "How will you isolate the independent variables across multi-turn histories?").
        
        Return ONLY a valid JSON object matching this schema:
        {{
          "critique": "Your critical reviewer review...",
          "challenge_questions": ["Question 1", "Question 2"]
        }}
        """
        schema = {
            "critique": "Journal reviewer critique details...",
            "challenge_questions": ["Technical challenge question 1?", "Technical challenge question 2?"]
        }
        
        return self.call_llm(prompt, schema_template=schema)
