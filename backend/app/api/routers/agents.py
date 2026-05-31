from fastapi import APIRouter, HTTPException, BackgroundTasks
from app.database.models import SessionResponse
import app.database.db as db
from app.agents.coordinator import run_agent_pipeline_for_session

router = APIRouter(prefix="/agents", tags=["Agents"])

# Dictionary to keep track of active background run states
active_runs = {}

def execute_pipeline_background(session_id: str):
    """Orchestrates pipeline execution in the background to avoid connection timeouts."""
    active_runs[session_id] = "running"
    try:
        run_agent_pipeline_for_session(session_id)
        active_runs[session_id] = "completed"
    except Exception as e:
        print(f"Background pipeline execution failed for session {session_id}: {e}")
        active_runs[session_id] = f"failed: {str(e)}"

@router.post("/run", response_model=SessionResponse)
def trigger_agent_run(
    session_id: str, 
    background_tasks: BackgroundTasks
):
    """
    Triggers the multi-agent dynamic graph pipeline for a session.
    Starts background processing and returns the immediate session state.
    """
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    if not session.papers:
        raise HTTPException(status_code=400, detail="Cannot run agents on an empty session. Please upload papers first.")
        
    # Queue background task to compile literature review, gaps, hypotheses, experiments
    background_tasks.add_task(execute_pipeline_background, session_id)
    
    # Reload and return
    return session

@router.get("/status/{session_id}")
def check_agent_run_status(session_id: str):
    """Checks the live background execution status of a session run."""
    status = active_runs.get(session_id, "idle")
    return {"session_id": session_id, "status": status}
