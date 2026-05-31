from fastapi import APIRouter, HTTPException
from app.database.models import ExperimentItem
import app.database.db as db
from app.agents.experiment_agent import ExperimentAgent

router = APIRouter(prefix="/experiments", tags=["Experiments"])
experiment_agent = ExperimentAgent()

@router.get("/{session_id}")
def get_session_experiments(session_id: str):
    """Retrieves experimental blueprints generated in the session."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.experiments

@router.post("/design")
def request_new_experiment_plan(
    session_id: str, 
    hypothesis_statement: str,
    hypothesis_rationale: str
):
    """
    Manually requests the Experiment Agent to design a new scientific trial 
    to validate a custom hypothesis.
    """
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    print(f"Designing manual experimental plan for hypothesis: {hypothesis_statement[:35]}...")
    try:
        exp_res = experiment_agent.design_experiment(hypothesis_statement, hypothesis_rationale)
        
        new_experiment = ExperimentItem(
            hypothesis_statement=hypothesis_statement,
            title=exp_res.get("title", "Empirical Evaluation Setup"),
            variables=exp_res.get("variables", {}),
            suggested_datasets=exp_res.get("suggested_datasets", []),
            methodology=exp_res.get("methodology", []),
            evaluation_metrics=exp_res.get("evaluation_metrics", []),
            confidence_score=exp_res.get("confidence_score", 85)
        )
        
        session.experiments.append(new_experiment)
        db.save_session(session)
        return new_experiment
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed designing experiment: {str(e)}")
