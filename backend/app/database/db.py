import os
import json
import urllib.request
import urllib.parse
from datetime import datetime
from typing import List, Optional
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv

# Import local schemas and models
from app.database.models import Base, ResearchSession, Paper, PaperMetadata, SessionResponse, GapItem, HypothesisItem, ExperimentItem, ReportResponse, ContradictionItem, TrendForecast, PatentOpportunity, BenchmarkScores

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")

# Local SQLite configuration
DB_FILE = "scholarmind.db"
DATABASE_URL = f"sqlite:///{DB_FILE}"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Verify Supabase configuration
supabase_active = False
if SUPABASE_URL and SUPABASE_KEY and len(SUPABASE_URL.strip()) > 0 and len(SUPABASE_KEY.strip()) > 0:
    supabase_active = True
    print("Zero-Config HTTP REST sync enabled for Supabase database.")

def init_db():
    """Initializes local SQLite database tables and executes migrations if columns are missing."""
    Base.metadata.create_all(bind=engine)
    print("Database tables initialized locally.")
    
    # Self-healing migration for SQLite columns
    import sqlite3
    try:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        
        # Check current columns in research_sessions
        cursor.execute("PRAGMA table_info(research_sessions)")
        columns = [col[1] for col in cursor.fetchall()]
        
        new_cols = {
            "contradictions": "TEXT DEFAULT '[]'",
            "trends": "TEXT DEFAULT '{}'",
            "copilot_history": "TEXT DEFAULT '[]'",
            "benchmarks": "TEXT DEFAULT '{}'",
            "patents": "TEXT DEFAULT '[]'",
            "debate_transcript": "TEXT DEFAULT '[]'"
        }
        
        for col, col_def in new_cols.items():
            if col not in columns:
                print(f"Migration: Adding column '{col}' to research_sessions table...")
                cursor.execute(f"ALTER TABLE research_sessions ADD COLUMN {col} {col_def}")
                
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Self-healing database migration warning: {e}")

def is_supabase_active() -> bool:
    return supabase_active

# ==========================================
# Zero-Dependency Supabase HTTP REST Client
# ==========================================

def make_supabase_rest_request(method: str, path: str, body: dict = None) -> list:
    """Executes a direct PostgREST request to Supabase using python's built-in urllib."""
    if not is_supabase_active():
        return []

    # Clean URL format
    base_url = SUPABASE_URL.rstrip('/')
    url = f"{base_url}/rest/v1/{path}"
    
    headers = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "Prefer": "return=representation"
    }
    
    data = None
    if body:
        data = json.dumps(body).encode("utf-8")
        
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as response:
            res_bytes = response.read()
            if res_bytes:
                return json.loads(res_bytes.decode("utf-8"))
            return []
    except Exception as e:
        print(f"Supabase REST error ({method} {path}): {e}")
        raise e

# ==========================================
# Session Management operations
# ==========================================

def get_session(session_id: str) -> Optional[SessionResponse]:
    """Retrieves a research session by ID."""
    if is_supabase_active():
        try:
            res = make_supabase_rest_request("GET", f"research_sessions?id=eq.{session_id}")
            if res and len(res) > 0:
                data = res[0]
                papers = json.loads(data.get("papers", "[]"))
                gaps = json.loads(data.get("gaps", "[]"))
                hypotheses = json.loads(data.get("hypotheses", "[]"))
                experiments = json.loads(data.get("experiments", "[]"))
                reports = json.loads(data.get("reports", "{}"))
                
                return SessionResponse(
                    id=data["id"],
                    topic=data["topic"],
                    timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
                    papers=papers,
                    gaps=gaps,
                    hypotheses=hypotheses,
                    experiments=experiments,
                    reports=ReportResponse(**reports)
                )
        except Exception as e:
            print(f"Supabase GET failed: {e}. Falling back to SQLite.")

    # SQLite Fallback
    db = SessionLocal()
    try:
        db_sess = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if db_sess:
            return SessionResponse(
                id=db_sess.id,
                topic=db_sess.topic,
                timestamp=db_sess.timestamp,
                papers=[PaperMetadata(**p) for p in json.loads(db_sess.papers or "[]")],
                gaps=[GapItem(**g) for g in json.loads(db_sess.gaps or "[]")],
                hypotheses=[HypothesisItem(**h) for h in json.loads(db_sess.hypotheses or "[]")],
                experiments=[ExperimentItem(**e) for e in json.loads(db_sess.experiments or "[]")],
                reports=ReportResponse(**json.loads(db_sess.reports or "{}")),
                contradictions=[ContradictionItem(**c) for c in json.loads(db_sess.contradictions or "[]")],
                trends=TrendForecast(**json.loads(db_sess.trends or "{}")),
                copilot_history=json.loads(db_sess.copilot_history or "[]"),
                benchmarks=BenchmarkScores(**json.loads(db_sess.benchmarks or "{}")),
                patents=[PatentOpportunity(**pat) for pat in json.loads(db_sess.patents or "[]")],
                debate_transcript=json.loads(db_sess.debate_transcript or "[]")
            )
    finally:
        db.close()
    return None


