import os
import shutil
import uuid
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from app.database.models import SessionResponse, PaperMetadata
import app.database.db as db
from app.services.pdf_parser import parse_and_ingest_pdf
from app.services.vector_store import index_paper

router = APIRouter(prefix="/ingest", tags=["Ingestion"])

# Ensure an uploads directory exists
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post("/upload", response_model=SessionResponse)
async def upload_pdf(
    session_id: str = Form(...),
    file: UploadFile = File(...)
):
    """
    Uploads an academic PDF, parses its text, extracts structured metadata 
    via Gemini, indexes text in ChromaDB, and associates it with the active session.
    """
    # 1. Verify session exists
    session = db.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail=f"Research Session {session_id} not found.")

    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF documents are supported.")

    # 2. Save the uploaded file locally
    paper_id = str(uuid.uuid4())[:8]
    sanitized_filename = f"{paper_id}_{file.filename}"
    file_path = os.path.join(UPLOAD_DIR, sanitized_filename)
    
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed saving file: {str(e)}")

    # 3. Parse text and extract metadata
    print(f"Parsing uploaded paper: {file.filename} in session {session_id}...")
    try:
        raw_text, metadata = parse_and_ingest_pdf(file_path)
    except Exception as e:
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(status_code=500, detail=f"Failed parsing PDF: {str(e)}")

    # 4. Save paper text content and metadata
    try:
        db.save_paper(
            session_id=session_id,
            paper_id=paper_id,
            title=metadata["title"],
            authors=metadata["authors"],
            journal=metadata["journal"],
            year=metadata["year"],
            abstract=metadata["abstract"],
            file_path=file_path,
            parsed_text=raw_text
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed committing paper metadata to DB: {str(e)}")

    # 5. Index chunks in the Vector Store (ChromaDB or custom mathematical fallback)
    try:
        index_paper(
            session_id=session_id,
            paper_id=paper_id,
            paper_title=metadata["title"],
            text=raw_text
        )
    except Exception as e:
        print(f"Warning: Indexing paper failed: {e}. Session will run with text metadata search fallback.")

    # 6. Update the active Research Session papers list
    paper_meta = PaperMetadata(
        id=paper_id,
        title=metadata["title"],
        authors=metadata["authors"],
        journal=metadata["journal"],
        year=metadata["year"],
        abstract=metadata["abstract"],
        file_path=file_path
    )
    
    session.papers.append(paper_meta)
    
    try:
        updated_session = db.save_session(session)
        return updated_session
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed updating research session database: {str(e)}")
