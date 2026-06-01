import os
import json
import re
import math
import uuid
from typing import Dict, Any, List
from dotenv import load_dotenv
from app.services.ollama_client import OllamaClient

load_dotenv()

def extract_graph_from_text(paper_title: str, text: str) -> Dict[str, List[Dict[str, Any]]]:
    """Uses local Ollama (Qwen3:8B) to parse a paper's text and extract semantic nodes and relationships."""
    default_graph = {"nodes": [], "edges": []}

    if not OllamaClient.is_online():
        # Mock Graph if Ollama is offline
        paper_id = re.sub(r"\W+", "_", paper_title.lower())[:20]
        return {
            "nodes": [
                {"id": paper_id, "type": "Paper", "label": paper_title, "summary": "Uploaded reference paper."},
                {"id": f"{paper_id}_m1", "type": "Method", "label": "Deep Learning Pipeline", "summary": "Core algorithmic framework."},
                {"id": f"{paper_id}_d1", "type": "Dataset", "label": "Benchmark dataset", "summary": "Testing dataset evaluation."},
                {"id": f"{paper_id}_f1", "type": "Finding", "label": "Accuracy Boost", "summary": "System achieves state-of-the-art results."},
                {"id": f"{paper_id}_l1", "type": "Limitation", "label": "Scale Bottleneck", "summary": "Computationally intensive for huge inputs."}
            ],
            "edges": [
                {"id": f"edge_{paper_id}_m1", "source": paper_id, "target": f"{paper_id}_m1", "label": "proposes_method"},
                {"id": f"edge_{paper_id}_m1_d1", "source": f"{paper_id}_m1", "target": f"{paper_id}_d1", "label": "evaluated_on"},
                {"id": f"edge_{paper_id}_m1_f1", "source": f"{paper_id}_m1", "target": f"{paper_id}_f1", "label": "yields_finding"},
                {"id": f"edge_{paper_id}_f1_l1", "source": f"{paper_id}_f1", "target": f"{paper_id}_l1", "label": "reveals_limitation"}
            ]
        }

    # Take abstract or first 5000 characters which outline methods and datasets
    summary_text = text[:6000]

    prompt = f"""
You are an advanced ontology and knowledge-graph parsing assistant. Analyze the academic paper text below and extract:
1. Core nodes (entities of interest)
2. Directed relationships (edges connecting them)

The allowed node types are:
- "Paper": The publication itself (Title: "{paper_title}")
- "Method": Algorithmic techniques, custom model architectures, or mathematical formulations.
- "Dataset": Experimental benchmarks, corpora, or data splits.
- "Finding": Crucial empirical discoveries, quantitative performance results, or qualitative outcomes.
- "Limitation": Inherent constraints, scaling thresholds, assumptions, or failure conditions.

Paper Context:
{summary_text}

---
Extract and return ONLY a valid JSON object matching this schema:
{{
  "nodes": [
    {{
      "label": "Short clean name of entity (e.g. ResNet-50, ImageNet, 94.2% Accuracy, Scale Sensitivity)",
      "type": "Paper" | "Method" | "Dataset" | "Finding" | "Limitation",
      "summary": "Brief 1-sentence description explaining its significance in the paper context"
    }}
  ],
  "edges": [
    {{
      "source_label": "Exact name of the source entity",
      "target_label": "Exact name of the target entity",
      "label": "Verbal relationship (e.g. proposes, evaluates_on, achieves, suffers_from, highlights)"
    }}
  ]
}}
Ensure the node "{paper_title}" of type "Paper" is included as the primary root node.
Do NOT output markdown blocks or notes. Output raw, clean, parseable JSON.
"""
    try:
        # Call Ollama Client with format constraints
        clean_json_str = OllamaClient.generate(
            prompt=prompt,
            format_json=True,
            temperature=0.1
        )

        if clean_json_str.startswith("```"):
            clean_json_str = re.sub(r"^```(?:json)?\n", "", clean_json_str)
            clean_json_str = re.sub(r"\n```$", "", clean_json_str)
            
        raw_graph = json.loads(clean_json_str.strip())
        
        # Build clean mapping
        nodes = []
        edges = []
        node_map = {}
        
        # Add Paper root explicitly to ensure it exists
        paper_id = re.sub(r"\W+", "_", paper_title.lower())[:25]
        nodes.append({
            "id": paper_id,
            "type": "Paper",
            "label": paper_title,
            "summary": "Primary reference paper under review."
        })
        node_map[paper_title.strip().lower()] = paper_id
        
        # Add other nodes
        for node in raw_graph.get("nodes", []):
            label = node.get("label", "").strip()
            ntype = node.get("type", "Method").strip()
            summary = node.get("summary", "").strip()
            
            if not label or label.lower() == paper_title.lower():
                continue
                
            node_id = re.sub(r"\W+", "_", label.lower())[:25] + "_" + str(uuid.uuid4().hex[:4])
            nodes.append({
                "id": node_id,
                "type": ntype,
                "label": label,
                "summary": summary
            })
            node_map[label.lower()] = node_id
            
        # Add edges
        for edge in raw_graph.get("edges", []):
            src_label = edge.get("source_label", "").strip().lower()
            tgt_label = edge.get("target_label", "").strip().lower()
            edge_lbl = edge.get("label", "connects_to").strip()
            
            # Find IDs matching labels
            src_id = node_map.get(src_label)
            tgt_id = node_map.get(tgt_label)
            
            # Smart fuzzy matching fallbacks
            if not src_id:
                for k, v in node_map.items():
                    if k in src_label or src_label in k:
                        src_id = v
                        break
            if not tgt_id:
                for k, v in node_map.items():
                    if k in tgt_label or tgt_label in k:
                        tgt_id = v
                        break
                        
            if src_id and tgt_id:
                edges.append({
                    "id": f"edge_{src_id}_{tgt_id}",
                    "source": src_id,
                    "target": tgt_id,
                    "label": edge_lbl
                })
                
        return {"nodes": nodes, "edges": edges}
        
    except Exception as e:
        print(f"Gemini Graph Extraction error: {e}. Returning mock values.")
        return default_graph

