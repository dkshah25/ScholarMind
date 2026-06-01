import sys
import os
import uuid
from datetime import datetime

# Add backend directory to system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import app.database.db as db
from app.database.models import (
    SessionResponse, PaperMetadata, ReportResponse, TrendForecast, BenchmarkScores
)
from app.agents.coordinator import run_agent_pipeline_for_session

def run_pipeline_test():
    print("=== STARTING FULL PIPELINE TEST VIA LOCAL OLLAMA ===")
    
    # 1. Initialize DB and Migration Sanity Check
    db.init_db()
    
    # 2. Create Unique Session
    session_id = str(uuid.uuid4())[:8]
    topic = "Decentralized consensus under communication delays"
    print(f"\n1. Creating test research session: ID={session_id}, Topic='{topic}'")
    
    # Initial SessionResponse structure
    sess_resp = SessionResponse(
        id=session_id,
        topic=topic,
        timestamp=datetime.now(),
        papers=[],
        gaps=[],
        hypotheses=[],
        experiments=[],
        reports=ReportResponse(abstract="", literature_review="", methodology="", future_work=""),
        contradictions=[],
        trends=TrendForecast(growth_rate="Emerging", emerging_directions=[], predictions=[]),
        copilot_history=[],
        benchmarks=BenchmarkScores(datasets=[], benchmarks=[], metrics=[], baselines=[], self_audit_critique=""),
        patents=[],
        debate_transcript=[]
    )
    db.save_session(sess_resp)
    
    # 3. Add Mock Ingested Paper
    paper_id = "paper_decentralized_1"
    paper_title = "Dynamic State Sync in Distributed Networks"
    paper_abstract = "We present an algorithm to achieve consensus in distributed systems suffering from communication delay constraints and node drops. Our empirical trials show linear convergence."
    paper_body = """
    Dynamic State Sync in Distributed Networks.
    By Alice Smith and Bob Jones. Published in Journal of Distributed Systems, 2025.
    
    Abstract:
    We present an algorithm to achieve consensus in distributed systems suffering from communication delay constraints and node drops. Our empirical trials show linear convergence.
    
    Introduction:
    Distributed databases and multi-agent coordination systems depend on consensus algorithms to align state vectors.
    However, conventional consensus loops face high communication delay overhead, leading to synchronization drift.
    
    Methodology:
    We formulate state convergence under variable network latency. Let the state vector be x_i(t).
    We model dynamic updates using delay equations: dx_i/dt = sum_{j} a_ij (x_j(t - tau) - x_i(t)).
    We evaluate the algorithm on standard simulation topologies.
    
    Findings:
    The convergence rate scales linearly with the number of nodes under bounded delay tau < 150ms.
    However, beyond 200ms delay, the state vectors show rapid oscillation and divergent behaviour.
    """
    
    print(f"\n2. Injecting mock parsed paper: ID={paper_id}, Title='{paper_title}'")
    db.save_paper(
        session_id=session_id,
        paper_id=paper_id,
        title=paper_title,
        authors="Alice Smith, Bob Jones",
        journal="Journal of Distributed Systems",
        year=2025,
        abstract=paper_abstract,
        file_path="mock_uploads/paper_decentralized_1.pdf",
        parsed_text=paper_body
    )
    
    # Update session to include paper metadata reference
    paper_meta = PaperMetadata(
        id=paper_id,
        title=paper_title,
        authors="Alice Smith, Bob Jones",
        journal="Journal of Distributed Systems",
        year=2025,
        abstract=paper_abstract
    )
    sess_resp.papers = [paper_meta]
    db.save_session(sess_resp)
    
    # 4. Trigger Multi-Agent Pipeline
    print("\n3. Triggering multi-agent pipeline (runs Research, Literature, Contradiction, Gap, Critique, Hypothesis, Quality, and Experiment Agents sequentially)...")
    try:
        final_session = run_agent_pipeline_for_session(session_id)
        
        print("\n=== PIPELINE EXECUTION SUCCESSFUL ===")
        print(f"Session Topic: {final_session.topic}")
        print(f"Papers Processed: {len(final_session.papers)}")
        print(f"Gaps Discovered: {len(final_session.gaps)}")
        if final_session.gaps:
            print(f" - Gap 1: {final_session.gaps[0].title}")
        print(f"Hypotheses Formulated: {len(final_session.hypotheses)}")
        if final_session.hypotheses:
            print(f" - Hypothesis 1: {final_session.hypotheses[0].statement}")
        print(f"Experiments Recommended: {len(final_session.experiments)}")
        print(f"Contradictions Detected: {len(final_session.contradictions)}")
        print(f"Trend Forecast Directions: {final_session.trends.emerging_directions if final_session.trends else 'None'}")
        print(f"LaTeX Literature Review Generated (first 100 chars): {final_session.reports.literature_review[:100] if final_session.reports else 'None'}...")
        
    except Exception as e:
        print(f"\nERROR: Pipeline execution failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_pipeline_test()
