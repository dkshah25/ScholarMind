import os
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from app.database.db import init_db
from app.api.routers import sessions, ingest, agents, graph, experiments

load_dotenv()

app = FastAPI(
    title="ScholarMind: AI Research Operating System API",
    description="Multi-agent academic compiler, gap discovery, and experiment planner.",
    version="1.0.0"
)

# CORS configurations for communication with Next.js dashboard
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Allow standard dev origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup routine
@app.on_event("startup")
def on_startup():
    print("Booting ScholarMind Research Engine...")
    init_db()

# Mount API Routers
app.include_router(sessions.router, prefix="/api")
app.include_router(ingest.router, prefix="/api")
app.include_router(agents.router, prefix="/api")
app.include_router(graph.router, prefix="/api")
app.include_router(experiments.router, prefix="/api")

@app.get("/api/health")
def health_check():
    """Simple API server status check."""
    return {"status": "healthy", "service": "scholarmind-api"}

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "127.0.0.1")
    uvicorn.run("app.api.main:app", host=host, port=port, reload=True)
