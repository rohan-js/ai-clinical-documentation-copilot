"""
Session management routes.
"""

import os
import shutil
import logging
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.models.schemas import (
    SessionData,
    SessionList,
    SessionListItem,
    ProcessingStatus,
    FileInfo,
    TranscriptionResult,
    ExtractedEntities,
    ClinicalSummary
)
from app.models.database import get_db, SessionRepository
from app.utils.helpers import generate_session_id, truncate_text

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/sessions", tags=["Sessions"])


@router.get("", response_model=SessionList)
async def list_sessions(
    skip: int = 0,
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """List all sessions with pagination."""
    sessions = SessionRepository.get_all(db, skip=skip, limit=limit)
    total = SessionRepository.count(db)
    
    items = []
    for s in sessions:
        # Get preview text
        preview = None
        transcription = s.get_transcription()
        if transcription and transcription.get("text"):
            preview = truncate_text(transcription["text"], 100)
        elif s.combined_text:
            preview = truncate_text(s.combined_text, 100)
        
        items.append(SessionListItem(
            id=s.id,
            created_at=s.created_at,
            status=ProcessingStatus(s.status) if s.status else ProcessingStatus.PENDING,
            has_audio=bool(s.audio_file_path),
            has_notes=bool(s.notes_file_path),
            preview=preview
        ))
    
    return SessionList(sessions=items, total=total)


@router.get("/{session_id}", response_model=SessionData)
async def get_session(session_id: str, db: Session = Depends(get_db)):
    """Get detailed session data."""
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Build file info
    audio_file = None
    if session.audio_file_path:
        try:
            size = os.path.getsize(session.audio_file_path) if os.path.exists(session.audio_file_path) else 0
            audio_file = FileInfo(
                filename=session.audio_filename or "audio",
                file_path=session.audio_file_path,
                file_type="audio",
                size_bytes=size,
                uploaded_at=session.created_at
            )
        except:
            pass
    
    notes_file = None
    if session.notes_file_path:
        try:
            size = os.path.getsize(session.notes_file_path) if os.path.exists(session.notes_file_path) else 0
            notes_file = FileInfo(
                filename=session.notes_filename or "notes",
                file_path=session.notes_file_path,
                file_type="notes",
                size_bytes=size,
                uploaded_at=session.created_at
            )
        except:
            pass
    
    # Get stored results
    transcription = None
    transcription_data = session.get_transcription()
    if transcription_data:
        transcription = TranscriptionResult(**transcription_data)
    
    entities = None
    entities_data = session.get_extracted_entities()
    if entities_data:
        entities = ExtractedEntities(**entities_data)
    
    summary = None
    summary_data = session.get_clinical_summary()
    if summary_data:
        summary = ClinicalSummary(**summary_data)
    
    return SessionData(
        id=session.id,
        created_at=session.created_at,
        updated_at=session.updated_at,
        status=ProcessingStatus(session.status) if session.status else ProcessingStatus.PENDING,
        audio_file=audio_file,
        notes_file=notes_file,
        transcription=transcription,
        extracted_entities=entities,
        clinical_summary=summary,
        combined_text=session.combined_text,
        error_message=session.error_message
    )


@router.post("/create")
async def create_session(db: Session = Depends(get_db)):
    """Create a new empty session."""
    session_id = generate_session_id()
    session = SessionRepository.create(db, session_id)
    
    return {
        "success": True,
        "session_id": session.id,
        "message": "Session created successfully"
    }


@router.delete("/{session_id}")
async def delete_session(session_id: str, db: Session = Depends(get_db)):
    """Delete a session and its files."""
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Delete files
    session_dir = settings.upload_dir / session_id
    if session_dir.exists():
        try:
            shutil.rmtree(session_dir)
        except Exception as e:
            logger.warning(f"Failed to delete session files: {e}")
    
    # Delete from database
    SessionRepository.delete(db, session_id)
    
    return {"success": True, "message": "Session deleted successfully"}


@router.post("/{session_id}/reset")
async def reset_session(session_id: str, db: Session = Depends(get_db)):
    """Reset a session's processing results while keeping files."""
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Clear processing results
    SessionRepository.update(
        db, session_id,
        status=ProcessingStatus.PENDING.value,
        transcription_json=None,
        extracted_entities_json=None,
        clinical_summary_json=None,
        combined_text=None,
        error_message=None
    )
    
    return {"success": True, "message": "Session reset successfully"}


@router.get("/{session_id}/export")
async def export_session(session_id: str, db: Session = Depends(get_db)):
    """Export session data as JSON for download."""
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    export_data = {
        "session_id": session.id,
        "created_at": session.created_at.isoformat(),
        "status": session.status,
        "transcription": session.get_transcription(),
        "extracted_entities": session.get_extracted_entities(),
        "clinical_summary": session.get_clinical_summary(),
        "combined_text": session.combined_text
    }
    
    return export_data