def list_sessions() -> List[SessionResponse]:
    """Lists all active research sessions."""
    if is_supabase_active():
        try:
            res = make_supabase_rest_request("GET", "research_sessions?order=timestamp.desc")
            if res:
                sessions = []
                for data in res:
                    papers = json.loads(data.get("papers", "[]"))
                    gaps = json.loads(data.get("gaps", "[]"))
                    hypotheses = json.loads(data.get("hypotheses", "[]"))
                    experiments = json.loads(data.get("experiments", "[]"))
                    reports = json.loads(data.get("reports", "{}"))
                    sessions.append(SessionResponse(
                        id=data["id"],
                        topic=data["topic"],
                        timestamp=datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00")),
                        papers=papers,
                        gaps=gaps,
                        hypotheses=hypotheses,
                        experiments=experiments,
                        reports=ReportResponse(**reports)
                    ))
                return sessions
        except Exception as e:
            print(f"Supabase LIST failed: {e}. Falling back to SQLite.")

    # SQLite Fallback
    db = SessionLocal()
    try:
        db_sessions = db.query(ResearchSession).order_by(ResearchSession.timestamp.desc()).all()
        result = []
        for s in db_sessions:
            result.append(SessionResponse(
                id=s.id,
                topic=s.topic,
                timestamp=s.timestamp,
                papers=[PaperMetadata(**p) for p in json.loads(s.papers or "[]")],
                gaps=[GapItem(**g) for g in json.loads(s.gaps or "[]")],
                hypotheses=[HypothesisItem(**h) for h in json.loads(s.hypotheses or "[]")],
                experiments=[ExperimentItem(**e) for e in json.loads(s.experiments or "[]")],
                reports=ReportResponse(**json.loads(s.reports or "{}")),
                contradictions=[ContradictionItem(**c) for c in json.loads(s.contradictions or "[]")],
                trends=TrendForecast(**json.loads(s.trends or "{}")),
                copilot_history=json.loads(s.copilot_history or "[]"),
                benchmarks=BenchmarkScores(**json.loads(s.benchmarks or "{}")),
                patents=[PatentOpportunity(**pat) for pat in json.loads(s.patents or "[]")],
                debate_transcript=json.loads(s.debate_transcript or "[]")
            ))
        return result
    finally:
        db.close()


