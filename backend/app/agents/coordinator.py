import json
import time
from datetime import datetime
from typing import Dict, Any, List, Tuple
from app.database.models import (
    SessionResponse, PaperMetadata, GapItem, HypothesisItem, ExperimentItem, ReportResponse,
    ContradictionItem, TrendForecast, PatentOpportunity, BenchmarkScores
)
import app.database.db as db

# Import individual agents
from app.agents.research_agent import ResearchAgent
from app.agents.literature_agent import LiteratureAgent
from app.agents.gap_agent import GapAgent
from app.agents.hypothesis_agent import HypothesisAgent
from app.agents.experiment_agent import ExperimentAgent
from app.agents.publication_agent import PublicationAgent

# Advanced Upgrades Agents
from app.agents.contradiction_agent import ContradictionAgent
from app.agents.trend_agent import TrendAgent
from app.agents.critic_agent import CriticAgent
from app.agents.quality_agent import QualityAgent

# Import knowledge graph builder
from app.services.knowledge_graph import extract_graph_from_text, calculate_graph_layout

# Initialize agents
research_agent = ResearchAgent()
literature_agent = LiteratureAgent()
gap_agent = GapAgent()
hypothesis_agent = HypothesisAgent()
experiment_agent = ExperimentAgent()
publication_agent = PublicationAgent()

contradiction_agent = ContradictionAgent()
trend_agent = TrendAgent()
critic_agent = CriticAgent()
quality_agent = QualityAgent()

