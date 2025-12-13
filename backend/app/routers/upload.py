"""
Upload routes for audio and notes files.
"""

import os
import shutil
import logging
from pathlib import Path
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.models.schemas import UploadResponse, ProcessingStatus
from app.models.database import get_db, SessionRepository
from app.utils.helpers import (
    generate_session_id,
    validate_audio_file,
    validate_notes_file,
    safe_file_name
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/upload", tags=["Upload"])


@router.post("/audio", response_model=UploadResponse)
async def upload_audio(
    file: UploadFile = File(...),
    session_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Upload an audio file for transcription.
    
    - Accepts MP3, WAV, M4A, OGG, FLAC formats
    - Maximum size: 50MB
    - Creates a new session if session_id not provided
    """
    try:
        # Read file content to check size
        content = await file.read()
        file_size = len(content)
        
        # Validate file
        is_valid, error_msg = validate_audio_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate or use session ID
        if not session_id:
            session_id = generate_session_id()
        
        # Get or create session
        session = SessionRepository.get(db, session_id)
        if not session:
            session = SessionRepository.create(db, session_id)
        
        # Create session upload directory
        session_dir = settings.upload_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file with safe name
        safe_name = safe_file_name(file.filename)
        file_path = session_dir / f"audio_{safe_name}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update session with audio file info
        SessionRepository.update(
            db,
            session_id,
            audio_file_path=str(file_path),
            audio_filename=file.filename,
            status=ProcessingStatus.PENDING.value
        )
        
        logger.info(f"Audio file uploaded: {file.filename} -> {file_path}")
        
        return UploadResponse(
            success=True,
            session_id=session_id,
            file_type="audio",
            filename=file.filename,
            file_path=str(file_path),
            message=f"Audio file uploaded successfully. Size: {file_size / 1024 / 1024:.1f}MB"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Audio upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/notes", response_model=UploadResponse)
async def upload_notes(
    file: UploadFile = File(...),
    session_id: str = None,
    db: Session = Depends(get_db)
):
    """
    Upload a notes file (text or PDF).
    
    - Accepts TXT, PDF, DOC, DOCX formats
    - Maximum size: 10MB
    - Creates a new session if session_id not provided
    """
    try:
        # Read file content
        content = await file.read()
        file_size = len(content)
        
        # Validate file
        is_valid, error_msg = validate_notes_file(file.filename, file_size)
        if not is_valid:
            raise HTTPException(status_code=400, detail=error_msg)
        
        # Generate or use session ID
        if not session_id:
            session_id = generate_session_id()
        
        # Get or create session
        session = SessionRepository.get(db, session_id)
        if not session:
            session = SessionRepository.create(db, session_id)
        
        # Create session upload directory
        session_dir = settings.upload_dir / session_id
        session_dir.mkdir(parents=True, exist_ok=True)
        
        # Save file with safe name
        safe_name = safe_file_name(file.filename)
        file_path = session_dir / f"notes_{safe_name}"
        
        with open(file_path, "wb") as f:
            f.write(content)
        
        # Update session with notes file info
        SessionRepository.update(
            db,
            session_id,
            notes_file_path=str(file_path),
            notes_filename=file.filename,
            status=ProcessingStatus.PENDING.value
        )
        
        logger.info(f"Notes file uploaded: {file.filename} -> {file_path}")
        
        return UploadResponse(
            success=True,
            session_id=session_id,
            file_type="notes",
            filename=file.filename,
            file_path=str(file_path),
            message=f"Notes file uploaded successfully. Size: {file_size / 1024:.1f}KB"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Notes upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.delete("/{session_id}/audio")
async def delete_audio(session_id: str, db: Session = Depends(get_db)):
    """Delete the audio file from a session."""
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.audio_file_path and os.path.exists(session.audio_file_path):
        os.remove(session.audio_file_path)
    
    SessionRepository.update(
        db, session_id,
        audio_file_path=None,
        audio_filename=None
    )
    
    return {"success": True, "message": "Audio file deleted"}


@router.delete("/{session_id}/notes")
async def delete_notes(session_id: str, db: Session = Depends(get_db)):
    """Delete the notes file from a session."""
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if session.notes_file_path and os.path.exists(session.notes_file_path):
        os.remove(session.notes_file_path)
    
    SessionRepository.update(
        db, session_id,
        notes_file_path=None,
        notes_filename=None
    )
    
    return {"success": True, "message": "Notes file deleted"}
