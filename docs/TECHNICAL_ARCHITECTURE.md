# ScholarMind: Technical Architecture & Implementation Specification

> **Version:** 1.0.0  
> **Classification:** Internal Technical Reference  
> **Audience:** Research Mentors, SCAAI Interviewers, Open-Source Contributors, Technical Reviewers  
> **Last Updated:** June 2026  
> **Author:** Dharmit Shah / SCAAI

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [System Vision](#2-system-vision)
3. [Complete Feature Breakdown](#3-complete-feature-breakdown)
4. [Full Technical Stack](#4-full-technical-stack)
5. [Folder Structure](#5-folder-structure)
6. [Database Architecture](#6-database-architecture)
7. [Agent Architecture](#7-agent-architecture)
8. [Pipeline Orchestration](#8-pipeline-orchestration)
9. [PDF Processing Pipeline](#9-pdf-processing-pipeline)
10. [Knowledge Graph Architecture](#10-knowledge-graph-architecture)
11. [Research Gap Discovery Engine](#11-research-gap-discovery-engine)
12. [Contradiction Detection Engine](#12-contradiction-detection-engine)
13. [Debate Arena](#13-debate-arena)
14. [Novelty Scoring System](#14-novelty-scoring-system)
15. [Experiment Design Engine](#15-experiment-design-engine)
16. [Publication Generation Engine](#16-publication-generation-engine)
17. [Research Lineage System](#17-research-lineage-system)
18. [Research Co-Pilot](#18-research-co-pilot)
19. [API Documentation](#19-api-documentation)
20. [Security Architecture](#20-security-architecture)
21. [Performance Optimizations](#21-performance-optimizations)
22. [Evaluation Framework](#22-evaluation-framework)
23. [Limitations & Technical Debt](#23-limitations--technical-debt)
24. [Future Roadmap](#24-future-roadmap)
25. [Conclusion](#25-conclusion)

---

## 1. Executive Summary

### What ScholarMind Is

ScholarMind is a **Multi-Agent AI Research Operating System** that automates the full academic research intelligence pipeline. It coordinates a network of specialized LLM agents — each owning a discrete research responsibility — to transform raw academic PDFs into structured research intelligence: gaps, hypotheses, experiments, publications, and peer-review simulations.

It is not a chatbot. It is not a summarizer. It is a complete research intelligence compiler that mimics the cognitive workflow of a senior research team.

### Core Objective

To reduce the time from "I have a collection of papers" to "I have a publication-ready research blueprint" from weeks to minutes by automating literature synthesis, gap identification, hypothesis formation, experimental design, and academic writing through coordinated AI agent execution.

### Problems Solved

| Problem | Solution |
|---|---|
| Manually reading 10+ papers and identifying what's missing | Gap Agent performs automated cross-paper gap synthesis |
| Papers contradicting each other with no reconciliation | Contradiction Agent identifies exact parameter-level clashes |
| No structured traceability from hypothesis back to source papers | Research Lineage system provides full traceability chain |
| Hypothesis generation lacks scientific grounding | Hypothesis Agent generates formally structured If-Then hypotheses |
| No peer-review simulation before submission | Debate Arena simulates Reviewer vs Researcher rounds |
| Manual experimental design | Experiment Agent generates complete blueprint with variables and metrics |
| Literature review writing is time-consuming | Publication Agent drafts Abstract, Lit Review, Methodology, Future Work |
| Dependency-heavy vector databases fail in production | Pure-Python Cosine Similarity fallback engine requires zero extra dependencies |
| No persistent workspace across sessions | SQLite + Supabase dual-layer persistence |

### Target Users

- **Graduate Researchers** building literature reviews and hypotheses
- **Research Mentors** evaluating student research blueprints
- **SCAAI (Student Center for AI and Applications Innovation)** — the originating institution
- **Open-source developers** building research tooling on top of the API
- **Technical reviewers** auditing AI pipeline architectures

---

## 2. System Vision

### Why ScholarMind Was Created

Academic research workflows are fundamentally broken in two ways:

1. **Cognitive overload:** Researchers are expected to hold mental maps of 20–50 papers simultaneously, spotting gaps and contradictions manually.
2. **Structural isolation:** Tools like Zotero manage citations; ChatGPT generates text — but nothing *coordinates* these into a living, stateful research environment.

ScholarMind was built at SCAAI to prove that a sufficiently well-architected multi-agent system can serve as a research intelligence layer — not replacing human judgment, but dramatically compressing the time to reach high-quality first drafts.

### Research Workflow Challenges

Traditional research workflow:
```
Paper 1 → read → notes
Paper 2 → read → notes
...
Paper N → read → notes
                    ↓
        Manual synthesis (days)
                    ↓
        Gap identification (weeks)
                    ↓
        Hypothesis formulation (weeks)
                    ↓
        Experiment design (days)
                    ↓
        Writing first draft (weeks)
```

ScholarMind workflow:
```
PDF Upload × N
      ↓
  Multi-Agent Pipeline (minutes)
      ↓
  Gaps + Hypotheses + Experiments + Draft
```

### Multi-Agent Research Intelligence Philosophy

Each agent in ScholarMind owns a single responsibility and has no visibility into other agents' internal state. They communicate exclusively through the shared `SessionResponse` state object, which is persisted to the database after each agent completes. This design follows the **Single Responsibility Principle** at the agent level and the **Shared State Pattern** at the orchestration level.

No agent calls another agent directly. The `coordinator.py` module is the only entity that invokes agents and wires their outputs together — creating a clean, auditable execution graph.

---

## 3. Complete Feature Breakdown

### 3.1 Research Workspace

**Purpose:** The primary operational context for all research activity. Every session has a unique topic string that anchors all downstream agent reasoning.

**Inputs:** User-defined topic string (e.g., "LLM Bias in Medical NLP")

**Outputs:** A `SessionResponse` object with a UUID-based 8-character session ID, persisted to SQLite/Supabase.

**Internal Logic:**
- Session created via `POST /api/sessions/create`
- `session_id = str(uuid.uuid4())[:8]` — intentionally short for UX readability
- Session stored immediately with empty arrays for all fields
- All subsequent operations reference this session ID as the primary key

**Dependencies:** SQLite (local), Supabase (optional cloud sync)

---

### 3.2 Research Sessions

**Purpose:** Encapsulates the full state of a research investigation. A session is the atomic unit of work in ScholarMind.

**Schema (Pydantic `SessionResponse`):**
```python
id: str                          # 8-char UUID
topic: str                       # Research topic string
timestamp: datetime              # Creation timestamp
papers: List[PaperMetadata]      # Ingested reference papers
gaps: List[GapItem]              # Discovered research gaps
hypotheses: List[HypothesisItem] # Generated hypotheses
experiments: List[ExperimentItem] # Experiment blueprints
reports: ReportResponse          # Generated manuscript sections
contradictions: List[ContradictionItem]
trends: TrendForecast
copilot_history: List[Dict]
benchmarks: BenchmarkScores
patents: List[PatentOpportunity]
debate_transcript: List[Dict]
```

**Persistence:** All list and dict fields are JSON-serialized as `TEXT` columns in SQLite. On `save_session()`, the system attempts Supabase upsert (POST → PATCH on conflict), then falls back to SQLite.

---

### 3.3 PDF Ingestion

**Purpose:** Accept academic PDF uploads, extract raw text, parse structured metadata via Gemini, index text chunks in the vector store, and associate the paper with the active session.

**Inputs:**
- `session_id` (form field)
- `file` (PDF binary, multipart upload)

**Outputs:** Updated `SessionResponse` with new `PaperMetadata` appended to `papers` list.

**Internal Logic (6 sequential steps):**
1. Verify session exists in DB
2. Validate file extension is `.pdf` — rejects `.pptx`, `.docx`, etc.
3. Save file to `./uploads/{paper_id}_{filename}` on disk
4. Call `parse_and_ingest_pdf()` — extracts raw text via `pypdf`, then sends first 8,000 characters to Gemini for structured metadata extraction
5. Save paper text + metadata to `papers` table in DB
6. Chunk text (1200 chars, 200 overlap) → generate embeddings → index in ChromaDB or fallback JSON store

**Dependencies:** `pypdf`, Gemini API, ChromaDB (optional), `embeddings.py`, `vector_store.py`

---

### 3.4 Metadata Extraction

**Purpose:** Transform unstructured PDF header text into clean structured fields: title, authors, journal, year, abstract.

**Inputs:** First 8,000 characters of raw PDF text.

**Outputs:**
```json
{
  "title": "Attention Is All You Need",
  "authors": "Vaswani, A., Shazeer, N., ...",
  "journal": "NeurIPS 2017",
  "year": 2017,
  "abstract": "We propose a new simple network architecture..."
}
```

**Internal Logic:**
- Gemini `gemini-2.5-flash` is called with a strict JSON-only extraction prompt
- Markdown stripping regex applied: `re.sub(r"^```(?:json)?\n", "", ...)`
- Year field validated and coerced to `int`
- Missing keys filled with safe defaults (e.g., `"Unknown Title"`)
- If Gemini unavailable: filename used as title, all other fields set to defaults

**Model Fallback Chain:** `gemini-2.5-flash` → `gemini-1.5-flash`

---

### 3.5 Research Agent

**Purpose:** Reads full paper text and produces a structured academic summary covering problem statement, methodology, findings, and unique contributions.

**Inputs:** Paper title + first 15,000 characters of parsed text.

**Outputs:**
```json
{
  "problem_statement": "...",
  "proposed_methodology": "...",
  "key_findings": "...",
  "contributions": ["...", "..."],
  "confidence_score": 85,
  "rationale": "..."
}
```

**Internal Logic:** Single Gemini call with structured schema. The 15,000 character window captures most papers' methods and results sections. Confidence score reflects text coverage quality.

---

### 3.6 Literature Agent

**Purpose:** Performs cross-paper comparative synthesis — identifying common themes, contrasting methodologies, and methodological clashes.

**Inputs:** Topic string + list of all paper summaries (from Research Agent).

**Outputs:**
```json
{
  "comparative_synthesis": "...",
  "methodological_clashes": ["...", "..."],
  "common_themes": ["...", "..."]
}
```

**Internal Logic:** Single Gemini call. Output feeds directly into the Gap Agent as "comparative review context."

---

### 3.7 Contradiction Agent

**Purpose:** Identifies up to 3 technical contradictions, methodological clashes, or competing empirical findings across the ingested paper set.

**Inputs:** Topic string + list of paper summaries.

**Outputs:** List of `ContradictionItem` objects with exact paper titles, clash subject, opposing findings from each paper, and root-cause analysis.

**Internal Logic:**
- Forces Gemini to name exact paper titles involved (not generic labels)
- Requires granular technical root-cause analysis (not "papers disagree")
- Results immediately written to `session.contradictions` and persisted

---

### 3.8 Trend Agent

**Purpose:** Projects research trajectory and emerging directions based on the synthesized literature landscape.

**Inputs:** Topic string + paper summaries.

**Outputs:**
```json
{
  "growth_rate": "Exponential Growth (Emerging Area)",
  "emerging_directions": ["...", "..."],
  "predictions": ["...", "..."]
}
```

---

### 3.9 Gap Agent

**Purpose:** The focal intelligence engine. Identifies 3 profound, non-obvious research gaps by cross-examining limitations across all papers.

**Inputs:** Topic + literature comparison output + paper summaries.

**Outputs:** List of `GapItem` objects. Each gap includes:
- `title`: Academic-grade short title
- `description`: Exact technical explanation of what is neglected
- `contribution`: Specific architectural or theoretical contribution blueprint
- `confidence_score`: 0–100, representing how strongly the literature supports gap existence
- `rationale`: Logical proof citing specific paper boundary limits
- `evidence_papers`: Exact paper titles cited as proof
- `supporting_passages`: Verbatim extracted sentences from papers

**System Prompt Design:** The agent is explicitly instructed to avoid generic gap claims ("more data needed") and must identify structural engineering blind spots, restrictive mathematical assumptions, narrow evaluation conditions, or unexplored cooperative paradigms.

---

### 3.10 Reviewer Agent (CriticAgent)

**Purpose:** Simulates an anonymous "Reviewer #2" academic journal reviewer. Generates a challenging critique and technical challenge questions targeting the primary discovered gap.

**Inputs:** Gap title, description, contribution.

**Outputs:**
```json
{
  "critique": "...",
  "challenge_questions": ["...", "..."]
}
```

**Role in Pipeline:** Called in the Debate Arena phase. Its output forms "Turn 1" of the debate transcript.

---

### 3.11 Debate Arena

**Purpose:** Simulates a 2-turn peer-review debate between the Reviewer Agent (CriticAgent) and the Researcher Agent (GapAgent defending the gap).

**Internal Logic:**
```
Turn 1: CriticAgent → issues critique + 2 challenge questions
Turn 2: GapAgent   → defends gap with 3-sentence scientific defense
```

The defense prompt constructs an inline query asking the GapAgent to rebut the specific critique. The full transcript is stored as `session.debate_transcript`.

**Output Format:**
```json
[
  {"speaker": "Reviewer Agent", "message": "Is this gap truly unaddressed?..."},
  {"speaker": "Reviewer Agent", "message": "Technical Query #1: How will you..."},
  {"speaker": "Researcher Agent", "message": "We defend this gap by..."}
]
```

---

### 3.12 Hypothesis Agent

**Purpose:** Formulates a formal, testable, publication-grade research hypothesis grounded in the primary discovered gap.

**Inputs:** Gap title, description, contribution.

**Outputs:** `HypothesisItem` including:
- Formal If-Then hypothesis statement with independent/dependent variables
- Deep logical rationale
- Novelty score (0.0–10.0)
- Confidence score (0–100)
- Suggested datasets, benchmarks, evaluation metrics, baseline models
- Full lineage dictionary linking hypothesis back to source papers

---

### 3.13 Novelty Scoring

**Purpose:** Assigns a quantified intellectual distance score comparing the hypothesis against the existing literature.

**Scoring Rubric:**
- `9.0+` = Structural paradigm shift (completely new cooperative framework)
- `7.0 – 8.9` = High novel integration of diverse concepts
- `< 7.0` = Incremental extension of existing models

**Novelty Comparison (Co-Pilot):** Users can also submit custom concepts via `POST /api/sessions/compare-novelty` for real-time novelty comparison against the session's indexed reference space.

---

### 3.14 Experiment Agent

**Purpose:** Designs a rigorous, publication-grade empirical testing blueprint to validate the generated hypothesis.

**Inputs:** Hypothesis statement + hypothesis rationale.

**Outputs:** `ExperimentItem` including:
- Title
- Variables dictionary: `{independent, dependent, controlled}`
- 2–3 recommended real-world datasets
- Step-by-step methodology list
- Mathematical evaluation metrics (e.g., BLEU-4, Macro-F1, p-values)
- Confidence score for design soundness

---

### 3.15 Publication Agent

**Purpose:** Compiles all session outputs into 4 formal, publication-ready academic manuscript sections.

**Inputs:** Topic + paper summaries + lit review + gaps + hypothesis + experiment.

**Outputs:** `ReportResponse`:
- `abstract`: 200-word compressed high-impact abstract
- `literature_review`: 2-paragraph rigorous literature review
- `methodology`: 2-paragraph technical methodology section
- `future_work`: Forward-looking extensions paragraph

---

### 3.16 Research Co-Pilot

**Purpose:** A context-aware conversational AI assistant with full visibility into the active session state (papers, gaps, hypotheses).

**Inputs:** `session_id` + user `message`

**Outputs:** Gemini-generated reply + updated `copilot_history` list.

**Internal Logic:**
- Reconstructs context from session state at query time (no pre-indexing)
- System prompt injects full session state (papers, gaps, hypotheses) as context
- Conversation history persisted to `copilot_history` column in DB

---

### 3.17 Knowledge Graph

**Purpose:** Visual, interactive semantic entity graph connecting papers, methods, datasets, findings, limitations, and research gaps.

**Internal Logic:**
- Gemini extracts nodes (typed entities) and directed edges from paper text
- Node IDs are slug-ified from labels: `re.sub(r"\W+", "_", label.lower())[:25]`
- Fuzzy label matching for edge construction (handles minor label mismatches)
- Spiral layout algorithm assigns `(x, y)` coordinates to prevent node overlap
- Gap nodes injected after Gap Agent run, with `exhibits_gap` edges to parent papers
- Contradiction edges (`contradicts`) added between papers with detected clashes
- Stored as `session_graph_{session_id}.json` on disk

---

### 3.18 Research Lineage Explorer

**Purpose:** Provides full traceability from hypothesis back through gap to source papers.

**Structure:**
```
HypothesisItem.lineage = {
  "gap_title": "...",
  "supporting_findings": ["...", "..."],
  "evidence_papers": [
    {
      "paper_id": "86d23221",
      "title": "...",
      "passage": "Verbatim sentence..."
    }
  ]
}
```

The coordinator patches `lineage.evidence_papers` with real paper IDs from the session after hypothesis generation.

---

### 3.19 Benchmark Evaluation Engine (QualityAgent)

**Purpose:** Acts as an automated Editor-in-Chief, grading the complete research session across 5 dimensions.

**Output (`BenchmarkScores`):**
- `gap_quality` (0–100): Analytical strength of gap
- `novelty` (0–100): Distance from prior work
- `scientific_rigor` (0–100): Causal clarity
- `reproducibility` (0–100): Replication feasibility
- `feasibility` (0–100): Practical deployment difficulty
- `feedback`: 3–4 sentence anonymous editor review
- `warnings`: List of specific reproducibility warnings

---

### 3.20 Session Memory & Workspace Persistence

**Purpose:** All session state persists between API calls and browser refreshes.

**Implementation:** Every agent write triggers a `db.save_session()` call which serializes all Pydantic models to JSON and upserts to Supabase (if configured) with SQLite as local fallback.

---

## 4. Full Technical Stack

### Frontend

| Component | Technology | Version |
|---|---|---|
| Framework | Next.js | 16.2.6 |
| Language | TypeScript | ^5 |
| Runtime | React | 19.2.4 |
| Styling | Tailwind CSS | ^4 |
| Animations | Framer Motion | ^12.40.0 |
| Icons | Lucide React | ^1.17.0 |
| Graph Visualization | React Flow (`reactflow`) | ^11.11.4 |
| State Management | React `useState`/`useEffect` (no external store) | — |
| Deployment | Vercel | — |
| Build | `next build` | — |
| Environment | `NEXT_PUBLIC_API_URL` → Render backend URL | — |

**Architecture Note:** The entire frontend is a single-page application in `app/page.tsx` (104KB). All UI state is managed locally via React hooks. There is no Redux, Zustand, or global state library. Navigation between modules (Overview, Research Workspace, Agent Control Center, Knowledge Graph, etc.) is handled by a local `activeModule` state variable.

---

### Backend

| Component | Technology | Version |
|---|---|---|
| Web Framework | FastAPI | 0.111.0 |
| ASGI Server | Uvicorn | 0.30.1 |
| Data Validation | Pydantic | >=2.9.0 |
| ORM | SQLAlchemy | 2.0.31 |
| File Parsing | pypdf | 4.2.0 |
| File Upload | python-multipart | 0.0.9 |
| Environment | python-dotenv | 1.0.1 |
| Vector DB | chromadb | 0.5.3 (optional) |
| Deployment | Render (free tier) | — |

**Installed but not directly exercised in core pipeline:** `langchain==0.2.5`, `langchain-core==0.2.9`, `langchain-google-genai==1.0.6`, `langgraph==0.1.4`. These are present in `requirements.txt` for future orchestration expansion but the current pipeline uses a custom Python coordinator, not LangGraph's graph execution engine.

---

### AI Layer

| Component | Model | Usage |
|---|---|---|
| Primary LLM | `gemini-2.5-flash` | All agent calls |
| Fallback LLM | `gemini-1.5-flash` | Metadata + graph extraction fallback |
| Embedding Model | `gemini-embedding-001` | Document and query embeddings |
| SDK | `google-genai` 2.7.0 | All Gemini API interactions |

**Model Selection Strategy:**
- All agents use `gemini-2.5-flash` as the primary model — chosen for high RPM availability on the free tier and strong instruction-following at JSON schema enforcement.
- Model selection is hardcoded per-agent, not dynamically selected.

**Fallback Strategy (3 levels):**
1. Primary call: `gemini-2.5-flash`
2. Model failure fallback: `gemini-1.5-flash` (only in `pdf_parser.py` and `knowledge_graph.py`)
3. API unavailable fallback: `_get_offline_stub()` — returns schema-conforming mock data

**Prompt Engineering Architecture:**
- System instruction injected via `types.GenerateContentConfig(system_instruction=...)`
- Schema appended to every user prompt: `"You must return ONLY a valid JSON object matching this structure: {json.dumps(schema_template)}"`
- Markdown stripping via regex after response: `re.sub(r"^```(?:json)?\n", "", ...)`
- Regex JSON extraction fallback: `re.search(r"\{.*\}", clean_text, re.DOTALL)`

---

### Database Layer

**Local (Primary):** SQLite via SQLAlchemy ORM
- File: `scholarmind.db`
- Connection: `sqlite:///scholarmind.db` with `check_same_thread=False`
- Auto-migration: `init_db()` runs `PRAGMA table_info` checks and issues `ALTER TABLE ADD COLUMN` for any missing columns

**Cloud (Optional):** Supabase via zero-dependency urllib REST client
- No Supabase Python SDK — uses raw `urllib.request` with PostgREST headers
- Upsert pattern: `POST` → catches duplicate → `PATCH ?id=eq.{id}`
- Falls back to SQLite on any Supabase error

**Persistence Strategy:** Session JSON fields stored as `TEXT` columns, serialized/deserialized on every read/write. Trade-off: simple schema, no complex joins, but full JSON re-parse on every access.

---

### Vector Layer

**Primary:** ChromaDB persistent client
- Collection name: `scholarmind_papers`
- Per-chunk metadata: `{session_id, paper_id, paper_title, chunk_index}`
- Query filtered by `session_id` to isolate session vectors

**Fallback:** Pure-Python Cosine Similarity Engine (no dependencies)
- Storage: `session_vectors_{session_id}.json` flat file
- Format: list of `{id, paper_id, paper_title, chunk_index, document, embedding}` objects
- Search: full linear scan + cosine similarity sort, O(n) per query
- Cosine formula: `dot(v1,v2) / (|v1| * |v2|)` implemented with Python `math.sqrt` and `sum`

**Embedding Model:** `gemini-embedding-001`
- Document task type: `RETRIEVAL_DOCUMENT`
- Query task type: `RETRIEVAL_QUERY`
- Fallback: deterministic pseudo-vectors using `random.seed(hash(text))` + 768-dimensional uniform random floats

**Chunking Parameters:**
- Chunk size: 1,200 characters
- Overlap: 200 characters
- Sentence boundary detection: `rfind(". ")`, `rfind("?\n")`, `rfind(".\n")` — splits at last sentence end past the halfway point

---

### Infrastructure

**Backend Deployment:** Render (free tier)
- Service URL: `https://scholarmind-f319.onrender.com`
- Spin-down: 50+ second cold start after 15 minutes of inactivity (free tier limitation)
- Start command: `uvicorn app.api.main:app --host 0.0.0.0 --port $PORT`
- Web concurrency: 1 worker (free tier default)

**Frontend Deployment:** Vercel
- URL: `https://scholar-mind-dks.vercel.app`
- Environment variable: `NEXT_PUBLIC_API_URL` → Render service URL

**CORS:** Wildcard `allow_origins=["*"]` — suitable for development, must be restricted in production.

---

## 5. Folder Structure

```
scholarmind/
├── .env.example                    # Template for required environment variables
├── .gitignore                      # Excludes .env, __pycache__, .venv, .next
├── LICENSE                         # MIT License
├── README.md                       # User-facing project overview
│
├── backend/                        # FastAPI Python backend
│   ├── .env                        # Local secrets (gitignored)
│   ├── .env.example                # Safe template for deployment setup
│   ├── requirements.txt            # Python package dependencies
│   ├── scholarmind.db              # SQLite database file (runtime artifact)
│   ├── session_graph_{id}.json     # Per-session knowledge graph layout cache
│   ├── session_vectors_{id}.json   # Per-session vector embeddings (fallback mode)
│   ├── uploads/                    # Uploaded PDF files (runtime directory)
│   └── app/
│       ├── __init__.py
│       ├── agents/                 # All LLM agent implementations
│       │   ├── __init__.py
│       │   ├── base_agent.py       # BaseAgent class: LLM calling, JSON parsing, stub fallbacks
│       │   ├── coordinator.py      # Pipeline orchestrator: wires all agents into sequential graph
│       │   ├── research_agent.py   # Summarizes individual paper text
│       │   ├── literature_agent.py # Cross-paper comparative synthesis
│       │   ├── contradiction_agent.py # Inter-paper clash detection
│       │   ├── trend_agent.py      # Research trajectory forecasting
│       │   ├── gap_agent.py        # Core gap discovery engine
│       │   ├── critic_agent.py     # Reviewer #2 simulation for Debate Arena
│       │   ├── hypothesis_agent.py # Formal hypothesis + novelty scoring
│       │   ├── experiment_agent.py # Empirical experiment blueprint generator
│       │   ├── publication_agent.py # Manuscript section drafter
│       │   └── quality_agent.py    # Benchmark evaluation + reproducibility auditor
│       ├── api/
│       │   ├── main.py             # FastAPI application factory, CORS, startup, router mounting
│       │   └── routers/
│       │       ├── agents.py       # POST /run, GET /status — pipeline trigger
│       │       ├── experiments.py  # Experiment-specific routes
│       │       ├── graph.py        # GET /graph/{session_id} — knowledge graph retrieval
│       │       ├── ingest.py       # POST /ingest/upload — PDF ingestion endpoint
│       │       └── sessions.py     # Session CRUD, copilot, novelty comparison
│       ├── database/
│       │   ├── db.py               # All DB operations: get/save/delete session, paper management
│       │   └── models.py           # SQLAlchemy ORM models + Pydantic schemas
│       └── services/
│           ├── embeddings.py       # Gemini embedding-001 calls + deterministic fallback
│           ├── knowledge_graph.py  # Gemini graph extraction + spiral layout algorithm
│           ├── pdf_parser.py       # pypdf text extraction + Gemini metadata parsing
│           └── vector_store.py     # ChromaDB + pure-Python cosine fallback vector engine
│
├── frontend/                       # Next.js TypeScript frontend
│   ├── app/
│   │   ├── globals.css             # Global styles, Tailwind imports
│   │   ├── layout.tsx              # Root layout (metadata, font loading)
│   │   └── page.tsx                # ENTIRE frontend application (single file, ~104KB)
│   ├── components/                 # (Currently empty — all components inline in page.tsx)
│   ├── public/                     # Static assets
│   ├── next.config.ts              # Next.js configuration
│   ├── package.json                # Frontend dependency manifest
│   └── tsconfig.json               # TypeScript compiler options
│
└── docs/
    └── TECHNICAL_ARCHITECTURE.md   # This document
```

---

## 6. Database Architecture

### SQLAlchemy ORM Models

#### `ResearchSession` Table: `research_sessions`

| Column | Type | Default | Description |
|---|---|---|---|
| `id` | String (PK) | — | 8-char UUID session identifier |
| `topic` | String | — | Research topic anchor string |
| `timestamp` | DateTime | `datetime.utcnow` | Creation time |
| `papers` | Text | `"[]"` | JSON-serialized `List[PaperMetadata]` |
| `gaps` | Text | `"[]"` | JSON-serialized `List[GapItem]` |
| `hypotheses` | Text | `"[]"` | JSON-serialized `List[HypothesisItem]` |
| `experiments` | Text | `"[]"` | JSON-serialized `List[ExperimentItem]` |
| `reports` | Text | `"{}"` | JSON-serialized `ReportResponse` |
| `contradictions` | Text | `"[]"` | JSON-serialized `List[ContradictionItem]` |
| `trends` | Text | `"{}"` | JSON-serialized `TrendForecast` |
| `copilot_history` | Text | `"[]"` | JSON-serialized `List[Dict]` chat history |
| `benchmarks` | Text | `"{}"` | JSON-serialized `BenchmarkScores` |
| `patents` | Text | `"[]"` | JSON-serialized `List[PatentOpportunity]` |
| `debate_transcript` | Text | `"[]"` | JSON-serialized debate dialog list |

#### `Paper` Table: `papers`

| Column | Type | Description |
|---|---|---|
| `id` | String (PK) | 8-char UUID |
| `session_id` | String (FK) | References `research_sessions.id` with CASCADE |
| `title` | String | Extracted paper title |
| `authors` | String | Comma-separated authors |
| `journal` | String | Journal/conference name |
| `year` | Integer | Publication year |
| `abstract` | Text | Full abstract |
| `file_path` | String | Disk path of uploaded PDF |
| `parsed_text` | Text | Full raw text extracted from PDF |

---

### Pydantic Schema Examples

#### `GapItem` Example Record:
```json
{
  "title": "Scalability Constraints in Decentralized Multi-Agent Synchronization",
  "description": "No existing work evaluates multi-agent consensus protocols under network partition conditions with more than 8 coordinated agents operating across heterogeneous hardware constraints...",
  "contribution": "A lightweight hierarchical consensus mechanism utilizing predictive filtering and asynchronous state buffering",
  "confidence_score": 87,
  "rationale": "Papers #1 and #3 both restrict evaluations to single-agent pipelines. Paper #2 tests at most 4 agents on homogeneous GPU clusters...",
  "evidence_papers": ["MARL Survey (2024)", "Consensus Protocols for Distributed AI (2023)"],
  "supporting_passages": ["Our experiments were limited to single-agent environments due to coordination overhead..."]
}
```

#### `HypothesisItem` Example Record:
```json
{
  "gap_title": "Scalability Constraints in Decentralized Multi-Agent Synchronization",
  "statement": "If a hierarchical consensus buffer is introduced between coordinating agents, then synchronization latency decreases by over 30% while maintaining >95% state consistency under network partition conditions with N>8 agents",
  "rationale": "Hierarchical buffering reduces direct peer-to-peer message complexity from O(N²) to O(N log N)...",
  "novelty_score": 8.4,
  "novelty_rationale": "No prior work combines hierarchical buffering with predictive state pre-computation in multi-agent LLM systems...",
  "confidence_score": 82,
  "citations": ["MARL Survey (2024)"],
  "suggested_datasets": ["MultiAgent-Bench", "AgentArena"],
  "suggested_benchmarks": ["MMLU", "AgentBench"],
  "suggested_metrics": ["Synchronization Latency (ms)", "State Consistency Rate (%)"],
  "baselines": ["GPT-4o Multi-Agent", "Gemini 2.5 Pro"],
  "lineage": {
    "gap_title": "Scalability Constraints...",
    "supporting_findings": ["Single-agent pipeline bottleneck at 8+ agents"],
    "evidence_papers": [
      {
        "paper_id": "7c9b3bcf",
        "title": "MARL Survey (2024)",
        "passage": "Our system was designed for single-agent evaluation pipelines..."
      }
    ]
  }
}
```

#### `BenchmarkScores` Example Record:
```json
{
  "gap_quality": 88,
  "novelty": 84,
  "scientific_rigor": 79,
  "reproducibility": 72,
  "feasibility": 81,
  "feedback": "The research blueprint demonstrates strong analytical depth with well-sourced gap evidence. The hypothesis is formally structured. However, missing exact dataset version specifications and baseline hyperparameter configurations reduce reproducibility confidence.",
  "warnings": [
    "Dataset version numbers not specified for MultiAgent-Bench",
    "Baseline model hyperparameters undefined"
  ]
}
```

#### `ContradictionItem` Example Record:
```json
{
  "papers": ["Attention Is All You Need", "EfficientNet: Rethinking Model Scaling"],
  "subject": "Computational efficiency vs. accuracy trade-off at scale",
  "finding_a": "Transformer self-attention achieves SOTA accuracy with O(n²) memory complexity, deemed acceptable for the performance gain",
  "finding_b": "Compound scaling with convolutions achieves comparable accuracy with 8.4x fewer parameters and linear memory scaling",
  "analysis": "The contradiction arises from evaluating different task domains: Transformers excel on sequence-to-sequence tasks where global attention is structurally necessary, while EfficientNet demonstrates superiority on fixed-resolution image classification where spatial locality is the dominant inductive bias."
}
```

---

## 7. Agent Architecture

### Architecture Overview

All agents inherit from `BaseAgent` which provides:
- `call_llm(prompt, schema_template)` — unified Gemini call with JSON parsing and stub fallback
- `_get_offline_stub(schema_template)` — recursive schema-conforming mock data generator
- `_generate_mock_value(val)` — type-aware mock value generator for nested structures

```
BaseAgent
├── ResearchAgent       → summarize_paper()
├── LiteratureAgent     → compare_papers()
├── ContradictionAgent  → detect_contradictions()
├── TrendAgent          → forecast_trends()
├── GapAgent            → discover_gaps()
├── CriticAgent         → critique_gap()
├── HypothesisAgent     → generate_hypothesis()
├── ExperimentAgent     → design_experiment()
├── PublicationAgent    → write_manuscript_draft()
└── QualityAgent        → evaluate_research()
```

---

### 7.1 ResearchAgent

**Responsibility:** Individual paper comprehension and structured summarization.

**Prompt Strategy:**
- System: "You are an elite Academic Research Ingestion Agent..."
- User: Paper title + first 15,000 characters
- Schema enforced: `{problem_statement, proposed_methodology, key_findings, contributions[], confidence_score, rationale}`

**Inputs:** `paper_title: str`, `text: str`

**Outputs:** Dict conforming to summarization schema

**State Update:** Results stored in `paper_summaries` list (in-memory during pipeline run); `paper.abstract` updated from `problem_statement`

**Failure Handling:** Falls back to `_get_offline_stub()` with academically-styled placeholder text

---

### 7.2 LiteratureAgent

**Responsibility:** Synthesizes multiple paper summaries into a comparative literature review.

**Prompt Strategy:**
- Receives concatenated summaries of all papers
- Produces `comparative_synthesis`, `methodological_clashes`, `common_themes`

**Outputs:** Dict fed directly to `GapAgent.discover_gaps()` as `literature_comparison` parameter

---

### 7.3 ContradictionAgent

**Responsibility:** Cross-paper technical clash identification.

**Prompt Strategy:**
- System: "...identify direct conflicts, competing findings, methodological clashes, or opposing theoretical conclusions..."
- Forces naming exact paper titles (not "Paper A vs Paper B")
- Requires granular 2–3 sentence root-cause analysis

**State Update:** `session.contradictions = [ContradictionItem(...), ...]` → persisted

---

### 7.4 TrendAgent

**Responsibility:** Research trajectory forecasting.

**Prompt Strategy:**
- Synthesizes growth direction from paper publication timelines and emerging concepts
- Outputs growth classification: `"Exponential Growth"`, `"Maturing"`, `"Declining"`

**State Update:** `session.trends = TrendForecast(...)` → persisted

---

### 7.5 GapAgent

**Responsibility:** Core gap discovery. The most prompt-engineered agent in the system.

**Prompt Strategy:**
- System: Explicitly prohibits generic gaps ("more data needed"). Demands structural engineering blind spots.
- User prompt builds formatted paper context: `Paper #i: Title\n- Methodology...\n- Findings...\n- Contributions...`
- Requires `evidence_papers` (exact titles) and `supporting_passages` (verbatim text)
- Confidence scoring tied to literature-backed evidence

**State Update:** `session.gaps = [GapItem(...), ...]` → persisted

**Also Used In Debate:** `gap_agent.call_llm()` called directly with defense prompt (bypassing `discover_gaps()`)

---

### 7.6 CriticAgent

**Responsibility:** Anonymous "Reviewer #2" critique simulation.

**Prompt Strategy:**
- System: "...anonymous Academic Journal Reviewer... question structural variables, point out potential prior works..."
- Produces `critique` (2–3 sentences) + `challenge_questions` (2 specific technical questions)

**State Update:** Feeds into `session.debate_transcript` (not a separate field)

---

### 7.7 HypothesisAgent

**Responsibility:** Formal hypothesis formulation and novelty self-evaluation.

**Prompt Strategy:**
- System: "...visionary Academic Architect and Theoretical Synthesizer..."
- Forces If-Then causal structure with explicit variable identification
- Novelty scoring with calibrated rubric (9.0+ = paradigm shift)
- Lineage dictionary construction with verbatim passage extraction

**State Update:** `session.hypotheses = [HypothesisItem(...)]` → persisted; lineage evidence_papers patched with real paper IDs

---

### 7.8 ExperimentAgent

**Responsibility:** Rigorous experimental blueprint design.

**Prompt Strategy:**
- System: "...expert Experimental Physicist and Empirical Computer Scientist..."
- Forbids vague instructions; requires exact execution steps
- Variables dictionary must distinguish independent/dependent/controlled

**State Update:** `session.experiments = [ExperimentItem(...)]` → persisted

---

### 7.9 PublicationAgent

**Responsibility:** Academic manuscript section drafting.

**Prompt Strategy:**
- System: "...elite Academic Copywriter..."
- Receives full session synthesis as input context
- Produces 4 sections: abstract (200 words), literature review (2 paragraphs), methodology (2 paragraphs), future work (1 paragraph)

**State Update:** `session.reports = ReportResponse(...)` → persisted

---

### 7.10 QualityAgent

**Responsibility:** Research blueprint audit and reproducibility checking.

**Prompt Strategy:**
- System: "...highly demanding Editor-in-Chief and Scientific Peer-Review Auditor..."
- Evaluates 5 dimensions + issues specific reproducibility warnings
- Warnings are concrete and actionable (e.g., "Missing control variables for baseline models")

**State Update:** `session.benchmarks = BenchmarkScores(...)` → persisted

---

## 8. Pipeline Orchestration

### Architecture

The orchestration layer is a **custom Python sequential-parallel coordinator** in `coordinator.py`, not a LangGraph state machine (despite LangGraph being listed in requirements).

### Execution Graph (ASCII Diagram)

```
PDF Upload
    │
    ▼
┌─────────────────────────────────────────────────────┐
│                   COORDINATOR                        │
│                                                      │
│  ┌──────────────────────────────────────────────┐   │
│  │  STEP 1: Per-Paper Loop                       │   │
│  │                                               │   │
│  │  For each paper:                              │   │
│  │    ├── ResearchAgent.summarize_paper()        │   │
│  │    └── KnowledgeGraph.extract_graph_from_text()  │
│  │         (runs in same loop, sequential)       │   │
│  └──────────────────────────────────────────────┘   │
│                        │                             │
│                        ▼                             │
│  ┌──────────────────────────────────────────────┐   │
│  │  STEP 2: Cross-Paper Synthesis                │   │
│  │                                               │   │
│  │    ├── LiteratureAgent.compare_papers()       │   │
│  │    ├── ContradictionAgent.detect_contradictions()│
│  │    └── TrendAgent.forecast_trends()           │   │
│  │         (sequential, 1s sleep between each)  │   │
│  └──────────────────────────────────────────────┘   │
│                        │                             │
│                        ▼                             │
│  ┌──────────────────────────────────────────────┐   │
│  │  STEP 3: Gap Discovery                        │   │
│  │                                               │   │
│  │    └── GapAgent.discover_gaps()               │   │
│  └──────────────────────────────────────────────┘   │
│                        │                             │
│                        ▼                             │
│  ┌──────────────────────────────────────────────┐   │
│  │  STEP 4: Debate Arena (on primary gap)        │   │
│  │                                               │   │
│  │    ├── CriticAgent.critique_gap()             │   │
│  │    └── GapAgent.call_llm(defense_prompt)      │   │
│  └──────────────────────────────────────────────┘   │
│                        │                             │
│                        ▼                             │
│  SAVE knowledge graph layout to disk                 │
│                        │                             │
│                        ▼                             │
│  ┌──────────────────────────────────────────────┐   │
│  │  STEP 5: Hypothesis (on primary gap)          │   │
│  │                                               │   │
│  │    └── HypothesisAgent.generate_hypothesis()  │   │
│  └──────────────────────────────────────────────┘   │
│                        │                             │
│                        ▼                             │
│  ┌──────────────────────────────────────────────┐   │
│  │  STEP 6: Experiment Design                    │   │
│  │                                               │   │
│  │    └── ExperimentAgent.design_experiment()    │   │
│  └──────────────────────────────────────────────┘   │
│                        │                             │
│                        ▼                             │
│  ┌──────────────────────────────────────────────┐   │
│  │  STEP 7: Publication Draft                    │   │
│  │                                               │   │
│  │    └── PublicationAgent.write_manuscript_draft() │
│  └──────────────────────────────────────────────┘   │
│                        │                             │
│                        ▼                             │
│  ┌──────────────────────────────────────────────┐   │
│  │  STEP 8: Quality Evaluation                   │   │
│  │                                               │   │
│  │    └── QualityAgent.evaluate_research()       │   │
│  └──────────────────────────────────────────────┘   │
│                        │                             │
│                        ▼                             │
│               Return SessionResponse                 │
└─────────────────────────────────────────────────────┘
```

### State Propagation

The shared state object is `SessionResponse`. Each agent's output is immediately written to the session and persisted:

```python
session.gaps = discovered_gaps
session = db.save_session(session)    # Persisted after each step
```

### Rate Limiting

`time.sleep(1)` between every agent call to respect Gemini free-tier 15 RPM limit. This results in a total pipeline execution time of approximately 60–120 seconds for a 2-paper session.

### Background Execution

The pipeline runs via FastAPI `BackgroundTasks`:

```python
background_tasks.add_task(execute_pipeline_background, session_id)
return session  # Returns immediately with current state
```

Frontend polls `GET /api/agents/status/{session_id}` to track: `idle` → `running` → `completed` / `failed: {error}`.

### Error Recovery

Each agent call is wrapped in `try/except` at the `BaseAgent.call_llm()` level. On any exception, `_get_offline_stub()` is called and the pipeline continues. No agent failure stops the overall pipeline execution.

---

## 9. PDF Processing Pipeline

### Complete Upload Flow

```
Client                     FastAPI                  Services             Storage
  │                           │                        │                    │
  │  POST /api/ingest/upload  │                        │                    │
  │  (multipart: session_id   │                        │                    │
  │   + file.pdf)             │                        │                    │
  │──────────────────────────►│                        │                    │
  │                           │  get_session()         │                    │
  │                           │──────────────────────────────────────────► │
  │                           │◄────────────────────────────────────────── │
  │                           │  (session validated)   │                    │
  │                           │                        │                    │
  │                           │  validate .pdf ext     │                    │
  │                           │  generate paper_id     │                    │
  │                           │  save to ./uploads/    │                    │
  │                           │──────────────────────────────────────────► │
  │                           │                        │                    │
  │                           │  parse_and_ingest_pdf()│                    │
  │                           │───────────────────────►│                    │
  │                           │                        │  pypdf.PdfReader() │
  │                           │                        │  extract_text()    │
  │                           │                        │  [raw_text ready]  │
  │                           │                        │                    │
  │                           │                        │  Gemini 2.5-flash  │
  │                           │                        │  (first 8000 chars)│
  │                           │                        │  → metadata JSON   │
  │                           │◄───────────────────────│                    │
  │                           │  (raw_text, metadata)  │                    │
  │                           │                        │                    │
  │                           │  save_paper()          │                    │
  │                           │──────────────────────────────────────────► │
  │                           │                        │                    │
  │                           │  index_paper()         │                    │
  │                           │───────────────────────►│                    │
  │                           │                        │  chunk_text()      │
  │                           │                        │  1200 chars,       │
  │                           │                        │  200 overlap       │
  │                           │                        │                    │
  │                           │                        │  get_embeddings()  │
  │                           │                        │  gemini-embedding  │
  │                           │                        │  -001              │
  │                           │                        │                    │
  │                           │                        │  ChromaDB.upsert() │
  │                           │                        │  OR fallback JSON  │
  │                           │                        │──────────────────► │
  │                           │◄───────────────────────│                    │
  │                           │                        │                    │
  │                           │  update session.papers │                    │
  │                           │  save_session()        │                    │
  │                           │──────────────────────────────────────────► │
  │                           │                        │                    │
  │◄──────────────────────────│                        │                    │
  │  200: SessionResponse     │                        │                    │
```

### Chunking Algorithm

```python
def chunk_text(text, chunk_size=1200, chunk_overlap=200):
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break
        chunk = text[start:end]
        # Find last sentence boundary past halfway point
        last_end = max(
            chunk.rfind(". "),
            chunk.rfind("?\n"),
            chunk.rfind(".\n")
        )
        if last_end > chunk_size // 2:
            end = start + last_end + 1
        chunks.append(text[start:end])
        start = end - chunk_overlap
```

---

## 10. Knowledge Graph Architecture

### Node Types

| Type | Description | Visual Role |
|---|---|---|
| `Paper` | Root publication node | Central anchor, rendered at (400, 300) |
| `Method` | Algorithmic technique or model architecture | Describes HOW |
| `Dataset` | Benchmark, corpus, or data split | Describes WHAT was tested on |
| `Finding` | Empirical result or qualitative outcome | Describes WHAT was discovered |
| `Limitation` | Constraint, threshold, or failure condition | Describes WHERE it breaks (also used for Gap nodes) |

### Relationship Types (Edge Labels)

| Label | Meaning |
|---|---|
| `proposes_method` | Paper → Method |
| `evaluated_on` | Method → Dataset |
| `yields_finding` | Method → Finding |
| `reveals_limitation` | Finding → Limitation |
| `exhibits_gap` | Paper → Gap (injected by coordinator) |
| `contradicts` | Paper → Paper (injected from contradiction results) |
| `proposes`, `highlights`, `achieves`, `suffers_from` | General Gemini-generated relations |

### Edge Color Coding

| Relationship | Color |
|---|---|
| `contradicts` | `#f43f5e` (Rose red) |
| `supports` | `#10b981` (Emerald green) |
| `extends` | `#8b5cf6` (Violet) |
| `gap` (contains) | `#d946ef` (Fuchsia) |
| Default | `#14b8a6` (Teal) |

### React Flow Integration

All nodes are returned with `position: {x: int, y: int}` computed by the backend spiral layout algorithm. The frontend passes this directly to React Flow's `<ReactFlow nodes={...} edges={...} />` component. Edges have `type: "smoothstep"` and `animated: true` for visual feedback.

### Spiral Layout Algorithm

```
Paper node → placed at center (400, 300)
For each remaining node i:
    multiplier = sqrt(len(layout_nodes_so_far))
    radius = 140 * multiplier
    theta += 0.75 + (0.2 / multiplier)
    x = 400 + radius * cos(theta)
    y = 300 + radius * sin(theta)
```

This produces an outward-expanding spiral that prevents node overlap even for large graphs.

### Graph Persistence

After coordinator completes, graph is written to `session_graph_{session_id}.json`. On `GET /api/graph/{session_id}`, the file is loaded directly if it exists. If not, a default graph containing only paper nodes is dynamically generated.

---

## 11. Research Gap Discovery Engine

### Gap Identification Methodology

The GapAgent performs a **structured 3-gap synthesis** across all ingested papers. Its methodology:

1. **Context aggregation:** All paper summaries formatted as numbered entries with methodology, findings, and contributions.
2. **Comparative input:** Literature agent's `comparative_synthesis` and `methodological_clashes` provided as additional context.
3. **Non-obvious gap constraint:** System prompt explicitly prohibits generic gaps. Forces the model to identify structural engineering blind spots, restrictive mathematical assumptions, narrow evaluation conditions, scale thresholds, or unexplored cooperative paradigms.
4. **Structured output:** Each gap must include confidence score backed by specific paper limitations.

### Evidence Extraction

Each gap requires:
- `evidence_papers`: Exact titles of papers whose limitations prove this gap exists
- `supporting_passages`: Verbatim sentences from paper text proving the limitation

### Confidence Scoring

The confidence score (0–100) represents the strength of evidence that this gap is genuinely open:
- `90+`: Multiple papers all share the same limitation with explicit statements
- `70–89`: Clear pattern of limitation across multiple papers
- `50–69`: Implied by methodology choices but not explicitly stated
- `<50`: Speculative gap not well-evidenced in current papers

### Citation Linking

Gap `evidence_papers` are free-text paper title strings at gap discovery time. The coordinator does not perform automatic ID resolution for gaps — paper IDs are injected only into hypothesis lineage.

### Verification Logic

No automated verification exists. Quality Agent scores the gap quality post-hoc as `gap_quality` (0–100).

---

## 12. Contradiction Detection Engine

### Comparison Strategy

ContradictionAgent receives paper summaries formatted as:
```
Paper #1: Title
- Proposed Methodology: ...
- Key Findings: ...
- Unique Contributions: ...
```

It performs cross-examination identifying up to 3 contradictions.

### Conflict Detection

The prompt specifically targets:
- **Metric contradictions:** Paper A claims method X outperforms Y; Paper B proves the opposite under condition Z
- **Methodological clashes:** Incompatible architectural assumptions
- **Theoretical contradictions:** Opposing explanations for the same phenomenon

### Structured Outputs

Each `ContradictionItem`:
- `papers`: Exact titles of conflicting papers (not placeholders)
- `subject`: Specific parameter or claim under clash
- `finding_a` / `finding_b`: Each paper's exact position
- `analysis`: 2–3 sentence technical root-cause explanation

### Graph Integration

Detected contradictions generate `contradicts` edges in the knowledge graph between identified paper nodes. Fuzzy string matching (`paper.title in clash.papers[0] or clash.papers[0] in paper.title`) resolves paper titles to node IDs.

---

## 13. Debate Arena

### Architecture

The Debate Arena simulates a 2-turn academic peer review:

**Turn 1 — Reviewer Agent (CriticAgent):**
```python
critique_res = critic_agent.critique_gap(
    target_gap.title,
    target_gap.description,
    target_gap.contribution
)
```
Output: `critique` (challenge text) + `challenge_questions` (2 technical questions)

**Turn 2 — Researcher Agent (GapAgent defense):**
```python
prompt_def = f"""
As a lead researcher, defend your proposed gap...
Gap Title: {target_gap.title}
Reviewer Critique: {critique_res.get('critique')}
Reviewer Questions: {', '.join(critique_res.get('challenge_questions', []))}
Provide a robust, technically grounded 3-sentence scientific defense.
"""
def_res = gap_agent.call_llm(prompt_def)
```

### Transcript Format

```json
[
  {"speaker": "Reviewer Agent", "message": "Is this gap truly unaddressed?..."},
  {"speaker": "Reviewer Agent", "message": "Technical Query #1: How will you isolate..."},
  {"speaker": "Researcher Agent", "message": "We defend this gap by..."}
]
```

The transcript is stored in `session.debate_transcript` and available for display in the frontend's Debate Arena module.

### Target Gap Selection

Only the **first** discovered gap (`discovered_gaps[0]`) is debated. Multi-gap debate is a roadmap feature.

---

## 14. Novelty Scoring System

### Hypothesis Novelty Score

The HypothesisAgent self-evaluates novelty as part of hypothesis generation:

**Calibrated Rubric:**
```
9.0–10.0: Structural paradigm shift
          Example: completely new cooperative multi-agent consensus framework
          
7.0–8.9:  High novel integration of diverse concepts  
          Example: merging two unrelated mathematical frameworks for the first time
          
5.0–6.9:  Moderate novelty
          Combines known concepts in a new application domain

< 5.0:    Incremental extension of existing models
          Applies a known technique to a slightly different dataset
```

**Output:** `novelty_score: float` + `novelty_rationale: str` explaining the conceptual delta from established works.

### Ad-Hoc Concept Novelty (Co-Pilot)

**Endpoint:** `POST /api/sessions/compare-novelty`

**Process:**
1. User submits arbitrary concept text
2. System constructs prompt: user concept vs. all ingested paper abstracts
3. Gemini evaluates using same rubric
4. Returns: `{novelty_score, novelty_rationale, closest_papers[], delta}`

**Uses `response_mime_type: "application/json"`** for structured output without schema prompting.

---

## 15. Experiment Design Engine

### Variable Generation

ExperimentAgent produces a `variables` dictionary with three keys:
- `independent`: What is manipulated in the experiment
- `dependent`: What is measured/observed
- `controlled`: What is kept constant to isolate the causal relationship

### Dataset Recommendations

The system recommends datasets from two sources:
1. HypothesisAgent's `suggested_datasets` (embedded in hypothesis, pulled from Gemini knowledge)
2. ExperimentAgent's `suggested_datasets` (independently generated from hypothesis statement)

The coordinator prefers HypothesisAgent's datasets: `primary_hypothesis.suggested_datasets or exp_res.get("suggested_datasets", [])`

### Benchmark Selection

Similarly, `suggested_benchmarks` come from HypothesisAgent output.

### Metric Recommendations

`evaluation_metrics` prioritize HypothesisAgent's `suggested_metrics` over ExperimentAgent's defaults.

### Experimental Protocol Generation

The `methodology` field is a sequential list of steps. The agent is instructed to avoid vague instructions:
```
Step 1: Set up environment and fetch benchmark dataset
Step 2: Train baseline model with default hyperparameters  
Step 3: Apply proposed modification
Step 4: Run parameter sweep over [specific range]
Step 5: Apply Wilcoxon signed-rank test for statistical significance
```

---

## 16. Publication Generation Engine

### Input Assembly

```python
papers_summary_text = "\n".join([
    f"Paper: {p.get('title')}\nProblem: {p.get('problem_statement')}\nMethod: {p.get('proposed_methodology')}"
    for p in paper_summaries
])

pub_res = publication_agent.write_manuscript_draft(
    topic=session.topic,
    papers_summary=papers_summary_text,
    lit_review=lit_review,
    gaps=[g.dict() for g in discovered_gaps],
    hypothesis=primary_hypothesis.dict(),
    experiment=primary_experiment.dict()
)
```

### Generated Sections

**Abstract** (target: 200 words):
- Problem statement
- Literature gap summary
- Proposed methodology reference
- Expected empirical significance claim

**Literature Review** (target: 2 paragraphs):
- Paragraph 1: Existing works with thematic grouping
- Paragraph 2: Common limitations and the specific gap this work addresses

**Methodology** (target: 2 paragraphs):
- Paragraph 1: Formal hypothesis and variable definitions
- Paragraph 2: Step-by-step technical implementation

**Future Work** (target: 1 paragraph):
- Dataset scaling opportunities
- Model configuration extensions
- Secondary research directions

---

## 17. Research Lineage System

### Traceability Model

```
HypothesisItem
  └── lineage: {
        "gap_title": "Scalability Constraints in...",
        "supporting_findings": [
            "Single-agent pipeline bottleneck at 8+ agents",
            "Linear complexity assumptions broken above N=12"
        ],
        "evidence_papers": [
            {
                "paper_id": "7c9b3bcf",    ← Real session paper ID (patched by coordinator)
                "title": "MARL Survey 2024",
                "passage": "Our experiments were limited to..."  ← Verbatim text
            }
        ]
      }
  │
  ├── gap_title → GapItem.title
  │
  └── evidence_papers[].paper_id → Paper.id (in session.papers)
                                     │
                                     └── Paper.parsed_text (in database)
```

### ID Patching

The coordinator performs a post-processing step after hypothesis generation:

```python
if primary_hypothesis.lineage and isinstance(primary_hypothesis.lineage, dict):
    evidence_papers = primary_hypothesis.lineage.get("evidence_papers", [])
    if isinstance(evidence_papers, list):
        for ep in evidence_papers:
            if isinstance(ep, dict):
                if ep.get("paper_id") == "86d23221" and session.papers:
                    ep["paper_id"] = session.papers[0].id
                    ep["title"] = session.papers[0].title
```

**Note:** This patches only the placeholder ID `"86d23221"` that Gemini inserts in mock lineage. For real responses with actual generated IDs, patching is skipped. This is a known limitation — full ID resolution requires matching by title rather than hardcoded placeholder detection.

---

## 18. Research Co-Pilot

### Memory Architecture

The Co-Pilot does **not** use a vector retrieval layer. It constructs context entirely from session state at query time:

```python
papers_context = "\n".join([
    f"- Title: {p.title}\n  Abstract: {p.abstract}" 
    for p in session.papers
])
gaps_context = "\n".join([
    f"- Gap: {g.title}\n  Description: {g.description}" 
    for g in session.gaps
])
hypotheses_context = "\n".join([
    f"- Hypothesis: {h.statement}\n  Rationale: {h.rationale}" 
    for h in session.hypotheses
])
```

This means the Co-Pilot's context is bounded by the SQLite/Supabase session data, not the raw paper text. For document-level semantic queries, the vector store would need to be integrated into the Co-Pilot endpoint (currently a roadmap feature).

### Session Awareness

The system prompt always includes the current session topic and all session-level data. The Co-Pilot is stateless per call but reconstructs context from persistent storage on every invocation.

### Query Handling

```
POST /api/sessions/copilot
{
    "session_id": "7c9b3bcf",
    "message": "What datasets should I use to test the hypothesis?"
}
```

Response: `{reply: "...", history: [...]}`

History is the full `copilot_history` list including the just-added turn.

---

## 19. API Documentation

### Base URL

```
Production: https://scholarmind-f319.onrender.com
Local:      http://127.0.0.1:8000
```

All routes are prefixed with `/api`.

---

#### `GET /api/health`

**Description:** Service liveness check.

**Response:**
```json
{"status": "healthy", "service": "scholarmind-api"}
```

---

#### `GET /api/sessions`

**Description:** List all research sessions ordered by timestamp descending.

**Response:** `List[SessionResponse]`

---

#### `POST /api/sessions/create`

**Description:** Initialize a new research workspace session.

**Request:**
```json
{"topic": "LLM Bias in Medical NLP"}
```

**Response:** `SessionResponse` (empty papers/gaps/etc.)

---

#### `GET /api/sessions/{session_id}`

**Description:** Retrieve full session state.

**Response:** `SessionResponse` with all fields populated.

---

#### `DELETE /api/sessions/{session_id}`

**Description:** Delete session, associated papers, vectors, and graph cache.

**Response:** `{"message": "Session deleted successfully"}`

---

#### `GET /api/sessions/paper/{paper_id}`

**Description:** Retrieve raw parsed text for a specific paper.

**Response:** `{"parsed_text": "..."}`

---

#### `POST /api/sessions/copilot`

**Description:** Query the Research Co-Pilot with session context.

**Request:**
```json
{
    "session_id": "7c9b3bcf",
    "message": "What is the primary research gap?"
}
```

**Response:**
```json
{
    "reply": "The primary gap identified is...",
    "history": [
        {"speaker": "user", "message": "...", "timestamp": "2026-06-01T..."},
        {"speaker": "copilot", "message": "...", "timestamp": "2026-06-01T..."}
    ]
}
```

---

#### `POST /api/sessions/compare-novelty`

**Description:** Compare a custom concept against the session's reference papers for novelty scoring.

**Request:**
```json
{
    "session_id": "7c9b3bcf",
    "concept": "A self-healing multi-agent consensus layer with predictive state buffering"
}
```

**Response:**
```json
{
    "novelty_score": 8.4,
    "novelty_rationale": "...",
    "closest_papers": ["MARL Survey 2024"],
    "delta": "The specific combination of self-healing with predictive state..."
}
```

---

#### `POST /api/ingest/upload`

**Description:** Upload and ingest an academic PDF file into a session.

**Request:** `multipart/form-data`
- `session_id: string`
- `file: binary PDF`

**Validation:** Rejects non-`.pdf` files with 400.

**Response:** Updated `SessionResponse` with new paper in `papers` list.

---

#### `POST /api/agents/run`

**Description:** Trigger the full multi-agent research pipeline for a session.

**Query Params:** `?session_id=7c9b3bcf`

**Behavior:** Immediately returns current session state; pipeline runs in background.

**Response:** Current `SessionResponse` (pipeline not yet complete)

---

#### `GET /api/agents/status/{session_id}`

**Description:** Check background pipeline execution status.

**Response:**
```json
{
    "session_id": "7c9b3bcf",
    "status": "running"  // "idle" | "running" | "completed" | "failed: {error}"
}
```

---

#### `GET /api/graph/{session_id}`

**Description:** Retrieve React Flow-formatted knowledge graph for a session.

**Response:**
```json
{
    "nodes": [
        {
            "id": "attention_is_all_you_nee",
            "type": "Paper",
            "label": "Attention Is All You Need",
            "summary": "Primary reference paper under review.",
            "position": {"x": 400, "y": 300}
        }
    ],
    "edges": [
        {
            "id": "edge_src_tgt",
            "source": "src_node_id",
            "target": "tgt_node_id",
            "label": "proposes_method",
            "type": "smoothstep",
            "animated": true,
            "style": {"stroke": "#14b8a6", "strokeWidth": 2}
        }
    ]
}
```

---

## 20. Security Architecture

### Secret Management

All secrets managed via `.env` file:

```env
GEMINI_API_KEY=...      # Required — Gemini API authentication
SUPABASE_URL=...        # Optional — cloud database sync
SUPABASE_KEY=...        # Optional — Supabase PostgREST auth
CHROMA_DB_PATH=./chroma_db  # ChromaDB persistence path
PORT=8000
HOST=127.0.0.1
```

### .env Strategy

- `.env` is gitignored (listed in `.gitignore`)
- `.env.example` committed to repository with placeholder values
- Render uses environment variable injection (not `.env` file in production)
- Vercel uses dashboard environment variables for `NEXT_PUBLIC_API_URL`

### API Key Protection

- Gemini key validated on startup: `len(key) > 8 and "Replace" not in key`
- If key is invalid/absent, system enters offline mode returning stubs
- Key never logged or exposed in API responses
- **Current Issue:** CORS is `allow_origins=["*"]` — must be restricted to Vercel domain in production

### GitHub Safety Practices

- `.gitignore` excludes: `.env`, `__pycache__/`, `.venv/`, `.next/`, `node_modules/`, `*.db`, `session_vectors_*.json`, `session_graph_*.json`, `uploads/`
- Secrets are never hardcoded in source files
- Example files use placeholder strings (e.g., `"Replace_With_Your_Key"`)

---

## 21. Performance Optimizations

### Vector Search Optimizations

**ChromaDB path:** Uses persistent client with indexed embeddings. Query complexity: O(log n) approximate nearest neighbor.

**Fallback path:** O(n) linear scan. For small sessions (< 100 chunks), performance is acceptable. For large paper sets, this is a bottleneck.

### Caching

**Knowledge Graph:** Cached to `session_graph_{id}.json` after first generation. Subsequent `GET /api/graph/{id}` calls load from disk without re-invoking Gemini.

**Session State:** SQLite acts as persistent cache — no re-computation on reads.

### Rate-Limit Handling

Between every agent call in the pipeline:
```python
time.sleep(1)  # Prevents 429 TooManyRequests on Gemini free tier
```

This adds ~8–10 seconds of total sleep time per pipeline run. On paid tier, these sleeps can be reduced to 100ms.

### Gemini Fallbacks

Three-tier fallback prevents total pipeline failure:
1. `gemini-2.5-flash` (primary)
2. `gemini-1.5-flash` (model fallback, only in parser and graph services)
3. `_get_offline_stub()` (API unavailable — schema-conforming mock data)

### Parallel Execution

**Current State:** All agent calls are sequential. The `coordinator.py` runs agents one after another with `time.sleep(1)` between calls.

**Not Implemented:** True parallel execution (e.g., running LiteratureAgent + ContradictionAgent + TrendAgent concurrently). This is a planned optimization that would reduce pipeline time by ~30 seconds on a 3-paper session.

---

## 22. Evaluation Framework

### Gap Quality (0–100)

Evaluated by QualityAgent on:
- Literature negligence evidence strength
- Specificity of the gap (non-generic)
- Supporting passage quality
- Confidence score calibration

### Evidence Coverage

Tracked via `evidence_papers` count and `supporting_passages` count per gap. More verbatim passages = higher evidence coverage. No automated scoring — evaluated holistically by QualityAgent.

### Citation Accuracy

Citation accuracy is not formally verified. The system trusts Gemini's output of paper titles. Future improvement: cross-reference cited titles against `session.papers` titles to detect hallucinated citations.

### Novelty Consistency

The Novelty Score from HypothesisAgent (0–10) and the Novelty score from QualityAgent (0–100) are independent evaluations. They should correlate but are not mathematically linked. Inconsistencies between them can reveal grounding failures.

### Research Readiness

Measured by `feasibility` in BenchmarkScores. Composite of:
- Are datasets publicly available?
- Are baseline models accessible?
- Is the methodology executable in a standard research environment?

---

## 23. Limitations & Technical Debt

### Current Limitations

| Area | Limitation |
|---|---|
| **File Types** | Only PDF files supported. PPTX, DOCX, images rejected at upload. |
| **Hypothesis Depth** | Only 1 hypothesis generated per pipeline run (for the first gap only). |
| **Debate Rounds** | Only 2-turn debate (1 critique + 1 defense). No multi-round iteration. |
| **Co-Pilot Memory** | Co-Pilot cannot search raw paper text — only uses session-level summaries. |
| **Knowledge Graph** | Graph layout is spiral-only, no force-directed or user-rearrangeable layout. |
| **Session Isolation** | Vectors scoped by `session_id` but the `session_vectors_*.json` files are stored in the server working directory, which is ephemeral on Render free tier. |
| **Contradiction Resolution** | Contradictions are identified but no resolution or reconciliation strategy is proposed. |
| **Patent Discovery** | `PatentOpportunity` schema exists in models but no agent populates it — all patent data is empty. |
| **Lineage ID Patching** | Hardcoded placeholder detection (`"86d23221"`) is fragile and won't resolve lineage correctly when Gemini generates real-looking IDs. |
| **Citation Hallucination** | No verification that cited paper titles in gaps/hypotheses actually exist in the session. |
| **CORS** | Wildcard `allow_origins=["*"]` — must be restricted before any production security review. |
| **Rate Limit** | 15 RPM free-tier cap means two concurrent users will cause 429 errors. |
| **Render Cold Start** | Free tier spins down after 15 minutes of inactivity, causing 50+ second cold starts. |

### Technical Debt

| Item | Description |
|---|---|
| **LangGraph not used** | Listed in requirements, installed, not invoked. Coordinator is custom Python. |
| **Single `page.tsx`** | Entire frontend in one 104KB file. Should be componentized. |
| **No test suite** | Zero unit tests, integration tests, or agent behavior tests. |
| **Hardcoded model name** | `"gemini-2.5-flash"` hardcoded in each agent. Should be a configurable constant. |
| **`time.sleep(1)` approach** | Brittle rate limiting. Should be exponential backoff with retry. |
| **`active_runs` dict** | In-memory pipeline status tracking. Lost on server restart. |
| **Vector files in working dir** | `session_vectors_*.json` stored at process working directory, not a stable path. |
| **Duplicate `save_session` call** | Lines 97–102 of coordinator.py call `db.save_session(session)` twice consecutively. |

---

## 24. Future Roadmap

### V1 — Completed Features

- ✅ Research Session management (create/read/delete)
- ✅ PDF upload, text extraction, Gemini metadata parsing
- ✅ ChromaDB vector indexing with pure-Python cosine fallback
- ✅ 9-agent sequential pipeline (Research → Literature → Contradiction → Trend → Gap → Debate → Hypothesis → Experiment → Publication → Quality)
- ✅ Knowledge Graph with React Flow visualization and spiral layout
- ✅ Research Co-Pilot with session context
- ✅ Novelty scoring (hypothesis-embedded + ad-hoc comparison)
- ✅ Benchmark evaluation (5-dimension quality audit)
- ✅ Research lineage traceability
- ✅ Debate Arena (Reviewer vs Researcher 2-turn simulation)
- ✅ SQLite + Supabase dual persistence
- ✅ Offline stub mode (zero-API operation)
- ✅ Backend deployed on Render, frontend on Vercel

### V2 — Research Features (Planned)

- [ ] **Multi-hypothesis generation** — 3 hypotheses per gap (currently only 1 per pipeline)
- [ ] **Multi-gap debate** — Debate Arena on all 3 discovered gaps
- [ ] **Semantic Co-Pilot** — integrate vector search into Co-Pilot for document-level queries
- [ ] **Citation verification** — cross-reference cited titles against actual session papers
- [ ] **Parallel agent execution** — run Literature + Contradiction + Trend agents concurrently
- [ ] **Exponential backoff** — replace `time.sleep(1)` with proper retry logic
- [ ] **Patent Discovery Agent** — populate the existing `PatentOpportunity` schema
- [ ] **Session comparison** — compare gaps across multiple research sessions
- [ ] **Export to PDF/LaTeX** — publication-ready document export

### Publication Roadmap

- [ ] Structured BibTeX citation export per paper
- [ ] Full LaTeX manuscript generation (not just markdown sections)
- [ ] Journal/conference template selection (IEEE, ACM, NeurIPS)
- [ ] Reference formatting (APA, MLA, Vancouver)
- [ ] ArXiv submission checklist validation

### Patent Roadmap

- [ ] **PatentAgent** — analyzes hypothesis novelty specifically for patentability
- [ ] **Prior art search** — integrates Google Patents API or USPTO database
- [ ] **Claims drafting** — generates formal patent claim language from hypothesis
- [ ] **Patent landscape mapping** — shows competitive patent filings in the research domain

---

## 25. Conclusion

ScholarMind is a working proof-of-concept that **multi-agent LLM coordination can automate the core cognitive workflows of academic research**. The system demonstrates:

**Architectural Decisions That Work:**
- The `BaseAgent` → specialized agent inheritance pattern cleanly separates LLM orchestration from domain logic
- The three-tier fallback (primary model → fallback model → offline stub) ensures the system never completely fails
- JSON schema enforcement via prompt engineering achieves structured output without function-calling APIs
- The spiral layout algorithm for knowledge graphs is a simple, dependency-free solution that prevents node overlap

**Technical Achievements:**
- Complete zero-dependency vector search implementation using pure Python mathematics
- Self-healing SQLite migration system that adds missing columns without schema drops
- Dual-layer persistence (Supabase cloud + SQLite local) with automatic failover using only `urllib` (no external HTTP library)
- Full research pipeline from PDF upload to publication draft in a single API trigger

**Honest Assessment:**
The system works end-to-end when the Gemini API is available and the backend is reachable. The free-tier constraints (15 RPM rate limit, Render cold starts) create practical friction for multi-user or high-frequency use. The gap agent and hypothesis agent produce genuinely useful output when fed with real academic PDFs. The debate arena simulation is structurally sound but limited to 2 turns. The knowledge graph visualization is functional and visually informative.

The most significant value ScholarMind delivers is **time compression** — reducing the gap-to-hypothesis-to-experiment loop from hours of manual work to approximately 90 seconds of automated pipeline execution.

---

*End of ScholarMind Technical Architecture & Implementation Specification*  
*Version 1.0.0 | SCAAI | June 2026*