def save_session(session: SessionResponse) -> SessionResponse:
    """Creates or updates a research session."""
    serialized_papers = json.dumps([p.dict() for p in session.papers])
    serialized_gaps = json.dumps([g.dict() for g in session.gaps])
    serialized_hypotheses = json.dumps([h.dict() for h in session.hypotheses])
    serialized_experiments = json.dumps([e.dict() for e in session.experiments])
    serialized_reports = json.dumps(session.reports.dict())
    
    serialized_contradictions = json.dumps([c.dict() for c in session.contradictions])
    serialized_trends = json.dumps(session.trends.dict() if session.trends else {})
    serialized_copilot = json.dumps(session.copilot_history)
    serialized_benchmarks = json.dumps(session.benchmarks.dict() if session.benchmarks else {})
    serialized_patents = json.dumps([pat.dict() for pat in session.patents])
    serialized_debate = json.dumps(session.debate_transcript)

    if is_supabase_active():
        try:
            payload = {
                "id": session.id,
                "topic": session.topic,
                "timestamp": session.timestamp.isoformat(),
                "papers": serialized_papers,
                "gaps": serialized_gaps,
                "hypotheses": serialized_hypotheses,
                "experiments": serialized_experiments,
                "reports": serialized_reports,
                "contradictions": serialized_contradictions,
                "trends": serialized_trends,
                "copilot_history": serialized_copilot,
                "benchmarks": serialized_benchmarks,
                "patents": serialized_patents,
                "debate_transcript": serialized_debate
            }
            # Bulletproof Upsert Pattern: try POSTing, if duplicate conflict, issue a PATCH update!
            try:
                make_supabase_rest_request("POST", "research_sessions", body=payload)
            except Exception as pe:
                make_supabase_rest_request("PATCH", f"research_sessions?id=eq.{session.id}", body=payload)
            return session
        except Exception as e:
            print(f"Supabase REST SAVE failed: {e}. Syncing locally to SQLite.")

    # SQLite Fallback
    db = SessionLocal()
    try:
        db_sess = db.query(ResearchSession).filter(ResearchSession.id == session.id).first()
        if not db_sess:
            db_sess = ResearchSession(
                id=session.id,
                topic=session.topic,
                timestamp=session.timestamp,
                papers=serialized_papers,
                gaps=serialized_gaps,
                hypotheses=serialized_hypotheses,
                experiments=serialized_experiments,
                reports=serialized_reports,
                contradictions=serialized_contradictions,
                trends=serialized_trends,
                copilot_history=serialized_copilot,
                benchmarks=serialized_benchmarks,
                patents=serialized_patents,
                debate_transcript=serialized_debate
            )
            db.add(db_sess)
        else:
            db_sess.topic = session.topic
            db_sess.papers = serialized_papers
            db_sess.gaps = serialized_gaps
            db_sess.hypotheses = serialized_hypotheses
            db_sess.experiments = serialized_experiments
            db_sess.reports = serialized_reports
            db_sess.contradictions = serialized_contradictions
            db_sess.trends = serialized_trends
            db_sess.copilot_history = serialized_copilot
            db_sess.benchmarks = serialized_benchmarks
            db_sess.patents = serialized_patents
            db_sess.debate_transcript = serialized_debate
        db.commit()
        return session
    finally:
        db.close()


def delete_session(session_id: str) -> bool:
    """Deletes a session and its associated papers."""
    if is_supabase_active():
        try:
            make_supabase_rest_request("DELETE", f"research_sessions?id=eq.{session_id}")
            return True
        except Exception as e:
            print(f"Supabase REST DELETE failed: {e}. Deleting from SQLite.")

    # SQLite
    db = SessionLocal()
    try:
        db_sess = db.query(ResearchSession).filter(ResearchSession.id == session_id).first()
        if db_sess:
            db.delete(db_sess)
            db.commit()
            return True
        return False
    finally:
        db.close()


# ==========================================
# Paper Management operations
# ==========================================

def get_paper_content(paper_id: str) -> Optional[str]:
    """Retrieves parsed text content for a paper."""
    if is_supabase_active():
        try:
            res = make_supabase_rest_request("GET", f"papers?id=eq.{paper_id}")
            if res and len(res) > 0:
                return res[0]["parsed_text"]
        except Exception as e:
            print(f"Supabase GET paper content failed: {e}. Falling back to SQLite.")

    # SQLite
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if paper:
            return paper.parsed_text
    finally:
        db.close()
    return None


def save_paper(session_id: str, paper_id: str, title: str, authors: str, journal: str, year: int, abstract: str, file_path: str, parsed_text: str):
    """Saves raw text and metadata of a paper."""
    if is_supabase_active():
        try:
            payload = {
                "id": paper_id,
                "session_id": session_id,
                "title": title,
                "authors": authors,
                "journal": journal,
                "year": year,
                "abstract": abstract,
                "file_path": file_path,
                "parsed_text": parsed_text
            }
            try:
                make_supabase_rest_request("POST", "papers", body=payload)
            except Exception as pe:
                make_supabase_rest_request("PATCH", f"papers?id=eq.{paper_id}", body=payload)
        except Exception as e:
            print(f"Supabase REST save paper failed: {e}. Syncing locally to SQLite.")

    # SQLite
    db = SessionLocal()
    try:
        paper = db.query(Paper).filter(Paper.id == paper_id).first()
        if not paper:
            paper = Paper(
                id=paper_id,
                session_id=session_id,
                title=title,
                authors=authors,
                journal=journal,
                year=year,
                abstract=abstract,
                file_path=file_path,
                parsed_text=parsed_text
            )
            db.add(paper)
        else:
            paper.title = title
            paper.authors = authors
            paper.journal = journal
            paper.year = year
            paper.abstract = abstract
            paper.file_path = file_path
            paper.parsed_text = parsed_text
        db.commit()
    finally:
        db.close()
