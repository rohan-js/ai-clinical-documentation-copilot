"""
Pydantic models (schemas) for request/response validation.
Defines the data structures used throughout the application.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class ProcessingStatus(str, Enum):
    """Status of the processing pipeline."""
    PENDING = "pending"
    UPLOADING = "uploading"
    TRANSCRIBING = "transcribing"
    EXTRACTING = "extracting"
    ENHANCING = "enhancing"
    GENERATING = "generating"
    COMPLETED = "completed"
    FAILED = "failed"


# ==================== Upload Schemas ====================

class UploadResponse(BaseModel):
    """Response after file upload."""
    success: bool
    session_id: str
    file_type: str  # "audio" or "notes"
    filename: str
    file_path: str
    message: str


class FileInfo(BaseModel):
    """Information about an uploaded file."""
    filename: str
    file_path: str
    file_type: str
    size_bytes: int
    uploaded_at: datetime


# ==================== Transcription Schemas ====================

class TranscriptionSegment(BaseModel):
    """A segment of transcribed audio with timing."""
    start: float
    end: float
    text: str


class TranscriptionResult(BaseModel):
    """Result of audio transcription."""
    success: bool
    text: str
    segments: List[TranscriptionSegment] = []
    language: Optional[str] = None
    duration: Optional[float] = None
    error: Optional[str] = None


# ==================== Extraction Schemas ====================

class ExtractedEntities(BaseModel):
    """Entities extracted from clinical text by the LLM."""
    symptoms: List[str] = Field(default_factory=list, description="Patient-reported symptoms")
    patient_history: List[str] = Field(default_factory=list, description="Relevant medical history")
    clinician_observations: List[str] = Field(default_factory=list, description="Clinical observations made by the provider")
    assessments: List[str] = Field(default_factory=list, description="Clinical assessments and diagnoses")
    recommendations: List[str] = Field(default_factory=list, description="Treatment recommendations")
    medications: List[str] = Field(default_factory=list, description="Current or prescribed medications")
    vital_signs: Dict[str, str] = Field(default_factory=dict, description="Vital signs if mentioned")
    audiological_findings: List[str] = Field(default_factory=list, description="Audiological test results")


class ExtractionResult(BaseModel):
    """Result of LLM extraction."""
    success: bool
    entities: Optional[ExtractedEntities] = None
    raw_response: Optional[str] = None
    error: Optional[str] = None


# ==================== SOAP Notes Schemas ====================

class SOAPNotes(BaseModel):
    """SOAP-format clinical notes."""
    subjective: str = Field(default="", description="Patient's chief complaint and symptoms in their own words")
    objective: str = Field(default="", description="Clinical observations, exam findings, test results")
    assessment: str = Field(default="", description="Clinical assessment and diagnosis")
    plan: str = Field(default="", description="Treatment plan and follow-up")


# ==================== Task Schemas ====================

class TaskPriority(str, Enum):
    """Priority level for workflow tasks."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class WorkflowTask(BaseModel):
    """A follow-up task or action item."""
    id: str
    title: str
    description: str
    priority: TaskPriority = TaskPriority.MEDIUM
    category: str  # e.g., "follow-up", "testing", "referral", "medication"
    due_date: Optional[str] = None
    completed: bool = False


# ==================== Summary Schemas ====================

class ClinicalSummary(BaseModel):
    """Complete clinical summary output."""
    narrative: str = Field(default="", description="Well-formatted clinical narrative")
    soap_notes: SOAPNotes = Field(default_factory=SOAPNotes)
    tasks: List[WorkflowTask] = Field(default_factory=list)
    rag_context_used: List[str] = Field(default_factory=list, description="Guidelines used for enhancement")


# ==================== Session Schemas ====================

class SessionCreate(BaseModel):
    """Request to create a new session."""
    patient_id: Optional[str] = None
    notes: Optional[str] = None


class SessionData(BaseModel):
    """Complete session data."""
    id: str
    created_at: datetime
    updated_at: datetime
    status: ProcessingStatus
    
    # File information
    audio_file: Optional[FileInfo] = None
    notes_file: Optional[FileInfo] = None
    
    # Processing results
    transcription: Optional[TranscriptionResult] = None
    extracted_entities: Optional[ExtractedEntities] = None
    clinical_summary: Optional[ClinicalSummary] = None
    
    # Combined text used for processing
    combined_text: Optional[str] = None
    
    # Error information
    error_message: Optional[str] = None


class SessionListItem(BaseModel):
    """Summary of a session for list views."""
    id: str
    created_at: datetime
    status: ProcessingStatus
    has_audio: bool
    has_notes: bool
    preview: Optional[str] = None  # First 100 chars of transcription/notes


class SessionList(BaseModel):
    """List of sessions."""
    sessions: List[SessionListItem]
    total: int


# ==================== Processing Schemas ====================

class ProcessingRequest(BaseModel):
    """Request to start processing."""
    session_id: str


class ProcessingStatusResponse(BaseModel):
    """Response with current processing status."""
    session_id: str
    status: ProcessingStatus
    progress: int  # 0-100
    current_step: str
    message: Optional[str] = None


class ProcessingResult(BaseModel):
    """Complete result of the processing pipeline."""
    success: bool
    session_id: str
    status: ProcessingStatus
    
    # All outputs
    transcription: Optional[TranscriptionResult] = None
    extracted_entities: Optional[ExtractedEntities] = None
    clinical_summary: Optional[ClinicalSummary] = None
    
    # Metadata
    processing_time_seconds: Optional[float] = None
    error: Optional[str] = None


# ==================== Error Schemas ====================

class ErrorResponse(BaseModel):
    """Standard error response."""
    success: bool = False
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
