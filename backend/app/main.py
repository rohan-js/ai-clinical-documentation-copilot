"""
AI Clinical Documentation Copilot - FastAPI Backend

Main application entry point with all routes and middleware configured.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers import upload, processing, sessions
from app.models.database import init_db

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info("Starting AI Clinical Documentation Copilot backend...")
    
    # Initialize database
    init_db()
    logger.info("Database initialized")
    
    # Ensure directories exist
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.chroma_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Upload directory: {settings.upload_dir}")
    logger.info(f"ChromaDB directory: {settings.chroma_dir}")
    
    # Pre-load models in production (optional, can be slow)
    # Uncomment to pre-load on startup:
    # try:
    #     from app.services.transcription import get_whisper_model
    #     get_whisper_model()
    #     logger.info("Whisper model pre-loaded")
    # except Exception as e:
    #     logger.warning(f"Failed to pre-load Whisper model: {e}")
    
    # try:
    #     from app.services.rag_pipeline import get_chroma_collection
    #     get_chroma_collection()
    #     logger.info("RAG pipeline initialized")
    # except Exception as e:
    #     logger.warning(f"Failed to initialize RAG pipeline: {e}")
    
    logger.info("Backend startup complete!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down backend...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    description="AI-powered clinical documentation assistant for audiologists and clinicians",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "https://ai-clinical-documentation-copilot.vercel.app",
        "https://*.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle uncaught exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": "Internal server error",
            "detail": str(exc) if settings.debug else "An unexpected error occurred"
        }
    )


# Include routers
app.include_router(upload.router)
app.include_router(processing.router)
app.include_router(sessions.router)


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.app_name,
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "description": "AI-powered clinical documentation assistant",
        "endpoints": {
            "upload_audio": "POST /api/upload/audio",
            "upload_notes": "POST /api/upload/notes",
            "start_processing": "POST /api/process/{session_id}",
            "get_status": "GET /api/process/{session_id}/status",
            "get_result": "GET /api/process/{session_id}/result",
            "list_sessions": "GET /api/sessions",
            "get_session": "GET /api/sessions/{session_id}",
            "health": "GET /health"
        }
    }


# API info endpoint
@app.get("/api")
async def api_info():
    """API information endpoint."""
    return {
        "version": "1.0.0",
        "models": {
            "whisper": settings.whisper_model,
            "llm": settings.groq_model,
            "embedding": settings.embedding_model
        },
        "limits": {
            "max_audio_size_mb": settings.max_audio_size_mb,
            "max_notes_size_mb": settings.max_notes_size_mb,
            "allowed_audio_formats": settings.allowed_audio_extensions,
            "allowed_notes_formats": settings.allowed_notes_extensions
        }
    }


# RAG stats endpoint
@app.get("/api/rag/stats")
async def rag_stats():
    """Get RAG pipeline statistics."""
    try:
        from app.services.rag_pipeline import get_collection_stats
        return get_collection_stats()
    except Exception as e:
        return {"error": str(e)}
