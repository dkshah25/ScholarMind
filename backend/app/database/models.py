from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, Text, DateTime, Integer, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# ==========================================
# SQLAlchemy Models for local SQLite / Postgres
# ==========================================

class ResearchSession(Base):
    __tablename__ = "research_sessions"

    id = Column(String, primary_key=True, index=True)
    topic = Column(String, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Store dynamic JSON content as Text for maximum SQLite compatibility, 
    # and map to Python structures.
    papers = Column(Text, default="[]")       # Serialized List of PaperMetadata dicts
    gaps = Column(Text, default="[]")         # Serialized List of Gap items
    hypotheses = Column(Text, default="[]")   # Serialized List of Hypothesis items
    experiments = Column(Text, default="[]")  # Serialized List of Experiment items
    reports = Column(Text, default="{}")      # Serialized Dict of generated sections (Abstract, Lit Review, etc.)
    
    # Advanced Research Intelligence Columns
    contradictions = Column(Text, default="[]")     # Serialized List of ContradictionItem dicts
    trends = Column(Text, default="{}")              # Serialized TrendForecast dict
    copilot_history = Column(Text, default="[]")     # Serialized List of chat message dicts
    benchmarks = Column(Text, default="{}")          # Serialized BenchmarkScores dict
    patents = Column(Text, default="[]")             # Serialized List of PatentOpportunity dicts
    debate_transcript = Column(Text, default="[]")   # Serialized List of debate transcript dialogs

    paper_relations = relationship("Paper", back_populates="session", cascade="all, delete-orphan")


class Paper(Base):
    __tablename__ = "papers"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String, ForeignKey("research_sessions.id", ondelete="CASCADE"), nullable=False)
    title = Column(String, nullable=True)
    authors = Column(String, nullable=True)
    journal = Column(String, nullable=True)
    year = Column(Integer, nullable=True)
    abstract = Column(Text, nullable=True)
    file_path = Column(String, nullable=True)
    parsed_text = Column(Text, nullable=True)

    session = relationship("ResearchSession", back_populates="paper_relations")


# ==========================================
# Pydantic Schemas for API Serialization
# ==========================================

class PaperMetadata(BaseModel):
    id: str
    title: str
    authors: str
    journal: str
    year: int
    abstract: str
    file_path: Optional[str] = None

class PaperCreate(BaseModel):
    title: Optional[str] = None
    authors: Optional[str] = None
    journal: Optional[str] = None
    year: Optional[int] = None
    abstract: Optional[str] = None
    parsed_text: str

class GapItem(BaseModel):
    title: str = Field(..., description="Short descriptive title of the research gap")
    description: str = Field(..., description="Elaborate description of the missing research domain")
    contribution: str = Field(..., description="Proposed potential contribution to fill this gap")
    confidence_score: int = Field(..., ge=0, le=100, description="Confidence score in the gap existence (0-100)")
    rationale: str = Field(..., description="Reasoning behind this gap and why it is neglected")
    evidence_papers: List[str] = Field(default_factory=list, description="IDs of cited reference papers backing this gap")
    supporting_passages: List[str] = Field(default_factory=list, description="Exact verifying sentence segments extracted from text")

class HypothesisItem(BaseModel):
    gap_title: str = Field(..., description="The title of the gap this hypothesis addresses")
    statement: str = Field(..., description="Formal testable hypothesis statement")
    rationale: str = Field(..., description="Logical mechanism and scientific rationale")
    novelty_score: float = Field(..., ge=0.0, le=10.0, description="Estimated novelty score (0-10)")
    novelty_rationale: str = Field(..., description="Gemini evaluation of why this hypothesis is novel")
    confidence_score: int = Field(..., ge=0, le=100, description="Feasibility and consistency confidence score")
    citations: List[str] = Field(default_factory=list, description="Cited paper IDs or metadata strings")
    lineage: Dict[str, Any] = Field(default_factory=dict, description="Structured traceability lineage from Hypothesis back to Source Papers")
    suggested_datasets: List[str] = Field(default_factory=list, description="Recommended testing datasets")
    suggested_benchmarks: List[str] = Field(default_factory=list, description="Recommended benchmarks")
    suggested_metrics: List[str] = Field(default_factory=list, description="Recommended evaluation metrics")
    baselines: List[str] = Field(default_factory=list, description="Baseline models to evaluate against")

class ExperimentItem(BaseModel):
    hypothesis_statement: str = Field(..., description="The hypothesis being tested")
    title: str = Field(..., description="Experiment plan title")
    variables: Dict[str, str] = Field(..., description="Independent, dependent, and control variables")
    suggested_datasets: List[str] = Field(..., description="Names/links of recommended benchmarks or open-source datasets")
    methodology: List[str] = Field(..., description="Step-by-step sequence of empirical execution")
    evaluation_metrics: List[str] = Field(..., description="Metrics to validate the outcomes (e.g. Accuracy, F1, Latency)")
    confidence_score: int = Field(..., ge=0, le=100, description="Score of design soundness and clarity")
    citations: List[str] = Field(default_factory=list, description="Cited paper IDs or metadata strings")

class ContradictionItem(BaseModel):
    papers: List[str] = Field(default_factory=list, description="IDs or titles of conflicting papers")
    subject: str = Field(..., description="Subject of technical contradiction")
    finding_a: str = Field(..., description="Finding/position of Paper A")
    finding_b: str = Field(..., description="Finding/position of Paper B")
    analysis: str = Field(..., description="Granular analytical reason behind the clash")

class TrendForecast(BaseModel):
    growth_rate: str = Field("", description="Estimated trajectory growth rate")
    emerging_directions: List[str] = Field(default_factory=list, description="Key emerging subfields")
    predictions: List[str] = Field(default_factory=list, description="Emerging future research projections")

class PatentOpportunity(BaseModel):
    novel_element: str = Field(..., description="Novel patentable element")
    commercial_potential: str = Field(..., description="Commercial market viability details")
    implementation_path: str = Field(..., description="Implementation blueprint path")

class BenchmarkScores(BaseModel):
    gap_quality: int = Field(0, description="Gap Quality score (0-100)")
    novelty: int = Field(0, description="Hypothesis Novelty score (0-100)")
    scientific_rigor: int = Field(0, description="Scientific Rigor score (0-100)")
    reproducibility: int = Field(0, description="Reproducibility score (0-100)")
    feasibility: int = Field(0, description="Feasibility and readiness score (0-100)")
    feedback: str = Field("", description="Benchmarking qualitative audit review")
    warnings: List[str] = Field(default_factory=list, description="Reproducibility warnings from reviewer checker")

class ReportResponse(BaseModel):
    abstract: str = ""
    literature_review: str = ""
    methodology: str = ""
    future_work: str = ""

class SessionCreate(BaseModel):
    topic: str

class SessionResponse(BaseModel):
    id: str
    topic: str
    timestamp: datetime
    papers: List[PaperMetadata] = []
    gaps: List[GapItem] = []
    hypotheses: List[HypothesisItem] = []
    experiments: List[ExperimentItem] = []
    reports: ReportResponse = Field(default_factory=ReportResponse)
    
    # Advanced Research Upgrades
    contradictions: List[ContradictionItem] = []
    trends: Optional[TrendForecast] = Field(default_factory=TrendForecast)
    copilot_history: List[Dict[str, Any]] = []
    benchmarks: Optional[BenchmarkScores] = Field(default_factory=BenchmarkScores)
    patents: List[PatentOpportunity] = []
    debate_transcript: List[Dict[str, Any]] = []

    class Config:
        from_attributes = True