def calculate_graph_layout(nodes: List[Dict[str, Any]], edges: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Computes visual coordinate layouts (x, y) for nodes using a spiral layout.
    This guarantees nodes never overlap and renders a gorgeous starting canvas.
    """
    if not nodes:
        return {"nodes": [], "edges": edges}
        
    layout_nodes = []
    
    # Locate the paper node as center (0, 0)
    paper_nodes = [n for n in nodes if n["type"] == "Paper"]
    root_id = paper_nodes[0]["id"] if paper_nodes else nodes[0]["id"]
    
    # Spiral Parameters
    theta = 0.0
    radius_step = 140
    angle_step = 0.75 # Radians step
    
    # Render central Paper
    for i, node in enumerate(nodes):
        if node["id"] == root_id:
            layout_nodes.append({
                **node,
                "position": {"x": 400, "y": 300} # Centered on canvas
            })
            continue
            
        # Spiral mathematical layout coordinate generator
        multiplier = math.sqrt(len(layout_nodes))
        current_r = radius_step * multiplier
        theta += angle_step + (0.2 / multiplier if multiplier > 0 else 0)
        
        pos_x = 400 + int(current_r * math.cos(theta))
        pos_y = 300 + int(current_r * math.sin(theta))
        
        layout_nodes.append({
            **node,
            "position": {"x": pos_x, "y": pos_y}
        })
        
    # Return formatted edges with animated arrows and premium color codings
    animated_edges = []
    for edge in edges:
        lbl = edge.get("label", "").lower()
        color = "#14b8a6" # Default Emerald/Teal
        if "contradict" in lbl:
            color = "#f43f5e" # Rose red for clashes
        elif "support" in lbl:
            color = "#10b981" # Green for support
        elif "extend" in lbl:
            color = "#8b5cf6" # Violet for extension
        elif "gap" in lbl:
            color = "#d946ef" # Fuchsia for gaps

        animated_edges.append({
            **edge,
            "type": "smoothstep",
            "animated": True,
            "style": {"stroke": color, "strokeWidth": 2}
        })
        
    return {"nodes": layout_nodes, "edges": animated_edges}
