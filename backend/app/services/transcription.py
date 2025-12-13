"""
Audio transcription service using OpenAI Whisper.
Provides local audio transcription without requiring an API.
"""

import logging
from pathlib import Path
from typing import Optional, List

from app.config import settings
from app.models.schemas import TranscriptionResult, TranscriptionSegment

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_whisper_model = None


def get_whisper_model():
    """
    Get or initialize the Whisper model.
    Uses lazy loading to avoid loading the model on import.
    """
    global _whisper_model
    
    if _whisper_model is None:
        try:
            from faster_whisper import WhisperModel
            
            logger.info(f"Loading Faster-Whisper model: {settings.whisper_model}")
            _whisper_model = WhisperModel(
                settings.whisper_model,
                device=settings.whisper_device,
                compute_type=settings.whisper_compute_type
            )
            logger.info("Faster-Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    return _whisper_model


def transcribe_audio(file_path: str) -> TranscriptionResult:
    """
    Transcribe an audio file using Faster-Whisper.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        TranscriptionResult with text and segments
    """
    try:
        # Validate file exists
        audio_path = Path(file_path)
        if not audio_path.exists():
            return TranscriptionResult(
                success=False,
                text="",
                error=f"Audio file not found: {file_path}"
            )
        
        # Get the model
        model = get_whisper_model()
        
        logger.info(f"Transcribing audio: {file_path}")
        
        # Perform transcription with faster-whisper
        segments_generator, info = model.transcribe(
            str(audio_path),
            vad_filter=True,
            vad_parameters=dict(min_silence_duration_ms=500)
        )
        
        # Process segments
        segments: List[TranscriptionSegment] = []
        full_text_parts = []
        
        for segment in segments_generator:
            segments.append(TranscriptionSegment(
                start=segment.start,
                end=segment.end,
                text=segment.text.strip()
            ))
            full_text_parts.append(segment.text.strip())
        
        full_text = " ".join(full_text_parts)
        
        # Calculate duration from last segment
        duration = segments[-1].end if segments else 0.0
        
        # Get detected language
        language = info.language if hasattr(info, 'language') else None
        
        logger.info(f"Transcription complete. Duration: {duration:.1f}s, Segments: {len(segments)}")
        
        return TranscriptionResult(
            success=True,
            text=full_text,
            segments=segments,
            language=language,
            duration=duration
        )
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}")
        return TranscriptionResult(
            success=False,
            text="",
            error=f"Transcription failed: {str(e)}"
        )


def get_transcription_preview(result: TranscriptionResult, max_length: int = 200) -> str:
    """
    Get a preview of the transcription.
    
    Args:
        result: TranscriptionResult object
        max_length: Maximum preview length
        
    Returns:
        Preview string
    """
    if not result.success or not result.text:
        return ""
    
    text = result.text
    if len(text) > max_length:
        text = text[:max_length - 3] + "..."
    return text


def format_timestamp(seconds: float) -> str:
    """
    Format seconds into HH:MM:SS.mmm format.
    
    Args:
        seconds: Time in seconds
        
    Returns:
        Formatted timestamp
    """
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:06.3f}"
    return f"{minutes:02d}:{secs:06.3f}"


def segments_to_srt(segments: List[TranscriptionSegment]) -> str:
    """
    Convert segments to SRT subtitle format.
    
    Args:
        segments: List of TranscriptionSegment
        
    Returns:
        SRT formatted string
    """
    srt_lines = []
    
    for i, segment in enumerate(segments, 1):
        start_time = format_srt_timestamp(segment.start)
        end_time = format_srt_timestamp(segment.end)
        
        srt_lines.append(str(i))
        srt_lines.append(f"{start_time} --> {end_time}")
        srt_lines.append(segment.text)
        srt_lines.append("")
    
    return "\n".join(srt_lines)


def format_srt_timestamp(seconds: float) -> str:
    """Format seconds for SRT format (HH:MM:SS,mmm)."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds % 1) * 1000)
    
    return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
