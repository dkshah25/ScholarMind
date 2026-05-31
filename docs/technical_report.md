# ScholarMind Technical Report: Advanced Multi-Agent Research Orchestration

**Author**: ScholarMind Core Architecture Team  
**Date**: June 2026  
**Status**: Technical Whitepaper & System Architecture Specification  

---

## Abstract

We present **ScholarMind**, a domain-specific Research Intelligence Platform designed to automate rigorous scientific literature analysis, identify latent research gaps, simulate peer-review adversarial debates, plan empirical verification steps, and compile publication-ready drafts. Rather than relying on standard monolithic RAG patterns, ScholarMind employs a decoupled network of specialized, self-correcting agents operating on a state-based LangGraph coordinator. We address critical deployment challenges—including API rate limitations and compilation failures of C++ vector dependencies under modern runtimes—by designing robust, self-healing runtime wrappers, including a pure-Python high-dimensional Cosine Similarity engine mapping Gemini embeddings.

---

## 1. System Architecture & Agent Orchestration

ScholarMind decouples literature analysis into a directed dynamic graph of discrete, role-specific agents:

```
[Parsed PDFs] ──► Ingestion & Vectorization ──► Research Agent (Entities)
                                                      │
                                                      ▼
[Contradictions] ◄── Contradiction Agent ◄──── Literature Agent (Synthesis)
                                                      │
                                                      ▼
[Debate Arena] ◄─── Reviewer vs Researcher ◄─── Gap Agent (Limitations)
                                                      │
                                                      ▼
[Experiment Plan] ◄── Experiment Agent ◄────── Hypothesis Agent (Causal if-then)
                                                      │
                                                      ▼
[Publication Draft] ◄───────────────────────── Publication Agent (LaTeX)
                                                      │
                                                      ▼
                                              Quality Evaluator
```

### 1.1 Ingestion & Pure-Math Vector Space
When a PDF is uploaded, a dense vector representation is generated using Gemini `text-embedding-004` (3072-dimensional spaces).
To eliminate compilation dependencies of native databases (e.g. `chromadb` C++ dependencies) in cloud runtimes, we implemented a pure-Python vector database fallback. Semantic searches are calculated using the standard **Cosine Similarity** formula over normalized vectors:

$$\text{Cosine Similarity} = \frac{\mathbf{A} \cdot \mathbf{B}}{\|\mathbf{A}\|_2 \|\mathbf{B}\|_2}$$

Where:
* $\mathbf{A}$ and $\mathbf{B}$ represent high-dimensional embedding vectors.
* $\|\mathbf{A}\|_2$ is the $L_2$ norm of vector $\mathbf{A}$.

---

## 2. Research Lineage Tracking (Zero-Hallucination Traceability)

A key limitation of modern scientific LLMs is the inability to track claims to original source segments, leading to hallucinations. ScholarMind solves this by enforcing a strict vertical lineage validation model:

```
          [Causal Hypothesis Statement]
                       │
                       ▼
          [Identified Research Gap]
                       │
                       ▼
          [Supporting Literature Findings]
                       │
                       ▼
          [Cited Source Paper & Verbatim Segment]
```

### 2.1 Schema Definition
The database serializes lineage using standard JSON arrays stored as plain text fields in SQLite:
```json
{
  "lineage": {
    "gap_title": "Multi-agent context degradation in high-token prompts",
    "supporting_findings": ["Standard LLM routing layers lose context when scaling past 32k tokens due to sparse attention grids."],
    "evidence_papers": [
      {
        "paper_id": "7c9b3bcf-paper-1",
        "title": "Attention Dispersal in Large Context Windows",
        "passage": "Under stress testing with context sizes exceeding 32,768 tokens, attention weights decay logarithmically over mid-range keys."
      }
    ]
  }
}
```

---

## 3. Academic Peer-Review Debate Arena

To simulate realistic academic criticism prior to experimental execution, we introduce a **Debate Arena** mimicking standard blind peer reviews:

1. **Reviewer Agent** (Adversary): Analyzes the generated gap and challenges assumptions:
   * "How did you isolate the confounding influence of the optimizer?"
   * "Prior work in [Reference] already reports linear boundaries. What is your conceptual delta?"
2. **Researcher Agent** (Defender): Performs a multi-turn logical defense, utilizing mathematical context and variable constraints.

---

## 4. Empirical Benchmark & Reproducibility Evaluator

Before committing to LaTeX manuscript generation, ScholarMind enforces a quality-control audit of the experimental setup:

- **Novelty**: Computes conceptual delta relative to current publications.
- **Reproducibility Warnings**: Automatically flags missing items like **Control Variables**, **Evaluation Protocol**, or **Data Split Specifications** so researchers can perfect their protocol prior to running live trials.
- **Dataset Recommender**: Proposes standard open-source benchmarks (e.g. BBQ, GSM8K, StereoSet) and metric equations (e.g. Refusal Symmetry, Accuracy) to build a robust methodology.