def run_agent_pipeline_for_session(session_id: str) -> SessionResponse:
    """
    Executes the multi-agent dynamic graph on the given research session.
    Fills gaps, hypotheses, experiments, and final reports dynamically.
    """
    session = db.get_session(session_id)
    if not session:
        raise ValueError(f"Session with ID {session_id} not found.")

    if not session.papers:
        # No papers to research, return as is
        print("No papers uploaded in session. Skipping pipeline execution.")
        return session

    print(f"--- Starting Dynamic Agent Graph for session: '{session.topic}' ---")
    
    # -------------------------------------------------------------
    # Step 1: Research Agent (Summarize each paper if not already summarized)
    # -------------------------------------------------------------
    paper_summaries = []
    papers_metadata_list = []
    
    # We will build a unified knowledge graph state representing all nodes/edges
    all_nodes = []
    all_edges = []
    
    for idx_p, paper in enumerate(session.papers):
        parsed_text = db.get_paper_content(paper.id) or ""
        if idx_p > 0:
            time.sleep(1)
        
        # Run Research Agent to get detailed summaries and contributions
        summary_res = research_agent.summarize_paper(paper.title, parsed_text)
        
        paper_summaries.append(summary_res)
        
        # Build PaperMetadata Pydantic object
        paper_meta = PaperMetadata(
            id=paper.id,
            title=paper.title,
            authors=paper.authors,
            journal=paper.journal,
            year=paper.year,
            abstract=summary_res.get("problem_statement", paper.abstract)
        )
        papers_metadata_list.append(paper_meta)
        
        # -------------------------------------------------------------
        # Step 2: Knowledge Graph (Runs in branch parallel with Gap analysis)
        # -------------------------------------------------------------
        print(f"Extracting conceptual entities for paper: '{paper.title}'")
        raw_graph = extract_graph_from_text(paper.title, parsed_text)
        all_nodes.extend(raw_graph.get("nodes", []))
        all_edges.extend(raw_graph.get("edges", []))

    # Save initial metadata changes
    session.papers = papers_metadata_list
    session = db.save_session(session)

    # Save initial metadata changes
    session.papers = papers_metadata_list
    session = db.save_session(session)

    # -------------------------------------------------------------
    # Step 3: Literature Agent, Contradiction Agent & Trend Agent
    # -------------------------------------------------------------
    time.sleep(1)
    print("Executing Literature Synthesis...")
    lit_review = literature_agent.compare_papers(session.topic, paper_summaries)
    
    time.sleep(1)
    print("Executing Contradiction Detection Agent...")
    clash_res = contradiction_agent.detect_contradictions(session.topic, paper_summaries)
    discovered_clashes = []
    for c in clash_res.get("contradictions", []):
        discovered_clashes.append(ContradictionItem(
            papers=c.get("papers", []),
            subject=c.get("subject", "Theoretical disagreement"),
            finding_a=c.get("finding_a", ""),
            finding_b=c.get("finding_b", ""),
            analysis=c.get("analysis", "")
        ))
    session.contradictions = discovered_clashes

    time.sleep(1)
    print("Executing Trend Forecasting Agent...")
    trend_res = trend_agent.forecast_trends(session.topic, paper_summaries)
    session.trends = TrendForecast(
        growth_rate=trend_res.get("growth_rate", "Maturing"),
        emerging_directions=trend_res.get("emerging_directions", []),
        predictions=trend_res.get("predictions", [])
    )
    session = db.save_session(session)

    # -------------------------------------------------------------
    # Step 4: Gap Agent & Peer-Review Debate Mode
    # -------------------------------------------------------------
    time.sleep(1)
    print("Executing Research Gap Discovery (Focal Feature)...")
    gap_res = gap_agent.discover_gaps(session.topic, lit_review, paper_summaries)
    
    discovered_gaps = []
    for g in gap_res.get("gaps", []):
        discovered_gaps.append(GapItem(
            title=g.get("title", "Neglected Area"),
            description=g.get("description", ""),
            contribution=g.get("contribution", ""),
            confidence_score=g.get("confidence_score", 80),
            rationale=g.get("rationale", ""),
            evidence_papers=g.get("evidence_papers", []),
            supporting_passages=g.get("supporting_passages", [])
        ))
    
    session.gaps = discovered_gaps
    session = db.save_session(session)

    # -------------------------------------------------------------
    # Step 4.5: Academic Peer-Review Debate Arena (Researcher vs Reviewer)
    # -------------------------------------------------------------
    primary_debate = []
    if discovered_gaps:
        target_gap = discovered_gaps[0]
        time.sleep(1)
        print(f"Executing Academic Peer-Review Debate Arena on Gap: '{target_gap.title}'...")
        critique_res = critic_agent.critique_gap(
            target_gap.title, 
            target_gap.description, 
            target_gap.contribution
        )
        
        # Turn 1: Reviewer Critique
        primary_debate.append({
            "speaker": "Reviewer Agent",
            "message": critique_res.get("critique", "Is this gap truly unaddressed? Please justify variable controls.")
        })
        for idx, q in enumerate(critique_res.get("challenge_questions", [])):
            primary_debate.append({
                "speaker": "Reviewer Agent",
                "message": f"Technical Query #{idx+1}: {q}"
            })
            
        # Turn 2: Researcher Defense (GapAgent defends the gap)
        prompt_def = f"""
        As a lead researcher, defend your proposed gap against the following peer reviewer critique.
        
        Gap Title: {target_gap.title}
        Reviewer Critique: {critique_res.get('critique')}
        Reviewer Questions: {', '.join(critique_res.get('challenge_questions', []))}
        
        Provide a robust, technically grounded 3-sentence scientific defense.
        """
        time.sleep(1)
        def_res = gap_agent.call_llm(prompt_def)
        primary_debate.append({
            "speaker": "Researcher Agent",
            "message": def_res.get("output_text", f"We defend '{target_gap.title}' by introducing a multi-modal, context-aware semantic space that completely captures the nuances missed by basic sentiment/lexical metrics.")
        })
        session.debate_transcript = primary_debate
        session = db.save_session(session)

    # Add discovered gaps & paper-to-paper edges to Knowledge Graph
    for i, gap in enumerate(discovered_gaps):
        gap_id = f"gap_{i}"
        all_nodes.append({
            "id": gap_id,
            "type": "Limitation", # Map gaps to Limitation node styling in React Flow
            "label": gap.title,
            "summary": gap.description
        })
        # Link root papers to the gaps they exhibit
        for paper in session.papers:
            all_edges.append({
                "id": f"edge_{paper.id}_{gap_id}",
                "source": paper.id,
                "target": gap_id,
                "label": "exhibits_gap"
            })

    # Add paper-to-paper relationship links (contradict / supports)
    for clash in discovered_clashes:
        if len(clash.papers) >= 2:
            p1_id = None
            p2_id = None
            for paper in session.papers:
                if paper.title in clash.papers[0] or clash.papers[0] in paper.title:
                    p1_id = paper.id
                if paper.title in clash.papers[1] or clash.papers[1] in paper.title:
                    p2_id = paper.id
            if p1_id and p2_id:
                all_edges.append({
                    "id": f"edge_clash_{p1_id}_{p2_id}",
                    "source": p1_id,
                    "target": p2_id,
                    "label": "contradicts"
                })

    # Save calculated knowledge graph layout for session persistence
    graph_data = calculate_graph_layout(all_nodes, all_edges)
    with open(f"session_graph_{session_id}.json", "w") as f:
        json.dump(graph_data, f, indent=2)

    # -------------------------------------------------------------
    # Step 5: Hypothesis Agent (Runs on first discovered gap as primary path)
    # -------------------------------------------------------------
    primary_hypothesis = None
    if discovered_gaps:
        target_gap = discovered_gaps[0]
        time.sleep(1)
        print(f"Generating Hypotheses for Gap: '{target_gap.title}' (Novelty Check)...")
        hypo_res = hypothesis_agent.generate_hypothesis(
            target_gap.title, 
            target_gap.description, 
            target_gap.contribution
        )
        
        primary_hypothesis = HypothesisItem(
            gap_title=target_gap.title,
            statement=hypo_res.get("statement", ""),
            rationale=hypo_res.get("rationale", ""),
            novelty_score=hypo_res.get("novelty_score", 8.0),
            novelty_rationale=hypo_res.get("novelty_rationale", ""),
            confidence_score=hypo_res.get("confidence_score", 85),
            citations=hypo_res.get("citations", []),
            lineage=hypo_res.get("lineage", {}),
            suggested_datasets=hypo_res.get("suggested_datasets", []),
            suggested_benchmarks=hypo_res.get("suggested_benchmarks", []),
            suggested_metrics=hypo_res.get("suggested_metrics", []),
            baselines=hypo_res.get("baselines", [])
        )
        
        # Inject real ID mapping into lineage evidence papers if empty
        if primary_hypothesis.lineage and isinstance(primary_hypothesis.lineage, dict) and "evidence_papers" in primary_hypothesis.lineage:
            evidence_papers = primary_hypothesis.lineage["evidence_papers"]
            if isinstance(evidence_papers, list):
                for ep in evidence_papers:
                    if isinstance(ep, dict):
                        if ep.get("paper_id") == "86d23221" and session.papers:
                            ep["paper_id"] = session.papers[0].id
                            ep["title"] = session.papers[0].title
                    
        session.hypotheses = [primary_hypothesis]
        session = db.save_session(session)

    # -------------------------------------------------------------
    # Step 6: Experiment Agent
    # -------------------------------------------------------------
    primary_experiment = None
    if primary_hypothesis:
        time.sleep(1)
        print("Designing Empirical Experiment Blueprint...")
        exp_res = experiment_agent.design_experiment(
            primary_hypothesis.statement, 
            primary_hypothesis.rationale
        )
        
        primary_experiment = ExperimentItem(
            hypothesis_statement=primary_hypothesis.statement,
            title=exp_res.get("title", "Empirical Evaluation Setup"),
            variables=exp_res.get("variables", {}),
            suggested_datasets=primary_hypothesis.suggested_datasets or exp_res.get("suggested_datasets", []),
            methodology=exp_res.get("methodology", []),
            evaluation_metrics=primary_hypothesis.suggested_metrics or exp_res.get("evaluation_metrics", []),
            confidence_score=exp_res.get("confidence_score", 85),
            citations=primary_hypothesis.citations
        )
        session.experiments = [primary_experiment]
        session = db.save_session(session)

    # -------------------------------------------------------------
    # Step 7: Publication Agent
    # -------------------------------------------------------------
    time.sleep(1)
    print("Compiling LaTeX/Markdown Academic Sections...")
    papers_summary_text = "\n".join([
        f"Paper: {p.get('title')}\nProblem: {p.get('problem_statement')}\nMethod: {p.get('proposed_methodology')}" 
        for p in paper_summaries
    ])
    
    time.sleep(1)
    pub_res = publication_agent.write_manuscript_draft(
        topic=session.topic,
        papers_summary=papers_summary_text,
        lit_review=lit_review,
        gaps=[g.dict() for g in discovered_gaps],
        hypothesis=primary_hypothesis.dict() if primary_hypothesis else {},
        experiment=primary_experiment.dict() if primary_experiment else {}
    )
    
    session.reports = ReportResponse(
        abstract=pub_res.get("abstract", ""),
        literature_review=pub_res.get("literature_review", ""),
        methodology=pub_res.get("methodology", ""),
        future_work=pub_res.get("future_work", "")
    )
    session = db.save_session(session)

    # -------------------------------------------------------------
    # Step 8: Research Quality Evaluator & Reproducibility Checker
    # -------------------------------------------------------------
    if primary_hypothesis and primary_experiment:
        time.sleep(1)
        print("Executing Research Quality Evaluator & Reproducibility Auditor...")
        quality_res = quality_agent.evaluate_research(
            topic=session.topic,
            gaps=[g.dict() for g in discovered_gaps],
            hypothesis=primary_hypothesis.dict(),
            experiment=primary_experiment.dict()
        )
        
        session.benchmarks = BenchmarkScores(
            gap_quality=quality_res.get("gap_quality", 85),
            novelty=quality_res.get("novelty", 85),
            scientific_rigor=quality_res.get("scientific_rigor", 85),
            reproducibility=quality_res.get("reproducibility", 85),
            feasibility=quality_res.get("feasibility", 85),
            feedback=quality_res.get("feedback", "Excellent empirical design framework."),
            warnings=quality_res.get("warnings", [])
        )
        session = db.save_session(session)

    print(f"--- Finished Multi-Agent Pipeline for session '{session.topic}' ---")
    return session
