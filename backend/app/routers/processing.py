"""
Processing routes for running the clinical documentation pipeline.
"""

import logging
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.config import settings
from app.models.schemas import (
    ProcessingRequest,
    ProcessingResult,
    ProcessingStatus,
    ProcessingStatusResponse,
    TranscriptionResult,
    ExtractedEntities,
    ClinicalSummary
)
from app.models.database import get_db, SessionRepository, SessionModel
from app.services.transcription import transcribe_audio
from app.services.pdf_extractor import extract_text_from_file, combine_texts
from app.services.summary_generator import process_and_generate_summary

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/process", tags=["Processing"])

# In-memory status tracking for async operations
processing_status = {}


def update_status(session_id: str, status: ProcessingStatus, step: str, progress: int):
    """Update the processing status for a session."""
    processing_status[session_id] = {
        "status": status,
        "step": step,
        "progress": progress,
        "updated_at": datetime.utcnow()
    }


async def run_processing_pipeline(session_id: str, db_session):
    """
    Run the full processing pipeline in the background.
    
    Steps:
    1. Transcribe audio (if present)
    2. Extract text from notes (if present)
    3. Combine texts
    4. Run LLM extraction
    5. RAG enhancement
    6. Generate summary
    """
    try:
        # Get session from database
        session = SessionRepository.get(db_session, session_id)
        if not session:
            logger.error(f"Session not found: {session_id}")
            return
        
        transcription_text = ""
        notes_text = ""
        
        # Step 1: Transcribe audio
        if session.audio_file_path:
            update_status(session_id, ProcessingStatus.TRANSCRIBING, "Transcribing audio...", 20)
            SessionRepository.update(db_session, session_id, status=ProcessingStatus.TRANSCRIBING.value)
            
            logger.info(f"[{session_id}] Transcribing audio: {session.audio_file_path}")
            transcription_result = transcribe_audio(session.audio_file_path)
            
            if transcription_result.success:
                transcription_text = transcription_result.text
                session.set_transcription(transcription_result.model_dump())
                db_session.commit()
                logger.info(f"[{session_id}] Transcription complete: {len(transcription_text)} chars")
            else:
                logger.warning(f"[{session_id}] Transcription failed: {transcription_result.error}")
        
        # Step 2: Extract notes text
        if session.notes_file_path:
            update_status(session_id, ProcessingStatus.EXTRACTING, "Extracting text from notes...", 35)
            
            logger.info(f"[{session_id}] Extracting notes: {session.notes_file_path}")
            success, notes_text, error = extract_text_from_file(session.notes_file_path)
            
            if success:
                logger.info(f"[{session_id}] Notes extracted: {len(notes_text)} chars")
            else:
                logger.warning(f"[{session_id}] Notes extraction failed: {error}")
        
        # Step 3: Combine texts
        combined_text = combine_texts(transcription_text, notes_text)
        
        if not combined_text.strip():
            update_status(session_id, ProcessingStatus.FAILED, "No text to process", 0)
            SessionRepository.update(
                db_session, session_id,
                status=ProcessingStatus.FAILED.value,
                error_message="No text content available. Please upload audio or notes."
            )
            return
        
        SessionRepository.update(db_session, session_id, combined_text=combined_text)
        
        # Step 4-6: LLM extraction, RAG enhancement, and summary generation
        update_status(session_id, ProcessingStatus.EXTRACTING, "Extracting clinical entities...", 50)
        SessionRepository.update(db_session, session_id, status=ProcessingStatus.EXTRACTING.value)
        
        # This runs extraction, RAG, and summary generation
        update_status(session_id, ProcessingStatus.ENHANCING, "Enhancing with clinical guidelines...", 70)
        SessionRepository.update(db_session, session_id, status=ProcessingStatus.ENHANCING.value)
        
        update_status(session_id, ProcessingStatus.GENERATING, "Generating clinical summary...", 85)
        SessionRepository.update(db_session, session_id, status=ProcessingStatus.GENERATING.value)
        
        result = process_and_generate_summary(combined_text, session_id)
        
        if result.success:
            # Store results
            if result.extracted_entities:
                session.set_extracted_entities(result.extracted_entities.model_dump())
            if result.clinical_summary:
                session.set_clinical_summary(result.clinical_summary.model_dump())
            
            SessionRepository.update(db_session, session_id, status=ProcessingStatus.COMPLETED.value)
            update_status(session_id, ProcessingStatus.COMPLETED, "Processing complete!", 100)
            logger.info(f"[{session_id}] Processing completed successfully")
        else:
            SessionRepository.update(
                db_session, session_id,
                status=ProcessingStatus.FAILED.value,
                error_message=result.error
            )
            update_status(session_id, ProcessingStatus.FAILED, result.error or "Processing failed", 0)
            logger.error(f"[{session_id}] Processing failed: {result.error}")
        
        db_session.commit()
        
    except Exception as e:
        logger.error(f"[{session_id}] Pipeline error: {e}")
        update_status(session_id, ProcessingStatus.FAILED, str(e), 0)
        try:
            SessionRepository.update(
                db_session, session_id,
                status=ProcessingStatus.FAILED.value,
                error_message=str(e)
            )
            db_session.commit()
        except:
            pass


