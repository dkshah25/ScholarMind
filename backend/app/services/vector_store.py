import os
import uuid
import json
import math
from typing import List, Dict, Any
from app.services.embeddings import get_embedding, get_embeddings

# ==========================================
# Self-Healing Optional Import Pattern
# ==========================================
chroma_client = None
try:
    import chromadb
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_db")
    chroma_client = chromadb.PersistentClient(path=CHROMA_DB_PATH)
    print("Using ChromaDB persistent vector database.")
except ImportError:
    print("ChromaDB is not installed. Falling back to local SQLite/JSON Cosine Similarity vector engine.")

def is_chroma_active() -> bool:
    return chroma_client is not None

def get_or_create_collection():
    if not is_chroma_active():
        return None
    return chroma_client.get_or_create_collection(name="scholarmind_papers")

# ==========================================
# Common Text Chunking Service
# ==========================================

def chunk_text(text: str, chunk_size: int = 1200, chunk_overlap: int = 200) -> List[str]:
    """Splits a document text into overlapping character chunks."""
    chunks = []
    if not text.strip():
        return chunks
        
    start = 0
    while start < len(text):
        end = start + chunk_size
        if end >= len(text):
            chunks.append(text[start:])
            break
            
        chunk = text[start:end]
        last_sentence_end = max(chunk.rfind(". "), chunk.rfind("?\n"), chunk.rfind(".\n"))
        if last_sentence_end != -1 and last_sentence_end > chunk_size // 2:
            end = start + last_sentence_end + 1
            
        chunks.append(text[start:end])
        start = end - chunk_overlap
        
    return chunks

# ==========================================
# Pure-Python Cosine Similarity Fallback Engine
# ==========================================

def calculate_cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Computes standard mathematical Cosine Similarity between two real vectors."""
    dot_product = sum(x * y for x, y in zip(v1, v2))
    magnitude1 = math.sqrt(sum(x * x for x in v1))
    magnitude2 = math.sqrt(sum(x * x for x in v2))
    if not magnitude1 or not magnitude2:
        return 0.0
    return dot_product / (magnitude1 * magnitude2)

def fallback_index_paper(session_id: str, paper_id: str, paper_title: str, chunks: List[str], embeddings: List[List[float]]):
    """Saves text chunks and vector embeddings inside local JSON session file."""
    vector_file = f"session_vectors_{session_id}.json"
    
    # Load existing vectors
    existing_vectors = []
    if os.path.exists(vector_file):
        try:
            with open(vector_file, "r") as f:
                existing_vectors = json.load(f)
        except Exception as e:
            print(f"Failed reading vector file {vector_file}: {e}")
            
    # Append new chunk vectors
    for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
        existing_vectors.append({
            "id": f"{paper_id}_chunk_{i}",
            "paper_id": paper_id,
            "paper_title": paper_title,
            "chunk_index": i,
            "document": chunk,
            "embedding": embedding
        })
        
    # Write back
    try:
        with open(vector_file, "w") as f:
            json.dump(existing_vectors, f, indent=2)
        print(f"Fallback Engine: Indexed {len(chunks)} chunks in {vector_file}.")
    except Exception as e:
        print(f"Failed writing fallback vector file: {e}")

def fallback_search_chunks(session_id: str, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
    """Performs Cosine Similarity sweep over local JSON session vectors."""
    vector_file = f"session_vectors_{session_id}.json"
    if not os.path.exists(vector_file):
        return []
        
    try:
        with open(vector_file, "r") as f:
            vectors = json.load(f)
    except Exception as e:
        print(f"Failed loading fallback vectors: {e}")
        return []
        
    scored_results = []
    for item in vectors:
        sim = calculate_cosine_similarity(query_vector, item["embedding"])
        scored_results.append({
            "text": item["document"],
            "paper_id": item["paper_id"],
            "paper_title": item["paper_title"],
            "chunk_index": item["chunk_index"],
            "score": round(sim, 4)
        })
        
    # Sort by score descending and take top_k
    scored_results.sort(key=lambda x: x["score"], reverse=True)
    return scored_results[:top_k]

# ==========================================
# Unified Vector Database Gateway APIs
# ==========================================

def index_paper(session_id: str, paper_id: str, paper_title: str, text: str):
    """Directs paper chunks indexing to either ChromaDB or Cosine Fallback Engine."""
    chunks = chunk_text(text)
    if not chunks:
        return
        
    # Generate embeddings
    embeddings = get_embeddings(chunks)
    
    if is_chroma_active():
        try:
            collection = get_or_create_collection()
            ids = [f"{paper_id}_chunk_{i}" for i in range(len(chunks))]
            metadatas = [{
                "session_id": session_id,
                "paper_id": paper_id,
                "paper_title": paper_title,
                "chunk_index": i
            } for i in range(len(chunks))]
            
            collection.upsert(
                ids=ids,
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadatas
            )
            print(f"ChromaDB: Indexed {len(chunks)} chunks for paper '{paper_title}'.")
            return
        except Exception as e:
            print(f"ChromaDB index failed: {e}. Switching to Cosine Fallback.")

    # Execute fallback mathematical indexer
    fallback_index_paper(session_id, paper_id, paper_title, chunks, embeddings)

def search_session_chunks(session_id: str, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """Performs semantic similarity search across either ChromaDB or the Fallback Cosine Engine."""
    query_vector = get_embedding(query, is_query=True)
    
    if is_chroma_active():
        try:
            collection = get_or_create_collection()
            results = collection.query(
                query_embeddings=[query_vector],
                n_results=top_k,
                where={"session_id": session_id}
            )
            
            formatted_results = []
            if results and results["documents"]:
                docs = results["documents"][0]
                metas = results["metadatas"][0]
                dists = results["distances"][0] if "distances" in results else [0.0] * len(docs)
                
                for doc, meta, dist in zip(docs, metas, dists):
                    formatted_results.append({
                        "text": doc,
                        "paper_id": meta["paper_id"],
                        "paper_title": meta["paper_title"],
                        "chunk_index": meta["chunk_index"],
                        "score": round(1.0 - dist, 4)
                    })
            return formatted_results
        except Exception as e:
            print(f"ChromaDB search failed: {e}. Switching to Cosine Fallback search.")

    # Execute fallback Cosine Search
    return fallback_search_chunks(session_id, query_vector, top_k)

def delete_session_vectors(session_id: str):
    """Deletes vector entries associated with a specific research session."""
    if is_chroma_active():
        try:
            collection = get_or_create_collection()
            collection.delete(where={"session_id": session_id})
            print(f"ChromaDB: Cleared session {session_id} vectors.")
        except Exception as e:
            print(f"ChromaDB deletion failed: {e}.")

    # Fallback JSON delete
    vector_file = f"session_vectors_{session_id}.json"
    if os.path.exists(vector_file):
        try:
            os.remove(vector_file)
            print(f"Fallback Engine: Deleted vector file {vector_file}.")
        except Exception as e:
            print(f"Failed deleting fallback vector file: {e}")
