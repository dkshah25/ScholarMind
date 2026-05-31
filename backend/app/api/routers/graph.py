import os
import json
import re
from fastapi import APIRouter, HTTPException
import app.database.db as db
from app.services.knowledge_graph import calculate_graph_layout

router = APIRouter(prefix="/graph", tags=["Knowledge Graph"])

@router.get("/{session_id}")
def get_session_knowledge_graph(session_id: str):
    """
    Retrieves the parsed conceptual entities and semantic edges of a session, 
    perfectly formatted and visual-positioned for Next.js React Flow.
    """
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 1. If we have a saved graph file for this session, load it directly
    graph_file = f"session_graph_{session_id}.json"
    if os.path.exists(graph_file):
        try:
            with open(graph_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed loading graph file {graph_file}: {e}")

    # 2. Otherwise, dynamically generate a default starting graph containing root papers
    nodes = []
    edges = []
    
    if session.papers:
        for i, paper in enumerate(session.papers):
            paper_node_id = paper.id
            nodes.append({
                "id": paper_node_id,
                "type": "Paper",
                "label": paper.title,
                "summary": paper.abstract or "Uploaded publication."
            })
            
        # Compile standard layout coordinates
        return calculate_graph_layout(nodes, edges)

    # 3. Completely empty default state
    return {"nodes": [], "edges": []}