@router.post("/{session_id}", response_model=ProcessingStatusResponse)
async def start_processing(
    session_id: str,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Start the processing pipeline for a session.
    
    The session must have at least one file (audio or notes) uploaded.
    Processing runs in the background.
    """
    # Check session exists
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Check if already processing
    if session.status in [ProcessingStatus.TRANSCRIBING.value, 
                          ProcessingStatus.EXTRACTING.value,
                          ProcessingStatus.ENHANCING.value,
                          ProcessingStatus.GENERATING.value]:
        return ProcessingStatusResponse(
            session_id=session_id,
            status=ProcessingStatus(session.status),
            progress=processing_status.get(session_id, {}).get("progress", 50),
            current_step="Processing in progress..."
        )
    
    # Check if has files
    if not session.audio_file_path and not session.notes_file_path:
        raise HTTPException(
            status_code=400,
            detail="No files uploaded. Please upload audio or notes first."
        )
    
    # Initialize status
    update_status(session_id, ProcessingStatus.UPLOADING, "Starting processing...", 10)
    SessionRepository.update(db, session_id, status=ProcessingStatus.UPLOADING.value)
    
    # Start background processing
    # Note: We need to create a new db session for background task
    from app.models.database import SessionLocal
    
    def process_task():
        db_session = SessionLocal()
        try:
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(run_processing_pipeline(session_id, db_session))
        finally:
            db_session.close()
    
    background_tasks.add_task(process_task)
    
    return ProcessingStatusResponse(
        session_id=session_id,
        status=ProcessingStatus.UPLOADING,
        progress=10,
        current_step="Processing started..."
    )


@router.get("/{session_id}/status", response_model=ProcessingStatusResponse)
async def get_processing_status(session_id: str, db: Session = Depends(get_db)):
    """Get the current processing status for a session."""
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Get status from in-memory tracking or database
    status_info = processing_status.get(session_id, {})
    
    status = ProcessingStatus(session.status) if session.status else ProcessingStatus.PENDING
    progress = status_info.get("progress", 0)
    step = status_info.get("step", "Waiting...")
    
    # Set progress based on status if not tracked
    if not status_info:
        progress_map = {
            ProcessingStatus.PENDING: 0,
            ProcessingStatus.UPLOADING: 10,
            ProcessingStatus.TRANSCRIBING: 30,
            ProcessingStatus.EXTRACTING: 50,
            ProcessingStatus.ENHANCING: 70,
            ProcessingStatus.GENERATING: 85,
            ProcessingStatus.COMPLETED: 100,
            ProcessingStatus.FAILED: 0
        }
        progress = progress_map.get(status, 0)
        step = status.value.title()
    
    return ProcessingStatusResponse(
        session_id=session_id,
        status=status,
        progress=progress,
        current_step=step,
        message=session.error_message if status == ProcessingStatus.FAILED else None
    )


@router.get("/{session_id}/result", response_model=ProcessingResult)
async def get_processing_result(session_id: str, db: Session = Depends(get_db)):
    """Get the complete processing result for a session."""
    session = SessionRepository.get(db, session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    status = ProcessingStatus(session.status) if session.status else ProcessingStatus.PENDING
    
    # Get stored results
    transcription_data = session.get_transcription()
    entities_data = session.get_extracted_entities()
    summary_data = session.get_clinical_summary()
    
    # Build result
    transcription = None
    if transcription_data:
        transcription = TranscriptionResult(**transcription_data)
    
    entities = None
    if entities_data:
        entities = ExtractedEntities(**entities_data)
    
    summary = None
    if summary_data:
        summary = ClinicalSummary(**summary_data)
    
    return ProcessingResult(
        success=status == ProcessingStatus.COMPLETED,
        session_id=session_id,
        status=status,
        transcription=transcription,
        extracted_entities=entities,
        clinical_summary=summary,
        error=session.error_message
    )
