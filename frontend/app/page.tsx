"use client";

import React, { useState, useEffect } from "react";
import Sidebar from "@/components/sidebar";
import { 
  FileText, 
  UploadCloud, 
  CheckCircle2, 
  AlertCircle, 
  Cpu, 
  FileCheck,
  TrendingUp,
  Award,
  Layers,
  Database,
  Calendar,
  Eye,
  RefreshCw,
  BookOpen,
  Beaker,
  MessageSquare,
  Send,
  GitBranch,
  X,
  FileWarning
} from "lucide-react";

// React Flow imports
import ReactFlow, { Background, Controls, MiniMap } from "reactflow";
import "reactflow/dist/style.css";

const API_BASE = "http://localhost:8000/api";

export default function MasterDashboard() {
  const [currentTab, setCurrentTab] = useState("overview");
  const [sessions, setSessions] = useState<any[]>([]);
  const [currentSession, setCurrentSession] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  const [pipelineStatus, setPipelineStatus] = useState("idle"); // idle, running, completed, failed
  const [graphData, setGraphData] = useState<{nodes: any[], edges: any[]}>({nodes: [], edges: []});
  
  // Active selected items for detailed panels
  const [selectedPaper, setSelectedPaper] = useState<any>(null);
  const [selectedPaperText, setSelectedPaperText] = useState<string>("");
  const [uploadFile, setUploadFile] = useState<File | null>(null);

  // Research Co-Pilot States
  const [isCopilotOpen, setIsCopilotOpen] = useState(false);
  const [copilotMessage, setCopilotMessage] = useState("");
  const [copilotLoading, setCopilotLoading] = useState(false);

  // Gaps & Hypothesis Explorer States
  const [activeWorkspaceSubTab, setActiveWorkspaceSubTab] = useState<"reader" | "lineage">("reader");
  const [selectedGap, setSelectedGap] = useState<any>(null);
  const [selectedHypothesis, setSelectedHypothesis] = useState<any>(null);

  // Live Console Logs
  const [consoleLogs, setConsoleLogs] = useState<string[]>([
    "System initialized. Select or create a Research Session memory workspace in the sidebar to start."
  ]);

  // ==========================================
  // API Fetch Actions
  // ==========================================

  const addLog = (msg: string) => {
    setConsoleLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${msg}`]);
  };

  const loadSessions = async (autoSelectId?: string) => {
    try {
      const res = await fetch(`${API_BASE}/sessions`);
      if (res.ok) {
        const data = await res.json();
        setSessions(data);
        addLog(`Loaded ${data.length} active research sessions from memory.`);
        
        if (data.length === 0) {
          addLog("Database is empty. Initializing default Research Session...");
          await handleCreateSession("Multi-Agent Collaboration in Academic Research");
        } else {
          const nextSess = autoSelectId 
            ? data.find((s: any) => s.id === autoSelectId) 
            : data[0];
          
          if (nextSess) {
            setCurrentSession(nextSess);
            loadGraph(nextSess.id);
            if (nextSess.gaps && nextSess.gaps.length > 0) setSelectedGap(nextSess.gaps[0]);
            if (nextSess.hypotheses && nextSess.hypotheses.length > 0) setSelectedHypothesis(nextSess.hypotheses[0]);
          }
        }
      }
    } catch (e) {
      addLog("Database server not active yet. Running in offline UI presentation mode.");
      // Fallback Default Mock Session for presentation when backend is launching
      const mockSess = {
        id: "demo-sess",
        topic: "Multi-Agent System for Collaborative Academic Research Gaps Discovery",
        timestamp: new Date().toISOString(),
        papers: [
          { id: "p1", title: "Single-Agent Research Ingestion Bottlenecks", authors: "A. Carter, M. Vance", journal: "J. of AI Research", year: 2024, abstract: "This work investigates traditional vector-store parsing constraints in single-agent architectures, exposing serious speed and parsing coverage blind spots." },
          { id: "p2", title: "Collaborative Agent Systems in Bioinformatics", authors: "L. Zhao, K. Patel", journal: "Nature Intelligence", year: 2025, abstract: "We design a dual-agent structure to parse genomic sequencing papers, verifying that decentralized agents boost extraction accuracy by over 14%." }
        ],
        gaps: [
          { 
            title: "Collaborative Multi-Agent Integration", 
            description: "Most studies evaluate single-agent systems. No work explores collaborative multi-agent educational assistants.", 
            contribution: "Multi-Agent AI Tutor Framework", 
            confidence_score: 82, 
            rationale: "Evaluations in Paper #1 only cover single-user schemas and Paper #2 focuses solely on biology data grids.",
            evidence_papers: ["p1", "p2"],
            supporting_passages: [
              "traditional single-agent architectures suffer from persistent processing bottlenecks under multi-document ingestion splits.",
              "prior setups evaluated single-user static nodes and failed to integrate multi-agent collaborative consensus filters."
            ]
          }
        ],
        hypotheses: [
          { 
            gap_title: "Collaborative Multi-Agent Integration", 
            statement: "If a research operating system coordinates multiple parallel parsing agents, then metadata coverage increases by over 18% with zero validation drift.", 
            rationale: "By parallelizing abstract summary splits, cross-agent consensus cleans noisy tags.", 
            novelty_score: 8.5, 
            novelty_rationale: "Fuses collaborative multi-agent orchestration theories with semantic citation analysis.", 
            confidence_score: 88,
            citations: ["Single-Agent Research Ingestion Bottlenecks", "Collaborative Agent Systems in Bioinformatics"],
            suggested_datasets: ["S2ORC Open Academic Corpus", "arXiv Metadata dataset"],
            suggested_benchmarks: ["MMLU (Massive Multitask Language Understanding)", "GSM8K math corpus"],
            suggested_metrics: ["BLEU-4 Validation Accuracy", "Semantic Cosine Similarity"],
            baselines: ["GPT-4o (baseline single-agent)", "Gemini 2.5 Pro (vanilla RAG)"],
            lineage: {
              gap_title: "Collaborative Multi-Agent Integration",
              supporting_findings: [
                "Single-agent pipelines fail under nested document branches.",
                "Multi-agent collaborative structures optimize validation bounds."
              ],
              evidence_papers: [
                {
                  paper_id: "p1",
                  title: "Single-Agent Research Ingestion Bottlenecks",
                  passage: "traditional single-agent architectures suffer from persistent processing bottlenecks under multi-document ingestion splits."
                },
                {
                  paper_id: "p2",
                  title: "Collaborative Agent Systems in Bioinformatics",
                  passage: "prior setups evaluated single-user static nodes and failed to integrate multi-agent collaborative consensus filters."
                }
              ]
            }
          }
        ],
        experiments: [
          { hypothesis_statement: "If a research operating system coordinates multiple parallel parsing agents...", title: "Multi-Agent Consensus Evaluation", variables: { independent: "Agent count (1 vs 6 parallel)", dependent: "Parsing coverage (%) and alignment metrics", controlled: "Gemini 2.5 Pro model temperatures" }, suggested_datasets: ["S2ORC Open Academic Corpus", "arXiv Metadata dataset"], methodology: ["Step 1: Ingest 100 papers on both systems.", "Step 2: Compute BLEU summary accuracy comparisons."], evaluation_metrics: ["Cosine similarity metrics", "BLEU-4 validation"], confidence_score: 86 }
        ],
        reports: {
          abstract: "We present ScholarMind, an advanced Research Operating System that coordinates multiple specialized agents. Current research approaches focus heavily on single-agent setups, leaving collaborative synthesis neglected. Our empirical trials show highly novel gains...",
          literature_review: "Prior works by Carter et al. (2024) evaluate single-agent pipelines showing severe latency. Conversely, Zhao & Patel (2025) proposed biological grid agents but omitted cross-domain synthesis. This literature comparison isolates a profound integration gap...",
          methodology: "We mathematically formalize our hypothesis using parallel state variables. In particular, we execute a spiral layout React Flow canvas to map relationships dynamically across Methods and Limitations...",
          future_work: "Future iterations will scale this framework to execute automated code executions for testing model benchmarks."
        },
        contradictions: [
          {
            papers: ["Single-Agent Ingestion", "Collaborative Agent Systems"],
            subject: "Parallel processing efficiency constraints",
            finding_a: "Decentralized pipelines scale linearly showing negligible latency.",
            finding_b: "Decentralized consensus overhead triggers exponential processing delay.",
            analysis: "The disagreement arises from the type of consensus network utilized; Paper A leverages zero-knowledge verification flags, whereas Paper B relies on heavy synchrony barriers, inducing substantial communication overhead."
          }
        ],
        trends: {
          growth_rate: "Exponential Growth",
          emerging_directions: ["Collaborative Multi-Agent Networks", "Decentralized Consensus RAG", "Dynamic Context Mapping"],
          predictions: [
            "AI agents will transition from autonomous task solvers to federated collaborative networks by late 2026.",
            "Dynamic peer-review simulation bounds will completely automate preliminary draft verification before journal submissions."
          ]
        },
        benchmarks: {
          gap_quality: 85,
          novelty: 90,
          scientific_rigor: 88,
          reproducibility: 85,
          feasibility: 80,
          feedback: "The proposed multi-agent framework shows exceptional structural coherence and directly solves a critical parsing bottleneck documented in modern single-agent RAG setups.",
          warnings: [
            "Controlled variables: temperature parameter for consensus voting is not fully detailed in methodology.",
            "Evaluation protocol lacks an explicit fallback mechanism for edge-case parsing failures."
          ]
        },
        debate_transcript: [
          {
            speaker: "Reviewer Agent",
            message: "While the multi-agent design seems novel, you've completely failed to address the consensus communication overhead. Why would 6 parallel agents not trigger a massive latency penalty?"
          },
          {
            speaker: "Researcher Agent",
            message: "We address the latency bottleneck by introducing a hierarchical state broker where sub-agents execute parallel, stateless map partitions. High-overhead consensus checks are restricted to a lightweight asynchronous validation ring."
          }
        ],
        copilot_history: [
          {
            speaker: "copilot",
            message: "Hello! I am your ScholarMind Research Co-Pilot. I've indexed your current workspace documents and am ready to help you analyze gaps, forecast trends, or review experimental layouts.",
            timestamp: new Date().toISOString()
          }
        ]
      };
      setSessions([mockSess]);
      setCurrentSession(mockSess);
      setSelectedGap(mockSess.gaps[0]);
      setSelectedHypothesis(mockSess.hypotheses[0]);
      
      // Default Mock React Flow Graph
      setGraphData({
        nodes: [
          { id: "root", type: "input", data: { label: "Multi-Agent Research OS" }, position: { x: 250, y: 5 }, style: { background: "#1e1b4b", border: "1px solid #6366f1", color: "#fff" } },
          { id: "p1", data: { label: "Paper: Ingestion Bottlenecks" }, position: { x: 100, y: 100 }, style: { background: "#0f172a", border: "1px solid #14b8a6", color: "#fff" } },
          { id: "p2", data: { label: "Paper: Collaborative Bioinformatics" }, position: { x: 400, y: 100 }, style: { background: "#0f172a", border: "1px solid #14b8a6", color: "#fff" } },
          { id: "gap", data: { label: "Gap: Multi-Agent Coordination" }, position: { x: 250, y: 200 }, style: { background: "#31102f", border: "1px solid #d946ef", color: "#fff" }, className: "active-pulse" }
        ],
        edges: [
          { id: "e1", source: "root", target: "p1", animated: true, style: { stroke: "#6366f1" } },
          { id: "e2", source: "root", target: "p2", animated: true, style: { stroke: "#6366f1" } },
          { id: "e3", source: "p1", target: "gap", animated: true, style: { stroke: "#d946ef" } },
          { id: "e4", source: "p2", target: "gap", animated: true, style: { stroke: "#d946ef" } }
        ]
      });
    }
  };

  const loadGraph = async (sessId: string) => {
    try {
      const res = await fetch(`${API_BASE}/graph/${sessId}`);
      if (res.ok) {
        const data = await res.json();
        // Convert raw backend nodes/edges to styled React Flow models
        const flowNodes = data.nodes.map((node: any) => {
          let borderCol = "#6366f1"; // Default Indigo
          let bgCol = "#121b2d";
          
          if (node.type === "Paper") {
            borderCol = "#14b8a6"; // Emerald
          } else if (node.type === "Method") {
            borderCol = "#a855f7"; // Purple
          } else if (node.type === "Dataset") {
            borderCol = "#3b82f6"; // Blue
          } else if (node.type === "Finding") {
            borderCol = "#f59e0b"; // Amber
          } else if (node.type === "Limitation") {
            borderCol = "#ec4899"; // Pink
          }

          return {
            id: node.id,
            data: { label: `${node.type}: ${node.label}` },
            position: node.position || { x: Math.random() * 400 + 100, y: Math.random() * 300 + 100 },
            style: { 
              background: bgCol, 
              border: `2.5px solid ${borderCol}`, 
              color: "#f8fafc",
              padding: "10px",
              borderRadius: "8px",
              fontSize: "11px",
              fontWeight: "600",
              boxShadow: "0 4px 12px rgba(0,0,0,0.45)"
            },
            className: node.type === "Limitation" ? "active-pulse" : ""
          };
        });

        const validatedEdges = (data.edges || []).map((edge: any, idx: number) => ({
          ...edge,
          id: edge.id || `edge_auto_${edge.source}_${edge.target}_${idx}`,
          type: edge.type || "smoothstep",
          animated: edge.animated !== undefined ? edge.animated : true,
          style: edge.style || { stroke: "#14b8a6", strokeWidth: 2 }
        }));

        setGraphData({
          nodes: flowNodes,
          edges: validatedEdges
        });
      }
    } catch (e) {
      console.log("Graph fetch skipped in offline presentation.");
    }
  };

  useEffect(() => {
    loadSessions();
  }, []);

  const handleSelectSession = (session: any) => {
    setCurrentSession(session);
    loadGraph(session.id);
    setSelectedPaper(null);
    setSelectedPaperText("");
    if (session.gaps && session.gaps.length > 0) {
      setSelectedGap(session.gaps[0]);
    } else {
      setSelectedGap(null);
    }
    if (session.hypotheses && session.hypotheses.length > 0) {
      setSelectedHypothesis(session.hypotheses[0]);
    } else {
      setSelectedHypothesis(null);
    }
    addLog(`Switched research workspace to: "${session.topic}"`);
  };

  const handleCreateSession = async (topic: string) => {
    try {
      const res = await fetch(`${API_BASE}/sessions/create`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic })
      });
      if (res.ok) {
        const data = await res.json();
        addLog(`Created new Research Session: "${topic}"`);
        loadSessions(data.id);
      }
    } catch (e) {
      // Offline fallback creation
      const offlineId = `sess-${Date.now().toString().slice(-4)}`;
      const offlineSess = {
        id: offlineId,
        topic,
        timestamp: new Date().toISOString(),
        papers: [],
        gaps: [],
        hypotheses: [],
        experiments: [],
        reports: { abstract: "", literature_review: "", methodology: "", future_work: "" }
      };
      setSessions(prev => [offlineSess, ...prev]);
      setCurrentSession(offlineSess);
      setGraphData({ nodes: [], edges: [] });
      addLog(`Offline simulated session created: "${topic}"`);
    }
  };

  // Upload Paper Action
  const handleUploadPaper = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFile || !currentSession) return;

    setIsUploading(true);
    addLog(`Ingesting PDF file: "${uploadFile.name}"...`);

    const formData = new FormData();
    formData.append("session_id", currentSession.id);
    formData.append("file", uploadFile);

    try {
      const res = await fetch(`${API_BASE}/ingest/upload`, {
        method: "POST",
        body: formData
      });

      if (res.ok) {
        const updatedSess = await res.json();
        setCurrentSession(updatedSess);
        
        // Update session in list
        setSessions(prev => prev.map(s => s.id === updatedSess.id ? updatedSess : s));
        loadGraph(updatedSess.id);
        
        addLog(`Successfully ingested paper and generated vector chunks in ChromaDB.`);
        setUploadFile(null);
      } else {
        const err = await res.json();
        addLog(`Ingestion error: ${err.detail || "Unknown parsing error."}`);
      }
    } catch (e) {
      // Simulated upload if offline
      addLog("Offline mode: Simulated successful PDF parsing.");
      const mockPaper = {
        id: `p-${Date.now().toString().slice(-3)}`,
        title: uploadFile.name.replace(".pdf", ""),
        authors: "Ingested Researcher",
        journal: "Local Workspace",
        year: 2026,
        abstract: "Simulated paper parsed in offline presentation mode. Run backend API to enable full Gemini vector embeddings extraction."
      };
      
      const updatedMockSess = {
        ...currentSession,
        papers: [...currentSession.papers, mockPaper]
      };
      
      setCurrentSession(updatedMockSess);
      setSessions(prev => prev.map(s => s.id === currentSession.id ? updatedMockSess : s));
      
      // Update local mock graph
      const newGraphNode = {
        id: mockPaper.id,
        data: { label: `Paper: ${mockPaper.title}` },
        position: { x: Math.random() * 200 + 200, y: Math.random() * 200 + 100 },
        style: { background: "#121b2d", border: "2.5px solid #14b8a6", color: "#fff", padding: "10px", borderRadius: "8px", fontSize: "11px", fontWeight: "600" }
      };
      setGraphData(prev => ({
        nodes: [...prev.nodes, newGraphNode],
        edges: [...prev.edges, { id: `e-${mockPaper.id}`, source: "root", target: mockPaper.id, animated: true, style: { stroke: "#14b8a6" } }]
      }));
      setUploadFile(null);
    } finally {
      setIsUploading(false);
    }
  };

  const handleRunAgents = async () => {
    if (!currentSession) return;
    setIsLoading(true);
    setPipelineStatus("running");
    addLog("Initializing Dynamic Agent Graph flow (Research -> Lit Review -> Gap Concurrently)...");
    
    try {
      const res = await fetch(`${API_BASE}/agents/run?session_id=${currentSession.id}`, {
        method: "POST"
      });
      
      if (res.ok) {
        addLog("Agents executing in background. Streaming logs to visual control center...");
        pollStatus();
      }
    } catch (e) {
      // Simulated agent execution offline
      setTimeout(() => {
        addLog("[Literature Agent] Synthesized multi-paper vector similarities.");
        addLog("[Gap Discovery Agent] Isolating unaddressed cooperative educational loops...");
        addLog("[Hypothesis Agent] Proposed testable collaborative agent consensus hypothesis.");
        addLog("[Experiment Agent] Formulated BLEU accuracy control design.");
        addLog("[Publication Agent] Synthesized publication markdown chapters successfully.");
        
        const offlineUpdated = {
          ...currentSession,
          gaps: [
            { 
              title: "Collaborative Multi-Agent Integration", 
              description: "Most studies evaluate single-agent systems. No work explores collaborative multi-agent educational assistants.", 
              contribution: "Multi-Agent AI Tutor Framework", 
              confidence_score: 82, 
              rationale: "Evaluations in Paper #1 only cover single-user schemas and Paper #2 focuses solely on biology data grids.",
              evidence_papers: ["p1", "p2"],
              supporting_passages: [
                "traditional single-agent architectures suffer from persistent processing bottlenecks under multi-document ingestion splits.",
                "prior setups evaluated single-user static nodes and failed to integrate multi-agent collaborative consensus filters."
              ]
            },
            { 
              title: "Cross-Domain Semantic Mapping", 
              description: "Existing frameworks lack real-time alignment grids for dynamically changing academic domains.", 
              contribution: "Real-Time Context Mapping Engine", 
              confidence_score: 76, 
              rationale: "Model evaluation sweeps are static and miss streaming updates.",
              evidence_papers: ["p2"],
              supporting_passages: [
                "prior setups evaluated single-user static nodes and failed to integrate multi-agent collaborative consensus filters."
              ]
            }
          ],
          hypotheses: [
            { 
              gap_title: "Collaborative Multi-Agent Integration", 
              statement: "If a research operating system coordinates multiple parallel parsing agents, then metadata coverage increases by over 18% with zero validation drift.", 
              rationale: "By parallelizing abstract summary splits, cross-agent consensus cleans noisy tags.", 
              novelty_score: 8.5, 
              novelty_rationale: "Fuses collaborative multi-agent orchestration theories with semantic citation analysis.", 
              confidence_score: 88,
              citations: ["Single-Agent Research Ingestion Bottlenecks", "Collaborative Agent Systems in Bioinformatics"],
              suggested_datasets: ["S2ORC Open Academic Corpus", "arXiv Metadata dataset"],
              suggested_benchmarks: ["MMLU (Massive Multitask Language Understanding)", "GSM8K math corpus"],
              suggested_metrics: ["BLEU-4 Validation Accuracy", "Semantic Cosine Similarity"],
              baselines: ["GPT-4o (baseline single-agent)", "Gemini 2.5 Pro (vanilla RAG)"],
              lineage: {
                gap_title: "Collaborative Multi-Agent Integration",
                supporting_findings: [
                  "Single-agent pipelines fail under nested document branches.",
                  "Multi-agent collaborative structures optimize validation bounds."
                ],
                evidence_papers: [
                  {
                    paper_id: "p1",
                    title: "Single-Agent Research Ingestion Bottlenecks",
                    passage: "traditional single-agent architectures suffer from persistent processing bottlenecks under multi-document ingestion splits."
                  },
                  {
                    paper_id: "p2",
                    title: "Collaborative Agent Systems in Bioinformatics",
                    passage: "prior setups evaluated single-user static nodes and failed to integrate multi-agent collaborative consensus filters."
                  }
                ]
              }
            }
          ],
          experiments: [
            { hypothesis_statement: "If a research operating system coordinates multiple parallel parsing agents...", title: "Multi-Agent Consensus Evaluation", variables: { independent: "Agent count (1 vs 6 parallel)", dependent: "Parsing coverage (%) and alignment metrics", controlled: "Gemini 2.5 Pro model temperatures" }, suggested_datasets: ["S2ORC Open Academic Corpus", "arXiv Metadata dataset"], methodology: ["Step 1: Ingest 100 papers on both systems.", "Step 2: Compute BLEU summary accuracy comparisons."], evaluation_metrics: ["Cosine similarity metrics", "BLEU-4 validation"], confidence_score: 86 }
          ],
          reports: {
            abstract: "We present ScholarMind, an advanced Research Operating System that coordinates multiple specialized agents. Current research approaches focus heavily on single-agent setups, leaving collaborative synthesis neglected. Our empirical trials show highly novel gains...",
            literature_review: "Prior works by Carter et al. (2024) evaluate single-agent pipelines showing severe latency. Conversely, Zhao & Patel (2025) proposed biological grid agents but omitted cross-domain synthesis. This literature comparison isolates a profound integration gap...",
            methodology: "We mathematically formalize our hypothesis using parallel state variables. In particular, we execute a spiral layout React Flow canvas to map relationships dynamically across Methods and Limitations...",
            future_work: "Future iterations will scale this framework to execute automated code executions for testing model benchmarks."
          },
          contradictions: [
            {
              papers: ["Single-Agent Ingestion", "Collaborative Agent Systems"],
              subject: "Parallel processing efficiency constraints",
              finding_a: "Decentralized pipelines scale linearly showing negligible latency.",
              finding_b: "Decentralized consensus overhead triggers exponential processing delay.",
              analysis: "The disagreement arises from the type of consensus network utilized; Paper A leverages zero-knowledge verification flags, whereas Paper B relies on heavy synchrony barriers, inducing substantial communication overhead."
            }
          ],
          trends: {
            growth_rate: "Exponential Growth",
            emerging_directions: ["Collaborative Multi-Agent Networks", "Decentralized Consensus RAG", "Dynamic Context Mapping"],
            predictions: [
              "AI agents will transition from autonomous task solvers to federated collaborative networks by late 2026.",
              "Dynamic peer-review simulation bounds will completely automate preliminary draft verification before journal submissions."
            ]
          },
          benchmarks: {
            gap_quality: 85,
            novelty: 90,
            scientific_rigor: 88,
            reproducibility: 85,
            feasibility: 80,
            feedback: "The proposed multi-agent framework shows exceptional structural coherence and directly solves a critical parsing bottleneck documented in modern single-agent RAG setups.",
            warnings: [
              "Controlled variables: temperature parameter for consensus voting is not fully detailed in methodology.",
              "Evaluation protocol lacks an explicit fallback mechanism for edge-case parsing failures."
            ]
          },
          debate_transcript: [
            {
              speaker: "Reviewer Agent",
              message: "While the multi-agent design seems novel, you've completely failed to address the consensus communication overhead. Why would 6 parallel agents not trigger a massive latency penalty?"
            },
            {
              speaker: "Researcher Agent",
              message: "We address the latency bottleneck by introducing a hierarchical state broker where sub-agents execute parallel, stateless map partitions. High-overhead consensus checks are restricted to a lightweight asynchronous validation ring."
            }
          ],
          copilot_history: [
            {
              speaker: "copilot",
              message: "Hello! I am your ScholarMind Research Co-Pilot. I've indexed your current workspace documents and am ready to help you analyze gaps, forecast trends, or review experimental layouts.",
              timestamp: new Date().toISOString()
            }
          ]
        };
        
        setCurrentSession(offlineUpdated);
        setSessions(prev => prev.map(s => s.id === currentSession.id ? offlineUpdated : s));
        setPipelineStatus("completed");
        setIsLoading(false);
        if (offlineUpdated.gaps && offlineUpdated.gaps.length > 0) setSelectedGap(offlineUpdated.gaps[0]);
        if (offlineUpdated.hypotheses && offlineUpdated.hypotheses.length > 0) setSelectedHypothesis(offlineUpdated.hypotheses[0]);
        addLog("Agents pipeline completed. Discovered gaps and novelty scores committed to memory.");
      }, 3000);
    }
  };

  const pollStatus = async () => {
    const interval = setInterval(async () => {
      try {
        const res = await fetch(`${API_BASE}/agents/status/${currentSession.id}`);
        if (res.ok) {
          const data = await res.json();
          setPipelineStatus(data.status);
          
          if (data.status === "completed" || data.status.startsWith("failed")) {
            clearInterval(interval);
            setIsLoading(false);
            
            // Reload entire session workspace to show outcomes
            const sessRes = await fetch(`${API_BASE}/sessions/${currentSession.id}`);
            if (sessRes.ok) {
              const updatedSess = await sessRes.json();
              setCurrentSession(updatedSess);
              setSessions(prev => prev.map(s => s.id === updatedSess.id ? updatedSess : s));
              loadGraph(updatedSess.id);
              if (updatedSess.gaps && updatedSess.gaps.length > 0) setSelectedGap(updatedSess.gaps[0]);
              if (updatedSess.hypotheses && updatedSess.hypotheses.length > 0) setSelectedHypothesis(updatedSess.hypotheses[0]);
            }
            addLog(`Multi-agent pipeline completed with status: ${data.status.toUpperCase()}`);
          } else {
            addLog(`Pipeline status: ${data.status.toUpperCase()}...`);
          }
        }
      } catch (e) {
        clearInterval(interval);
        setIsLoading(false);
      }
    }, 2500);
  };

  const selectPaperForReview = async (paper: any) => {
    setSelectedPaper(paper);
    setSelectedPaperText("Loading full document text extraction...");
    try {
      // Dynamically fetch full parsed text from backend database
      const res = await fetch(`${API_BASE}/sessions/paper/${paper.id}`);
      if (res.ok) {
        const data = await res.json();
        setSelectedPaperText(data.parsed_text);
      }
    } catch {
      // Offline fallback text
      setSelectedPaperText(`[DOCUMENT ANALYSIS CARD]\n\nTitle: ${paper.title}\nAuthors: ${paper.authors}\nPublished in: ${paper.journal} (${paper.year})\n\n[Extracted Abstract]\n${paper.abstract}\n\n[SYSTEM NOTE]\nRun the FastAPI server locally to parse full PDF page buffers and review raw document characters.`);
    }
  };

  const handleSendCopilotMessage = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!copilotMessage.trim() || !currentSession) return;

    const userText = copilotMessage.trim();
    setCopilotMessage("");
    setCopilotLoading(true);

    // Optimistically update local UI history
    const tempMessage = { speaker: "user", message: userText, timestamp: new Date().toISOString() };
    const updatedHistory = [...(currentSession.copilot_history || []), tempMessage];
    
    const updatedSession = { ...currentSession, copilot_history: updatedHistory };
    setCurrentSession(updatedSession);
    setSessions(prev => prev.map(s => s.id === currentSession.id ? updatedSession : s));

    try {
      const res = await fetch(`${API_BASE}/sessions/copilot`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ session_id: currentSession.id, message: userText })
      });

      if (res.ok) {
        const data = await res.json();
        const nextSession = { ...currentSession, copilot_history: data.history };
        setCurrentSession(nextSession);
        setSessions(prev => prev.map(s => s.id === currentSession.id ? nextSession : s));
        addLog("Co-Pilot response received.");
      } else {
        addLog("Co-Pilot endpoint returned error.");
      }
    } catch (e) {
      addLog("Offline mode: Simulated Co-Pilot reply.");
      // Offline fallback simulated response
      setTimeout(() => {
        const mockReply = {
          speaker: "copilot",
          message: `Regarding your topic "${currentSession.topic}", I've analyzed your literature references. The proposed concept is highly novel, but to maximize rigor, you should control for model context length bias and run evaluation sweeps on MMLU and WinoBias baselines.`,
          timestamp: new Date().toISOString()
        };
        const finalHistory = [...updatedHistory, mockReply];
        const offlineSession = { ...currentSession, copilot_history: finalHistory };
        setCurrentSession(offlineSession);
        setSessions(prev => prev.map(s => s.id === currentSession.id ? offlineSession : s));
      }, 1000);
    } finally {
      setCopilotLoading(false);
    }
  };

  // ==========================================
  // Layout views rendering
  // ==========================================

  return (
    <div className="flex h-screen overflow-hidden bg-background text-foreground">
      {/* Sidebar Navigation */}
      <Sidebar 
        currentTab={currentTab}
        setCurrentTab={setCurrentTab}
        sessions={sessions}
        currentSession={currentSession}
        onSelectSession={handleSelectSession}
        onCreateSession={handleCreateSession}
      />

      {/* Main Content Dashboard Wrapper */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden bg-slate-950/20">
        
        {/* Top Header Navigation bar */}
        <header className="h-16 border-b border-white/5 px-8 flex items-center justify-between bg-slate-900/10 backdrop-blur-md">
          <div className="flex items-center gap-4">
            <span className="text-sm font-semibold tracking-wide text-white">
              {currentSession ? `Topic: ${currentSession.topic}` : "No Active Research Session"}
            </span>
          </div>
          
          <div className="flex items-center gap-6">
            <div className="flex items-center gap-1.5 px-3 py-1 rounded-full bg-slate-900/80 border border-white/5 text-[10px] text-teal-400 font-semibold tracking-wider uppercase">
              <span className="w-1.5 h-1.5 rounded-full bg-teal-400 animate-ping"></span>
              <span>API Gateway Online</span>
            </div>
            
            <button 
              onClick={() => loadSessions(currentSession?.id)}
              className="p-2 hover:bg-white/5 rounded-lg text-slate-400 hover:text-white transition-all cursor-pointer"
              title="Reload data"
            >
              <RefreshCw size={15} />
            </button>
          </div>
        </header>

        {/* Dashboard Tab Panels */}
        <div className="flex-1 overflow-y-auto p-8">
          
          {/* TAB 1: OVERVIEW */}
          {currentTab === "overview" && currentSession && (
            <div className="space-y-8">
              
              {/* Top Summary Metrics Cards */}
              <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                
                <div className="glass-panel p-6 rounded-xl flex items-center justify-between border-l-2 border-teal-400 glass-card-hover">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-1">Ingested Papers</span>
                    <span className="text-3xl font-extrabold text-white">{currentSession.papers?.length || 0}</span>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-teal-500/10 flex items-center justify-center text-teal-400">
                    <FileCheck size={20} />
                  </div>
                </div>

                <div className="glass-panel p-6 rounded-xl flex items-center justify-between border-l-2 border-pink-500 glass-card-hover">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-1">Discovered Gaps</span>
                    <span className="text-3xl font-extrabold text-white">{currentSession.gaps?.length || 0}</span>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-pink-500/10 flex items-center justify-center text-pink-400">
                    <Layers size={20} />
                  </div>
                </div>

                <div className="glass-panel p-6 rounded-xl flex items-center justify-between border-l-2 border-purple-500 glass-card-hover">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-1">Hypotheses Novelty</span>
                    <span className="text-3xl font-extrabold text-white">
                      {currentSession.hypotheses?.length > 0 ? `${currentSession.hypotheses[0].novelty_score}/10` : "0/10"}
                    </span>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-purple-500/10 flex items-center justify-center text-purple-400">
                    <Award size={20} />
                  </div>
                </div>

                <div className="glass-panel p-6 rounded-xl flex items-center justify-between border-l-2 border-blue-500 glass-card-hover">
                  <div>
                    <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block mb-1">Pipeline Soundness</span>
                    <span className="text-3xl font-extrabold text-white">
                      {currentSession.gaps?.length > 0 ? `${currentSession.gaps[0].confidence_score}%` : "0%"}
                    </span>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-blue-500/10 flex items-center justify-center text-blue-400">
                    <TrendingUp size={20} />
                  </div>
                </div>

              </div>

              {/* Main Panel grid - Row 1 */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                {/* Ingested list overview */}
                <div className="lg:col-span-2 glass-panel p-6 rounded-xl space-y-6">
                  <h3 className="text-sm font-bold text-white uppercase tracking-wider border-b border-white/5 pb-3">
                    Session Library References
                  </h3>
                  
                  {currentSession.papers?.length === 0 ? (
                    <div className="py-12 text-center text-slate-500 text-xs flex flex-col items-center gap-3">
                      <AlertCircle size={32} className="text-slate-600" />
                      <span>No references uploaded yet. Switch to the Research Workspace tab to ingest papers.</span>
                    </div>
                  ) : (
                    <div className="divide-y divide-white/5">
                      {currentSession.papers.map((paper: any) => (
                        <div key={paper.id} className="py-4 first:pt-0 last:pb-0 flex items-start gap-4">
                          <div className="w-10 h-10 rounded bg-slate-800 flex items-center justify-center text-teal-400 font-bold text-xs shrink-0">
                            PDF
                          </div>
                          <div className="min-w-0 flex-1">
                            <h4 className="font-semibold text-xs text-white truncate">{paper.title}</h4>
                            <p className="text-[10px] text-slate-400 mt-1 truncate">{paper.authors} &bull; {paper.journal} ({paper.year})</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Scientific Trend Forecast */}
                <div className="glass-panel p-6 rounded-xl space-y-5">
                  <div className="flex items-center justify-between border-b border-white/5 pb-3">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <TrendingUp size={14} className="text-teal-400" />
                      <span>Scientific Trend Forecast</span>
                    </h3>
                    <span className={`px-2 py-0.5 rounded-full text-[9px] uppercase font-bold border ${
                      currentSession.trends?.growth_rate === 'Exponential Growth' || currentSession.trends?.growth_rate === 'Exponential' || currentSession.trends?.growth_rate === 'High Growth'
                        ? 'bg-teal-500/10 border-teal-500/35 text-teal-400'
                        : 'bg-indigo-500/10 border-indigo-500/35 text-indigo-400'
                    }`}>
                      {currentSession.trends?.growth_rate || "Emerging"}
                    </span>
                  </div>
                  
                  <div className="space-y-4 text-xs">
                    {currentSession.trends?.emerging_directions && currentSession.trends.emerging_directions.length > 0 ? (
                      <div className="space-y-2">
                        <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">Emerging Subfields</span>
                        <div className="flex flex-wrap gap-2">
                          {currentSession.trends.emerging_directions.map((sub: string, subIdx: number) => (
                            <span key={subIdx} className="bg-slate-900 border border-white/5 px-2 py-1 rounded text-[10px] text-slate-300">
                              {sub}
                            </span>
                          ))}
                        </div>
                      </div>
                    ) : (
                      <p className="text-[10px] text-slate-500">Run agents to forecast emerging directions.</p>
                    )}

                    {currentSession.trends?.predictions && currentSession.trends.predictions.length > 0 ? (
                      <div className="space-y-2 pt-2 border-t border-white/5">
                        <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold block mb-1">Trajectory Projections</span>
                        <ul className="space-y-1.5 list-disc pl-4 text-slate-300 text-[11px]">
                          {currentSession.trends.predictions.map((pred: string, predIdx: number) => (
                            <li key={predIdx} className="leading-relaxed">{pred}</li>
                          ))}
                        </ul>
                      </div>
                    ) : (
                      <p className="text-[10px] text-slate-500">No predictions recorded.</p>
                    )}
                  </div>
                </div>

              </div>

              {/* Main Panel grid - Row 2 */}
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
                
                {/* Methodological Contradictions & Clashes */}
                <div className="lg:col-span-2 glass-panel p-6 rounded-xl space-y-6">
                  <div className="flex justify-between items-center border-b border-white/5 pb-3">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <AlertCircle size={14} className="text-pink-500" />
                      <span>Literature Contradictions & Methodological Clashes</span>
                    </h3>
                    <span className="text-[10px] font-mono text-slate-500">Isolating conflicts and technical root causes</span>
                  </div>
                  
                  {!currentSession.contradictions || currentSession.contradictions.length === 0 ? (
                    <div className="py-12 text-center text-slate-500 text-xs flex flex-col items-center justify-center gap-2">
                      <CheckCircle2 size={24} className="text-teal-500/60" />
                      <span>No literature contradictions detected in current memory workspace.</span>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {currentSession.contradictions.map((clash: any, cIdx: number) => (
                        <div key={cIdx} className="bg-slate-900/25 border border-white/5 rounded-xl p-5 space-y-4">
                          <div className="flex justify-between items-start gap-2">
                            <span className="text-xs font-bold text-white uppercase tracking-wide">{clash.subject}</span>
                            <div className="flex flex-wrap gap-1.5 justify-end shrink-0">
                              {clash.papers?.map((pTitle: string, pIdx: number) => (
                                <span key={pIdx} className="bg-slate-950 border border-white/5 px-2 py-0.5 rounded text-[9px] text-slate-400 max-w-[120px] truncate" title={pTitle}>
                                  {pTitle}
                                </span>
                              ))}
                            </div>
                          </div>
                          
                          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs leading-relaxed">
                            <div className="border-l-2 border-teal-400 pl-3">
                              <span className="text-[9px] font-bold text-teal-400 uppercase tracking-widest block mb-1">Position A</span>
                              <p className="text-slate-300">"{clash.finding_a}"</p>
                            </div>
                            <div className="border-l-2 border-pink-500 pl-3">
                              <span className="text-[9px] font-bold text-pink-500 uppercase tracking-widest block mb-1">Position B</span>
                              <p className="text-slate-300">"{clash.finding_b}"</p>
                            </div>
                          </div>
                          
                          <div className="bg-slate-950/40 border border-white/5 rounded-lg p-3.5 text-xs text-slate-300 leading-relaxed font-sans border-t border-indigo-500/30">
                            <span className="text-[9px] font-bold text-indigo-400 uppercase tracking-wider block mb-1">Technical Root Cause Analysis</span>
                            <p className="italic">{clash.analysis}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Research Quality Audit */}
                <div className="glass-panel p-6 rounded-xl space-y-5">
                  <div className="flex justify-between items-center border-b border-white/5 pb-3">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Award size={14} className="text-purple-400" />
                      <span>Research Quality Audit</span>
                    </h3>
                  </div>
                  
                  {!currentSession.benchmarks || !currentSession.benchmarks.gap_quality ? (
                    <div className="py-12 text-center text-slate-500 text-xs">
                      <span>Run agents to compute academic quality and self-evaluation bounds.</span>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      <div className="space-y-3">
                        {[
                          { label: "Novelty Score", val: currentSession.benchmarks.novelty || 85, color: "bg-purple-500 text-purple-400" },
                          { label: "Scientific Rigour", val: currentSession.benchmarks.scientific_rigor || 85, color: "bg-teal-500 text-teal-400" },
                          { label: "Execution Feasibility", val: currentSession.benchmarks.feasibility || 85, color: "bg-blue-500 text-blue-400" },
                          { label: "Reproducibility Rate", val: currentSession.benchmarks.reproducibility || 85, color: "bg-pink-500 text-pink-400" }
                        ].map((score, sIdx) => (
                          <div key={sIdx} className="space-y-1">
                            <div className="flex justify-between text-xs">
                              <span className="text-slate-400 font-medium">{score.label}</span>
                              <span className={`font-bold ${score.color.split(' ')[1]}`}>{score.val}%</span>
                            </div>
                            <div className="w-full bg-slate-900 border border-white/5 h-2 rounded-full overflow-hidden">
                              <div className={`h-full ${score.color.split(' ')[0]} rounded-full`} style={{ width: `${score.val}%` }}></div>
                            </div>
                          </div>
                        ))}
                      </div>
                      
                      <div className="bg-slate-950/40 border border-white/5 rounded-lg p-3 text-[11px] text-slate-300 leading-relaxed font-sans">
                        <span className="text-[9px] uppercase font-bold text-slate-500 tracking-wider block mb-1 font-sans">Qualitative Feedback Summary</span>
                        <p className="text-justify italic font-sans leading-relaxed">"{currentSession.benchmarks.feedback || 'Discovered gaps are academically grounded. Experimental designs utilize complete controls.'}"</p>
                      </div>
                    </div>
                  )}
                </div>

              </div>

            </div>
          )}

          {/* TAB 2: RESEARCH WORKSPACE */}
          {currentTab === "workspace" && currentSession && (
            <div className="space-y-6 h-[calc(100vh-12rem)] min-h-[500px] flex flex-col">
              
              {/* Workspace Subtabs Header Selector */}
              <div className="flex justify-between items-center bg-slate-900/35 border border-white/5 p-3 rounded-xl">
                <div>
                  <h2 className="text-sm font-bold text-white uppercase tracking-wider">Research Operations Workspace</h2>
                  <p className="text-[10px] text-slate-400 mt-0.5">Toggle between raw document parsing and structured causal trace chains.</p>
                </div>
                
                <div className="flex border border-white/10 rounded-lg overflow-hidden bg-slate-950 text-xs">
                  <button
                    onClick={() => setActiveWorkspaceSubTab("reader")}
                    className={`px-4 py-2 font-semibold transition-all cursor-pointer ${activeWorkspaceSubTab === "reader" ? 'bg-teal-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                  >
                    Deep PDF Reader
                  </button>
                  <button
                    onClick={() => setActiveWorkspaceSubTab("lineage")}
                    className={`px-4 py-2 font-semibold transition-all cursor-pointer ${activeWorkspaceSubTab === "lineage" ? 'bg-teal-500 text-slate-950 font-bold' : 'text-slate-400 hover:text-white hover:bg-white/5'}`}
                  >
                    Hypothesis Lineage & Gap Explorer
                  </button>
                </div>
              </div>

              {activeWorkspaceSubTab === "reader" ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1 min-h-0">
                  {/* Left Panel: Library & Ingestion widget */}
                  <div className="glass-panel p-6 rounded-xl flex flex-col min-h-0">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-white/5 pb-3 block mb-4">
                      Reference Ingestion Library
                    </h3>
                    
                    {/* Upload Form */}
                    <form onSubmit={handleUploadPaper} className="space-y-4 mb-6">
                      <div className="border border-dashed border-white/10 hover:border-teal-400/40 rounded-lg p-6 text-center cursor-pointer transition-all flex flex-col items-center justify-center gap-2 relative bg-slate-900/25">
                        <input 
                          type="file" 
                          accept=".pdf"
                          onChange={(e) => setUploadFile(e.target.files?.[0] || null)}
                          className="absolute inset-0 opacity-0 cursor-pointer"
                        />
                        <UploadCloud size={24} className="text-slate-500" />
                        <span className="text-xs font-medium text-slate-300">
                          {uploadFile ? uploadFile.name : "Select academic research PDF"}
                        </span>
                        <span className="text-[10px] text-slate-500">Max size 15MB</span>
                      </div>
                      
                      {uploadFile && (
                        <button
                          type="submit"
                          disabled={isUploading}
                          className="w-full bg-teal-500 hover:bg-teal-600 text-slate-950 font-bold py-2 px-3 rounded-lg text-xs flex items-center justify-center gap-2 shadow-lg cursor-pointer"
                        >
                          {isUploading ? (
                            <>
                              <RefreshCw size={14} className="animate-spin" />
                              <span>Embedding vector blocks...</span>
                            </>
                          ) : (
                            <span>Ingest Reference PDF</span>
                          )}
                        </button>
                      )}
                    </form>

                    {/* Library References */}
                    <div className="flex-1 overflow-y-auto space-y-2">
                      <label className="text-[10px] uppercase text-slate-500 font-bold tracking-wider mb-2 block">
                        Ingested Documents ({currentSession.papers?.length || 0})
                      </label>
                      {currentSession.papers?.map((paper: any) => (
                        <button
                          key={paper.id}
                          onClick={() => selectPaperForReview(paper)}
                          className={`w-full text-left p-3 rounded-lg border text-xs flex items-center justify-between glass-card-hover ${selectedPaper?.id === paper.id ? 'border-teal-500/50 bg-teal-500/5' : 'border-white/5 bg-slate-900/10'}`}
                        >
                          <div className="min-w-0 flex-1 pr-2">
                            <span className="font-semibold text-white truncate block">{paper.title}</span>
                            <span className="text-[10px] text-slate-500 truncate block mt-0.5">{paper.authors} &bull; {paper.year}</span>
                          </div>
                          <Eye size={14} className="text-slate-400 shrink-0" />
                        </button>
                      ))}
                    </div>
                  </div>

                  {/* Right Panel: Deep Reader Workspace */}
                  <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col min-h-0">
                    {selectedPaper ? (
                      <div className="flex-1 flex flex-col min-h-0">
                        {/* Header info */}
                        <div className="border-b border-white/5 pb-4 mb-4 flex justify-between items-start">
                          <div>
                            <h2 className="font-bold text-white text-base leading-snug">{selectedPaper.title}</h2>
                            <p className="text-xs text-slate-400 mt-1">{selectedPaper.authors} &bull; {selectedPaper.journal} ({selectedPaper.year})</p>
                          </div>
                        </div>

                        {/* Parsed content workspace scrollable */}
                        <div className="flex-1 overflow-y-auto bg-slate-950/40 border border-white/5 rounded-lg p-6 font-mono text-xs text-slate-300 leading-relaxed whitespace-pre-wrap select-text">
                          {selectedPaperText}
                        </div>
                      </div>
                    ) : (
                      <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-xs gap-3">
                        <BookOpen size={48} className="text-slate-700" />
                        <span>Select a reference from the library panel to review extracted document segments.</span>
                      </div>
                    )}
                  </div>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1 min-h-0">
                  {/* Left Column: Discovered Gaps & Hypotheses List */}
                  <div className="glass-panel p-6 rounded-xl flex flex-col min-h-0 space-y-4">
                    <div>
                      <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-white/5 pb-2 block mb-3">
                        Intellectual Entities
                      </h3>
                      
                      {/* Discovered Gaps List */}
                      <div className="space-y-2 mb-6">
                        <label className="text-[10px] uppercase text-pink-400 font-bold tracking-wider mb-2 block">
                          Discovered Gaps ({currentSession.gaps?.length || 0})
                        </label>
                        {currentSession.gaps?.length === 0 ? (
                          <div className="text-[10px] text-slate-500 py-2">No research gaps discovered yet. Execute agents.</div>
                        ) : (
                          currentSession.gaps.map((gap: any, gIdx: number) => (
                            <button
                              key={gIdx}
                              onClick={() => {
                                setSelectedGap(gap);
                                setSelectedHypothesis(null);
                              }}
                              className={`w-full text-left p-3 rounded-lg border text-xs flex items-center justify-between transition-all ${selectedGap?.title === gap.title ? 'border-pink-500 bg-pink-500/5 text-white font-bold' : 'border-white/5 bg-slate-900/10 hover:bg-white/5'}`}
                            >
                              <span className="truncate pr-2">{gap.title}</span>
                              <span className="text-[9px] uppercase font-bold text-pink-400 bg-pink-500/10 px-1.5 py-0.5 rounded shrink-0">{gap.confidence_score}%</span>
                            </button>
                          ))
                        )}
                      </div>

                      {/* Discovered Hypotheses List */}
                      <div className="space-y-2">
                        <label className="text-[10px] uppercase text-indigo-400 font-bold tracking-wider mb-2 block">
                          Proposed Hypotheses ({currentSession.hypotheses?.length || 0})
                        </label>
                        {currentSession.hypotheses?.length === 0 ? (
                          <div className="text-[10px] text-slate-500 py-2">No hypotheses formulated yet. Execute agents.</div>
                        ) : (
                          currentSession.hypotheses.map((hypo: any, hIdx: number) => (
                            <button
                              key={hIdx}
                              onClick={() => {
                                setSelectedHypothesis(hypo);
                                setSelectedGap(null);
                              }}
                              className={`w-full text-left p-3 rounded-lg border text-xs flex items-center justify-between transition-all ${selectedHypothesis?.statement === hypo.statement ? 'border-indigo-500 bg-indigo-500/5 text-white font-bold' : 'border-white/5 bg-slate-900/10 hover:bg-white/5'}`}
                            >
                              <span className="truncate pr-2">Hypothesis #{hIdx+1}</span>
                              <span className="text-[9px] uppercase font-bold text-indigo-400 bg-indigo-500/10 px-1.5 py-0.5 rounded shrink-0">{hypo.novelty_score} score</span>
                            </button>
                          ))
                        )}
                      </div>
                    </div>
                  </div>

                  {/* Right Column: Deep details pane */}
                  <div className="lg:col-span-2 glass-panel p-6 rounded-xl flex flex-col min-h-0 overflow-y-auto">
                    {selectedGap && (
                      <div className="space-y-6">
                        <div className="border-b border-white/5 pb-4 flex justify-between items-start">
                          <div>
                            <span className="text-[9px] uppercase font-bold text-pink-400 tracking-wider">Discovered Research Gap</span>
                            <h2 className="text-base font-bold text-white mt-1">{selectedGap.title}</h2>
                          </div>
                          <div className="flex flex-col items-end">
                            <span className="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Gap Confidence</span>
                            <span className="text-base font-black text-pink-400 mt-0.5">{selectedGap.confidence_score}%</span>
                          </div>
                        </div>

                        <div className="space-y-4 text-xs select-text">
                          <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4 space-y-1">
                            <span className="text-[10px] font-bold text-pink-400 uppercase tracking-wider block">Description of Neglected Domain</span>
                            <p className="text-slate-300 leading-relaxed text-justify">{selectedGap.description}</p>
                          </div>

                          <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4 space-y-1">
                            <span className="text-[10px] font-bold text-teal-400 uppercase tracking-wider block">Proposed Contribution to Fill Gap</span>
                            <p className="text-slate-300 leading-relaxed text-justify">{selectedGap.contribution}</p>
                          </div>

                          <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4 space-y-1">
                            <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block">Methodological Neglect Rationale</span>
                            <p className="text-slate-300 leading-relaxed text-justify">{selectedGap.rationale}</p>
                          </div>

                          {selectedGap.supporting_passages && selectedGap.supporting_passages.length > 0 && (
                            <div className="space-y-3 pt-3 border-t border-white/5">
                              <span className="text-[10px] font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                                <FileCheck size={13} className="text-teal-400" />
                                <span>Verifying Evidence Passages Extracted From PDF Vector Space</span>
                              </span>
                              <div className="space-y-3">
                                {selectedGap.supporting_passages.map((psg: string, psIdx: number) => (
                                  <div key={psIdx} className="bg-slate-950/40 rounded-lg p-4 border border-white/5 font-mono text-[10px] text-slate-300 leading-relaxed border-l-2 border-l-teal-400 italic">
                                    "{psg}"
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}

                    {selectedHypothesis && (
                      <div className="space-y-6">
                        <div className="border-b border-white/5 pb-4 flex justify-between items-start">
                          <div>
                            <span className="text-[9px] uppercase font-bold text-indigo-400 tracking-wider">Proposed Causal Hypothesis</span>
                            <h2 className="text-sm font-semibold text-slate-400 mt-0.5">Gap Addressed: "{selectedHypothesis.gap_title}"</h2>
                          </div>
                          <div className="flex flex-col items-end">
                            <span className="text-[9px] text-slate-500 uppercase tracking-widest font-bold">Novelty Grade</span>
                            <span className="text-base font-black text-indigo-400 mt-0.5">{selectedHypothesis.novelty_score}/10.0</span>
                          </div>
                        </div>

                        <div className="space-y-6 text-xs">
                          {/* Traceability Lineage Chain Widget */}
                          <div className="space-y-3">
                            <span className="text-[10px] font-bold text-white uppercase tracking-wider flex items-center gap-1.5">
                              <GitBranch size={13} className="text-teal-400" />
                              <span>Research Lineage Tracking Chain</span>
                            </span>
                            
                            {/* Vertical Chain */}
                            <div className="relative border-l-2 border-dashed border-teal-500/35 ml-4 pl-8 py-2 space-y-8 select-text">
                              
                              {/* Node 1: Hypothesis Statement */}
                              <div className="relative">
                                <div className="absolute -left-[41px] top-1.5 w-5 h-5 rounded-full bg-indigo-500 border border-slate-900 flex items-center justify-center text-[10px] text-white font-bold font-mono">
                                  H
                                </div>
                                <div className="bg-indigo-950/20 border border-indigo-500/20 rounded-xl p-5 space-y-2">
                                  <span className="text-[9px] uppercase font-bold text-indigo-400 tracking-wider block">Formal Hypothesis Statement</span>
                                  <p className="text-xs text-white font-medium leading-relaxed">"{selectedHypothesis.statement}"</p>
                                  <p className="text-[10px] text-slate-400 leading-relaxed italic mt-1">Causal mechanism: {selectedHypothesis.rationale}</p>
                                </div>
                              </div>

                              {/* Node 2: Discovered Gap */}
                              <div className="relative">
                                <div className="absolute -left-[41px] top-1.5 w-5 h-5 rounded-full bg-pink-500 border border-slate-900 flex items-center justify-center text-[10px] text-white font-bold font-mono">
                                  G
                                </div>
                                <div className="bg-pink-950/20 border border-pink-500/20 rounded-xl p-5 space-y-2">
                                  <span className="text-[9px] uppercase font-bold text-pink-400 tracking-wider block">Supporting Research Gap</span>
                                  <h4 className="text-xs font-bold text-white">{selectedHypothesis.lineage?.gap_title || selectedHypothesis.gap_title}</h4>
                                  <p className="text-[11px] text-slate-300 leading-relaxed">
                                    {currentSession.gaps?.find((g: any) => g.title === (selectedHypothesis.lineage?.gap_title || selectedHypothesis.gap_title))?.description || "A critical gap exists in the semantic alignment across diverse parallel multi-agent parsing boundaries."}
                                  </p>
                                </div>
                              </div>

                              {/* Node 3: Supporting Findings */}
                              {selectedHypothesis.lineage?.supporting_findings && selectedHypothesis.lineage.supporting_findings.length > 0 && (
                                <div className="relative">
                                  <div className="absolute -left-[41px] top-1.5 w-5 h-5 rounded-full bg-amber-500 border border-slate-900 flex items-center justify-center text-[10px] text-white font-bold font-mono">
                                    F
                                  </div>
                                  <div className="bg-amber-950/20 border border-amber-500/20 rounded-xl p-5 space-y-2">
                                    <span className="text-[9px] uppercase font-bold text-amber-400 tracking-wider block">Supporting Empirical Findings</span>
                                    <ul className="list-disc pl-4 space-y-1.5 text-slate-300 text-[11px]">
                                      {selectedHypothesis.lineage.supporting_findings.map((f: string, fIdx: number) => (
                                        <li key={fIdx} className="leading-relaxed">{f}</li>
                                      ))}
                                    </ul>
                                  </div>
                                </div>
                              )}

                              {/* Node 4: Cited Reference & Exact Passage */}
                              {selectedHypothesis.lineage?.evidence_papers && selectedHypothesis.lineage.evidence_papers.map((ep: any, epIdx: number) => (
                                <div key={epIdx} className="relative">
                                  <div className="absolute -left-[41px] top-1.5 w-5 h-5 rounded-full bg-teal-400 border border-slate-900 flex items-center justify-center text-[10px] text-slate-950 font-bold font-mono">
                                    P
                                  </div>
                                  <div className="bg-teal-950/10 border border-teal-400/20 rounded-xl p-5 space-y-3">
                                    <div className="flex justify-between items-center">
                                      <span className="text-[9px] uppercase font-bold text-teal-400 tracking-wider">Cited Paper Evidence Source</span>
                                      <span className="text-[9px] font-mono text-slate-500">ID: {ep.paper_id}</span>
                                    </div>
                                    <h4 className="text-xs font-bold text-white">{ep.title}</h4>
                                    
                                    <div className="bg-slate-950/50 rounded-lg p-4 border border-white/5 font-mono text-[10px] text-slate-300 leading-relaxed border-l-2 border-l-teal-400 italic">
                                      "{ep.passage}"
                                    </div>
                                    
                                    <button
                                      onClick={() => {
                                        const matchedPaper = currentSession.papers?.find((p: any) => p.id === ep.paper_id || p.title === ep.title);
                                        if (matchedPaper) {
                                          selectPaperForReview(matchedPaper);
                                          setActiveWorkspaceSubTab("reader");
                                          addLog(`Navigated to reference paper: "${matchedPaper.title}" via Lineage Trace link.`);
                                        } else {
                                          addLog(`Paper "${ep.title}" not found in current session library.`);
                                        }
                                      }}
                                      className="text-[10px] font-semibold text-teal-400 hover:text-teal-300 flex items-center gap-1.5 cursor-pointer hover:underline"
                                    >
                                      <BookOpen size={11} />
                                      <span>Open document source in reader</span>
                                    </button>
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {!selectedGap && !selectedHypothesis && (
                      <div className="flex-1 flex flex-col items-center justify-center text-slate-500 text-xs gap-3">
                        <GitBranch size={48} className="text-slate-700" />
                        <span>Select a Research Gap or proposed Hypothesis on the left panel to explore full causations and lineages.</span>
                      </div>
                    )}
                  </div>
                </div>
              )}

            </div>
          )}

          {/* TAB 3: AGENTS CONTROL CENTER */}
          {currentTab === "agents" && currentSession && (
            <div className="space-y-8">
              
              {/* Top orchestration panel */}
              <div className="glass-panel p-6 rounded-xl flex items-center justify-between">
                <div>
                  <h2 className="text-base font-bold text-white">Dynamic Multi-Agent Graph</h2>
                  <p className="text-xs text-slate-400 mt-1">
                    Orchestrates 6 specialized agents concurrently (Research $\rightarrow$ Literature $\rightarrow$ Gap/Graph Builder $\rightarrow$ Hypothesis $\rightarrow$ Experiment $\rightarrow$ Publication).
                  </p>
                </div>
                
                <button
                  onClick={handleRunAgents}
                  disabled={isLoading || currentSession.papers?.length === 0}
                  className="bg-gradient-to-r from-teal-400 to-indigo-500 hover:from-teal-500 hover:to-indigo-600 text-slate-950 font-bold px-6 py-3 rounded-lg text-xs shadow-xl cursor-pointer flex items-center gap-2"
                >
                  {isLoading ? (
                    <>
                      <RefreshCw size={14} className="animate-spin" />
                      <span>Pipeline executing (Branching Tunnels)...</span>
                    </>
                  ) : (
                    <>
                      <Cpu size={15} />
                      <span>Execute Multi-Agent Research</span>
                    </>
                  )}
                </button>
              </div>

              {/* Grid of the 6 agents */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                
                {[
                  { num: "01", name: "Research Agent", resp: "Parses PDF body paragraphs, extracts structural abstract themes, and indexes clean metadata in SQLite.", status: currentSession.papers?.length > 0 ? "active" : "idle", border: "border-teal-500" },
                  { num: "02", name: "Literature Agent", resp: "Synthesizes cross-document correlations, compares methodologies, and isolates consensus themes.", status: currentSession.gaps?.length > 0 ? "active" : "idle", border: "border-teal-500" },
                  { num: "03", name: "Gap Discovery Agent", resp: "Exposes neglected research boundaries, Restrictive model variables, and theoretical gaps. (40% Engine Focus).", status: currentSession.gaps?.length > 0 ? "active" : "idle", border: "border-pink-500 font-bold animate-pulse" },
                  { num: "04", name: "Hypothesis Agent", resp: "Formulates mathematically testable theories based on Gaps, evaluating structural Novelty Scores.", status: currentSession.hypotheses?.length > 0 ? "active" : "idle", border: "border-purple-500" },
                  { num: "05", name: "Experiment Agent", resp: "Designs experimental frameworks including variables, evaluation parameters, baselines, and corpora.", status: currentSession.experiments?.length > 0 ? "active" : "idle", border: "border-blue-500" },
                  { num: "06", name: "Publication Agent", resp: "Generates high-grade publication drafts (Abstract, Lit Review, Methodology, Future Work) in Markdown.", status: currentSession.reports?.abstract ? "active" : "idle", border: "border-indigo-500" }
                ].map((agent, i) => (
                  <div key={i} className={`glass-panel p-6 rounded-xl border-t-2 ${agent.border} relative overflow-hidden glass-card-hover`}>
                    <div className="absolute top-4 right-6 text-3xl font-extrabold text-slate-800 select-none">
                      {agent.num}
                    </div>
                    <span className="text-[9px] uppercase font-bold px-2 py-0.5 rounded-full bg-slate-900 border border-white/5 tracking-wider block w-max mb-3 text-slate-400">
                      {agent.status.toUpperCase()}
                    </span>
                    <h3 className="font-bold text-white text-sm">{agent.name}</h3>
                    <p className="text-xs text-slate-400 mt-2 leading-relaxed">{agent.resp}</p>
                  </div>
                ))}

              </div>

              {/* Peer-Review Debate Arena */}
              {currentSession.debate_transcript && currentSession.debate_transcript.length > 0 && (
                <div className="glass-panel p-6 rounded-xl space-y-4">
                  <div className="flex justify-between items-center border-b border-white/5 pb-2">
                    <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Cpu size={14} className="text-pink-500" />
                      <span>Academic Peer-Review Debate Arena</span>
                    </h3>
                    <span className="text-[10px] text-teal-400 font-semibold uppercase tracking-wider">Researcher Agent vs Reviewer Agent</span>
                  </div>
                  
                  <div className="space-y-4 max-h-[350px] overflow-y-auto pr-2 select-text">
                    {currentSession.debate_transcript.map((dialog: any, dIdx: number) => {
                      const isReviewer = dialog.speaker === "Reviewer Agent";
                      return (
                        <div key={dIdx} className={`flex gap-3 text-xs leading-relaxed border border-white/5 rounded-xl p-4 ${isReviewer ? 'bg-pink-950/5 border-l-2 border-l-pink-500' : 'bg-teal-950/5 border-l-2 border-l-teal-400'}`}>
                          <span className={`w-8 h-8 rounded-full flex items-center justify-center font-bold text-[10px] shrink-0 ${isReviewer ? 'bg-pink-500/10 text-pink-400 border border-pink-500/35' : 'bg-teal-400/10 text-teal-400 border border-teal-400/35'}`}>
                            {isReviewer ? 'REV' : 'RES'}
                          </span>
                          <div className="space-y-1">
                            <span className={`text-[9px] uppercase font-bold tracking-wider ${isReviewer ? 'text-pink-400' : 'text-teal-400'}`}>
                              {dialog.speaker}
                            </span>
                            <p className="text-slate-300 font-mono text-[11px] leading-relaxed text-justify whitespace-pre-wrap">{dialog.message}</p>
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </div>
              )}

              {/* Console log monitor */}
              <div className="glass-panel p-6 rounded-xl space-y-4">
                <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-white/5 pb-2">
                  System Orchestrator Console Logs
                </h3>
                <div className="h-48 overflow-y-auto bg-slate-950/80 border border-white/5 rounded-lg p-4 font-mono text-[10px] text-teal-400/90 leading-relaxed space-y-2 select-text">
                  {consoleLogs.map((log, idx) => (
                    <div key={idx}>{log}</div>
                  ))}
                </div>
              </div>

            </div>
          )}

          {/* TAB 4: KNOWLEDGE GRAPH */}
          {currentTab === "graph" && currentSession && (
            <div className="glass-panel rounded-xl h-[calc(100vh-12rem)] min-h-[500px] flex flex-col overflow-hidden relative">
              <div className="p-4 border-b border-white/5 bg-slate-900/35 flex justify-between items-center z-10">
                <div>
                  <h2 className="font-bold text-white text-xs uppercase tracking-wider">Session Concept Ontology Map</h2>
                  <span className="text-[9px] text-slate-500">Interactive panning grid mapping entity correlations</span>
                </div>
                <div className="flex gap-4 text-[9px] font-semibold text-slate-400">
                  <div className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-teal-400"></span><span>Paper</span></div>
                  <div className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-purple-400"></span><span>Method</span></div>
                  <div className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-blue-400"></span><span>Dataset</span></div>
                  <div className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-amber-400"></span><span>Finding</span></div>
                  <div className="flex items-center gap-1"><span className="w-2 h-2 rounded bg-pink-400"></span><span>Limitation (Gap)</span></div>
                </div>
              </div>
              
              <div className="flex-1 w-full bg-slate-950/60 relative">
                <ReactFlow 
                  nodes={graphData.nodes} 
                  edges={graphData.edges}
                  fitView
                >
                  <Background color="#1e293b" gap={16} />
                  <Controls />
                  <MiniMap nodeStrokeWidth={3} nodeColor="#1e293b" maskColor="rgba(15,23,42,0.6)" />
                </ReactFlow>
              </div>
            </div>
          )}

          {/* TAB 5: EXPERIMENTS */}
          {currentTab === "experiments" && currentSession && (
            <div className="space-y-8">
              
              {currentSession.experiments?.length === 0 ? (
                <div className="glass-panel py-20 text-center text-slate-500 text-xs flex flex-col items-center gap-3">
                  <Beaker size={48} className="text-slate-700" />
                  <span>No experimental layouts generated yet. Run Multi-Agent Research to compile blueprints.</span>
                </div>
              ) : (
                <div className="space-y-8">
                  
                  {/* Reproducibility Checker Warnings Audits */}
                  {currentSession.benchmarks?.warnings && currentSession.benchmarks.warnings.length > 0 ? (
                    <div className="glass-panel p-5 rounded-xl border border-pink-500/20 bg-pink-500/5 space-y-3">
                      <div className="flex items-center gap-2 text-pink-400 font-bold text-xs uppercase tracking-wider">
                        <AlertCircle size={16} />
                        <span>Reproducibility & Completeness warnings ({currentSession.benchmarks.warnings.length})</span>
                      </div>
                      <p className="text-[11px] text-slate-400 leading-normal">
                        Anonymous Peer Reviewers frequently criticize papers with incomplete experimental setups. The following gaps must be resolved prior to journal submission:
                      </p>
                      <ul className="space-y-1.5 pl-5 list-disc text-xs text-slate-300 select-text">
                        {currentSession.benchmarks.warnings.map((warn: string, wIdx: number) => (
                          <li key={wIdx} className="leading-relaxed">{warn}</li>
                        ))}
                      </ul>
                    </div>
                  ) : currentSession.benchmarks?.gap_quality > 0 ? (
                    <div className="glass-panel p-5 rounded-xl border border-teal-500/20 bg-teal-500/5 flex items-center gap-3">
                      <CheckCircle2 size={18} className="text-teal-400 shrink-0" />
                      <div className="text-xs">
                        <span className="font-bold text-white block uppercase tracking-wide">Reproducibility Verified</span>
                        <span className="text-slate-400 block mt-0.5">Experimental variables and controls meet high-rigor peer-review submission standards. Zero warning flags raised.</span>
                      </div>
                    </div>
                  ) : null}

                  {/* Empirical Testing Protocol / Recommendations from Hypothesis */}
                  {currentSession.hypotheses?.[0] && (
                    <div className="glass-panel p-6 rounded-xl space-y-4">
                      <div className="border-b border-white/5 pb-3">
                        <h3 className="text-xs font-bold text-white uppercase tracking-wider flex items-center gap-2">
                          <Cpu size={14} className="text-indigo-400" />
                          <span>Empirical Baseline & Testing Recommendation Protocol</span>
                        </h3>
                        <p className="text-[10px] text-slate-500 mt-0.5">Rigorous baselines and benchmarks proposed to evaluate the conceptual delta</p>
                      </div>
                      
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 text-xs select-text">
                        <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4 space-y-2">
                          <span className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider block">Recommended Baselines</span>
                          <ul className="space-y-1 text-slate-300">
                            {(currentSession.hypotheses[0].baselines || ["GPT-4o (baseline single-agent)", "Gemini 2.5 Pro (vanilla RAG)"]).map((b: string, idx: number) => (
                              <li key={idx} className="flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-indigo-400 shrink-0"></span>
                                <span>{b}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4 space-y-2">
                          <span className="text-[10px] font-bold text-teal-400 uppercase tracking-wider block">Standard Benchmarks</span>
                          <ul className="space-y-1 text-slate-300">
                            {(currentSession.hypotheses[0].suggested_benchmarks || ["MMLU", "GSM8K math corpus"]).map((b: string, idx: number) => (
                              <li key={idx} className="flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-teal-400 shrink-0"></span>
                                <span>{b}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4 space-y-2">
                          <span className="text-[10px] font-bold text-pink-500 uppercase tracking-wider block">Target Datasets</span>
                          <ul className="space-y-1 text-slate-300">
                            {(currentSession.hypotheses[0].suggested_datasets || ["S2ORC Open Academic Corpus", "arXiv Metadata"]).map((d: string, idx: number) => (
                              <li key={idx} className="flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-pink-500 shrink-0"></span>
                                <span>{d}</span>
                              </li>
                            ))}
                          </ul>
                        </div>

                        <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4 space-y-2">
                          <span className="text-[10px] font-bold text-amber-500 uppercase tracking-wider block">Mathematical Metrics</span>
                          <ul className="space-y-1 text-slate-300">
                            {(currentSession.hypotheses[0].suggested_metrics || ["BLEU Validation Accuracy", "Cosine Similarity"]).map((m: string, idx: number) => (
                              <li key={idx} className="flex items-center gap-1.5">
                                <span className="w-1.5 h-1.5 rounded-full bg-amber-500 shrink-0"></span>
                                <span>{m}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  )}

                  {currentSession.experiments.map((exp: any, idx: number) => (
                    <div key={idx} className="glass-panel p-8 rounded-xl space-y-6">
                      
                      {/* Title block */}
                      <div className="border-b border-white/5 pb-4 flex justify-between items-start">
                        <div>
                          <span className="text-[9px] uppercase font-bold text-teal-400 tracking-wider">
                            Empirical Blueprint Evaluation
                          </span>
                          <h2 className="text-lg font-bold text-white mt-1">{exp.title}</h2>
                          <p className="text-xs text-slate-500 mt-1 italic">Testing: "{exp.hypothesis_statement}"</p>
                        </div>
                        <div className="flex flex-col items-end">
                          <span className="text-[10px] text-slate-500 uppercase tracking-widest font-bold">Soundness Score</span>
                          <span className="text-xl font-black text-teal-400 mt-0.5">{exp.confidence_score}%</span>
                        </div>
                      </div>

                      {/* Variables list */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 select-text">
                        <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4">
                          <span className="text-[10px] font-bold text-teal-400 uppercase tracking-wider block mb-2">Independent Variable</span>
                          <p className="text-xs text-slate-300 leading-relaxed">{exp.variables?.independent || "Agent count (1 vs 6 parallel)"}</p>
                        </div>
                        <div className="bg-slate-950/20 border border-pink-500/20 rounded-lg p-4">
                          <span className="text-[10px] font-bold text-pink-500 uppercase tracking-wider block mb-2">Dependent Variable</span>
                          <p className="text-xs text-slate-300 leading-relaxed">{exp.variables?.dependent || "Parsing coverage (%) and alignment metrics"}</p>
                        </div>
                        <div className="bg-slate-900/35 border border-white/5 rounded-lg p-4">
                          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-wider block mb-2">Controlled Variable</span>
                          <p className="text-xs text-slate-300 leading-relaxed">{exp.variables?.controlled || "Gemini 2.5 Pro model temperatures"}</p>
                        </div>
                      </div>

                      {/* Timeline execution steps */}
                      <div className="space-y-4 pt-4 border-t border-white/5">
                        <h4 className="text-xs font-bold text-white uppercase tracking-wider">
                          Experimental Execution sequence
                        </h4>
                        <div className="space-y-3 select-text">
                          {exp.methodology.map((step: string, sIdx: number) => (
                            <div key={sIdx} className="flex gap-3 text-xs leading-relaxed">
                              <span className="w-5 h-5 rounded-full bg-teal-500/10 border border-teal-500/40 text-teal-400 flex items-center justify-center font-bold text-[10px] shrink-0">
                                {sIdx+1}
                              </span>
                              <p className="text-slate-300 pt-0.5">{step}</p>
                            </div>
                          ))}
                        </div>
                      </div>

                    </div>
                  ))}
                </div>
              )}

            </div>
          )}

          {/* TAB 6: REPORTS */}
          {currentTab === "reports" && currentSession && (
            <div className="space-y-8">
              
              {!currentSession.reports?.abstract ? (
                <div className="glass-panel py-20 text-center text-slate-500 text-xs flex flex-col items-center gap-3">
                  <FileText size={48} className="text-slate-700" />
                  <span>No manuscript sections drafted yet. Run Multi-Agent Research to compile reports.</span>
                </div>
              ) : (
                <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
                  
                  {/* Left Side: Novelty metrics & session overview */}
                  <div className="space-y-6">
                    <div className="glass-panel p-6 rounded-xl space-y-4">
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block">Novelty Evaluation</span>
                      
                      <div className="flex items-center gap-3">
                        <div className="w-14 h-14 rounded-full border-4 border-purple-500/35 border-t-purple-500 flex items-center justify-center font-black text-white text-base">
                          {currentSession.hypotheses?.[0]?.novelty_score || "8.2"}
                        </div>
                        <div>
                          <h4 className="font-bold text-white text-xs">High Novelty Grade</h4>
                          <span className="text-[10px] text-purple-400">Estimated by Gemini 2.5 Pro</span>
                        </div>
                      </div>

                      <p className="text-[10px] text-slate-400 leading-relaxed border-t border-white/5 pt-3">
                        {currentSession.hypotheses?.[0]?.novelty_rationale || "Hypothesis fuses cooperative multi-agent consensus validation directly with vector citation heuristics."}
                      </p>
                    </div>

                    <div className="glass-panel p-6 rounded-xl space-y-4">
                      <span className="text-[10px] text-slate-500 font-bold uppercase tracking-widest block">Soundness Metrics</span>
                      
                      <div className="flex items-center gap-3">
                        <div className="w-14 h-14 rounded-full border-4 border-teal-500/35 border-t-teal-500 flex items-center justify-center font-black text-white text-base">
                          {currentSession.gaps?.[0]?.confidence_score || "82"}%
                        </div>
                        <div>
                          <h4 className="font-bold text-white text-xs">Confidence Soundness</h4>
                          <span className="text-[10px] text-teal-400">Assessed by Gap Agent</span>
                        </div>
                      </div>
                    </div>
                  </div>

                  {/* Right Side: Academic Editor preview */}
                  <div className="lg:col-span-3 glass-panel rounded-xl flex flex-col p-8 space-y-8 bg-slate-950/40 relative overflow-hidden">
                    
                    {/* Manuscript Page styling */}
                    <div className="space-y-8 select-text">
                      <div className="text-center space-y-2 border-b border-white/5 pb-6">
                        <h1 className="font-serif text-xl font-bold text-white uppercase tracking-wider">{currentSession.topic}</h1>
                        <p className="text-[10px] uppercase font-mono tracking-widest text-slate-500">ScholarMind Automated Academic Draft</p>
                      </div>

                      {/* Section 1: Abstract */}
                      <div className="space-y-2">
                        <h3 className="font-bold text-white font-serif text-sm">Abstract</h3>
                        <p className="text-xs text-slate-300 leading-relaxed text-justify first-letter:text-xl first-letter:font-bold first-letter:text-teal-400">
                          {currentSession.reports.abstract}
                        </p>
                      </div>

                      {/* Section 2: Lit Review */}
                      <div className="space-y-2">
                        <h3 className="font-bold text-white font-serif text-sm">1. Introduction & Related Work</h3>
                        <p className="text-xs text-slate-300 leading-relaxed text-justify">
                          {currentSession.reports.literature_review}
                        </p>
                      </div>

                      {/* Section 3: Methodology */}
                      <div className="space-y-2">
                        <h3 className="font-bold text-white font-serif text-sm">2. System Model & Methodology</h3>
                        <p className="text-xs text-slate-300 leading-relaxed text-justify">
                          {currentSession.reports.methodology}
                        </p>
                      </div>

                      {/* Section 4: Future Work */}
                      <div className="space-y-2">
                        <h3 className="font-bold text-white font-serif text-sm">3. Concluding Remarks & Future Vector</h3>
                        <p className="text-xs text-slate-300 leading-relaxed text-justify">
                          {currentSession.reports.future_work}
                        </p>
                      </div>
                    </div>

                  </div>

                </div>
              )}

            </div>
          )}

        </div>

      </main>

      {/* Floating Co-Pilot Toggle Button */}
      {currentSession && (
        <button
          onClick={() => setIsCopilotOpen(true)}
          className="fixed bottom-6 right-6 w-14 h-14 rounded-full bg-gradient-to-tr from-teal-400 to-indigo-500 hover:from-teal-500 hover:to-indigo-600 flex items-center justify-center text-slate-950 font-bold shadow-2xl z-40 transition-all hover:scale-105 active:scale-95 cursor-pointer border border-white/20 active-pulse"
          title="Research Co-Pilot"
        >
          <MessageSquare size={24} />
        </button>
      )}

      {/* Glassmorphic Co-Pilot Drawer */}
      {currentSession && (
        <div className={`fixed inset-y-0 right-0 w-96 bg-slate-900/95 backdrop-blur-2xl border-l border-white/10 shadow-2xl z-50 transform transition-transform duration-300 flex flex-col ${isCopilotOpen ? 'translate-x-0' : 'translate-x-full'}`}>
          {/* Header */}
          <div className="p-4 border-b border-white/5 flex items-center justify-between bg-slate-950/40">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded bg-teal-400/10 flex items-center justify-center text-teal-400">
                <Cpu size={14} />
              </div>
              <div>
                <h3 className="font-bold text-white text-xs uppercase tracking-wider">Research Co-Pilot</h3>
                <span className="text-[9px] text-teal-400 font-semibold uppercase tracking-widest">Active Workspace Advisor</span>
              </div>
            </div>
            <button 
              onClick={() => setIsCopilotOpen(false)} 
              className="p-1 hover:bg-white/5 rounded text-slate-400 hover:text-white transition-all cursor-pointer"
            >
              <X size={16} />
            </button>
          </div>

          {/* Messages Box */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 font-sans text-xs">
            {/* Welcome message if history is empty */}
            {(!currentSession?.copilot_history || currentSession.copilot_history.length === 0) && (
              <div className="text-slate-400 text-justify bg-slate-950/40 border border-white/5 rounded-lg p-3 leading-relaxed space-y-2 select-none font-sans">
                <p className="font-semibold text-white font-sans">Welcome to ScholarMind Co-Pilot!</p>
                <p className="font-sans">I am your session-connected AI research strategist. I have full context of your uploaded papers, discovered gaps, and proposed hypotheses.</p>
                <p className="text-[10px] text-slate-500 font-sans">Ask me to challenge your hypotheses, check for literature contradictions, or brainstorm experimental baselines.</p>
              </div>
            )}

            {/* Render history */}
            {currentSession?.copilot_history?.map((msg: any, mIdx: number) => {
              const isUser = msg.speaker === "user";
              return (
                <div key={mIdx} className={`flex ${isUser ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-lg p-3 leading-relaxed ${isUser ? 'bg-indigo-600/25 border border-indigo-500/20 text-white font-medium font-sans' : 'bg-slate-950/60 border border-white/5 text-slate-300 font-sans'}`}>
                    <span className={`text-[9px] uppercase font-bold tracking-wider block mb-1 ${isUser ? 'text-indigo-300 font-sans' : 'text-teal-400 font-sans'}`}>
                      {isUser ? 'Researcher' : 'Co-Pilot'}
                    </span>
                    <p className="whitespace-pre-wrap leading-relaxed select-text font-sans">{msg.message}</p>
                  </div>
                </div>
              );
            })}

            {copilotLoading && (
              <div className="flex justify-start">
                <div className="bg-slate-950/60 border border-white/5 rounded-lg p-3 flex items-center gap-2 text-slate-400 font-sans">
                  <RefreshCw size={12} className="animate-spin text-teal-400" />
                  <span>Co-Pilot is analyzing literature...</span>
                </div>
              </div>
            )}
          </div>

          {/* Input form */}
          <form onSubmit={handleSendCopilotMessage} className="p-4 border-t border-white/5 bg-slate-950/40 flex gap-2">
            <input
              type="text"
              placeholder="Challenge this hypothesis..."
              value={copilotMessage}
              onChange={(e) => setCopilotMessage(e.target.value)}
              disabled={copilotLoading}
              className="flex-1 bg-slate-950 border border-white/10 text-xs px-3 py-2 rounded-lg text-white focus:outline-none focus:border-teal-400 focus:ring-1 focus:ring-teal-400 font-sans"
            />
            <button
              type="submit"
              disabled={copilotLoading || !copilotMessage.trim()}
              className="p-2 bg-teal-500 hover:bg-teal-600 text-slate-950 rounded-lg cursor-pointer flex items-center justify-center transition-all disabled:opacity-40"
            >
              <Send size={14} />
            </button>
          </form>
        </div>
      )}
    </div>
  );
}
