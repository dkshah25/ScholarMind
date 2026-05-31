import uuid
from datetime import datetime
from typing import List
from fastapi import APIRouter, HTTPException
from app.database.models import SessionCreate, SessionResponse, ReportResponse
import app.database.db as db

router = APIRouter(prefix="/sessions", tags=["Sessions"])

@router.get("", response_model=List[SessionResponse])
def get_all_sessions():
    """Lists all active research sessions."""
    try:
        return db.list_sessions()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}", response_model=SessionResponse)
def get_session_by_id(session_id: str):
    """Retrieves metadata and workspace memory of a session."""
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.post("/create", response_model=SessionResponse)
def create_new_session(payload: SessionCreate):
    """Initializes a new research workspace session with a specific topic."""
    session_id = str(uuid.uuid4())[:8] # Short clean session id
    new_sess = SessionResponse(
        id=session_id,
        topic=payload.topic,
        timestamp=datetime.utcnow(),
        papers=[],
        gaps=[],
        hypotheses=[],
        experiments=[],
        reports=ReportResponse()
    )
    try:
        db.save_session(new_sess)
        return new_sess
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.delete("/{session_id}")
def delete_existing_session(session_id: str):
    """Cleans up a session and deletes its vector models."""
    success = db.delete_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
        
    # Clean up associated vector indices dynamically
    try:
        from app.services.vector_store import delete_session_vectors
        delete_session_vectors(session_id)
    except Exception as e:
        print(f"Failed cleaning session vector collection: {e}")
        
    # Also clean up layout cache if present
    import os
    if os.path.exists(f"session_graph_{session_id}.json"):
        try:
            os.remove(f"session_graph_{session_id}.json")
        except:
            pass
            
    return {"message": "Session deleted successfully"}

@router.get("/paper/{paper_id}")
def get_paper_parsed_text(paper_id: str):
    """Retrieves full parsed text content for a paper from the database."""
    content = db.get_paper_content(paper_id)
    if not content:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"parsed_text": content}

from pydantic import BaseModel
class CopilotRequest(BaseModel):
    session_id: str
    message: str

@router.post("/copilot")
def run_copilot_assistant(payload: CopilotRequest):
    """Connected conversational chat co-pilot querying paper context and SQLite memories."""
    session = db.get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    papers_context = "\n".join([f"- Title: {p.title}\n  Abstract: {p.abstract}" for p in session.papers])
    gaps_context = "\n".join([f"- Gap: {g.title}\n  Description: {g.description}" for g in session.gaps])
    hypotheses_context = "\n".join([f"- Hypothesis: {h.statement}\n  Rationale: {h.rationale}" for h in session.hypotheses])
    
    system_prompt = f"""
    You are ScholarMind's interactive Research Co-Pilot—a senior AI research advisor, peer reviewer, and scientific strategist.
    You have absolute visibility over the active research workspace:
    
    Topic: "{session.topic}"
    
    Ingested Papers:
    {papers_context}
    
    Discovered Gaps:
    {gaps_context}
    
    Proposed Hypotheses:
    {hypotheses_context}
    
    Answer the researcher's query with extreme technical clarity, rigour, and precision. Maintain a serious, constructive academic tone. Proactively provide citation links or trace arguments where possible.
    """
    
    from app.agents.base_agent import client
    if not client:
        reply = "Copilot engine offline. Please verify GEMINI_API_KEY settings."
    else:
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=payload.message,
                config={"system_instruction": system_prompt}
            )
            reply = response.text
        except Exception as e:
            reply = f"Error calling copilot agent: {str(e)}"
            
    # Save to copilot history in session
    history = session.copilot_history or []
    history.append({"speaker": "user", "message": payload.message, "timestamp": datetime.utcnow().isoformat()})
    history.append({"speaker": "copilot", "message": reply, "timestamp": datetime.utcnow().isoformat()})
    
    session.copilot_history = history
    db.save_session(session)
    
    return {"reply": reply, "history": history}

class NoveltyRequest(BaseModel):
    session_id: str
    concept: str

@router.post("/compare-novelty")
def compare_concept_novelty(payload: NoveltyRequest):
    """Compares custom user proposed concept against indexed reference vector space."""
    session = db.get_session(payload.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
        
    papers_context = "\n".join([f"- Title: {p.title}\n  Abstract: {p.abstract}" for p in session.papers])
    
    prompt = f"""
    As a peer-review editor, critically compare this user-proposed concept against the ingested references in the workspace.
    
    User Concept: "{payload.concept}"
    
    Ingested References:
    {papers_context}
    
    ---
    Calculate the novelty score (float out of 10.0) where:
    - 9.0+ = Completely original paradigm shift.
    - 7.0 - 8.9 = High novel integration of diverse ideas.
    - < 7.0 = Incremental or directly covered in references.
    
    Return a list of closest matching papers, explaining why they are similar, and outline the specific conceptual delta (novel element).
    
    Return ONLY a valid JSON object matching this schema:
    {{
      "novelty_score": 8.4,
      "novelty_rationale": "Deep peer analysis...",
      "closest_papers": ["Citing Paper Title 1", "Citing Paper Title 2"],
      "delta": "Specific novel elements that distinguish this concept from references..."
    }}
    """
    
    from app.agents.base_agent import client
    if not client:
        return {
            "novelty_score": 8.0,
            "novelty_rationale": "LLM offline default novelty review.",
            "closest_papers": [p.title for p in session.papers[:2]],
            "delta": "Simulated novel element."
        }
        
    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config={"response_mime_type": "application/json"}
        )
        import json
        return json.loads(response.text.strip())
    except Exception as e:
        return {
            "novelty_score": 8.0,
            "novelty_rationale": f"Calculated fallback due to API error: {str(e)}",
            "closest_papers": [p.title for p in session.papers[:1]],
            "delta": "Calculated conceptual delta."
        }
