"""
Audio transcription service using Groq's Whisper API.
Cloud-based transcription without local dependencies.
"""

import logging
from pathlib import Path
from typing import Optional, List

from app.config import settings
from app.models.schemas import TranscriptionResult, TranscriptionSegment

logger = logging.getLogger(__name__)


def transcribe_audio(file_path: str) -> TranscriptionResult:
    """
    Transcribe an audio file using Groq's Whisper API.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        TranscriptionResult with text and segments
    """
    try:
        from groq import Groq
        
        # Validate file exists
        audio_path = Path(file_path)
        if not audio_path.exists():
            logger.error(f"Audio file not found: {file_path}")
            return TranscriptionResult(
                success=False,
                text="",
                error=f"Audio file not found: {file_path}"
            )
        
        logger.info(f"Transcribing audio via Groq API: {file_path}")
        logger.info(f"File size: {audio_path.stat().st_size} bytes")
        
        # Initialize Groq client
        client = Groq(api_key=settings.groq_api_key)
        
        # Open and transcribe the audio file
        with open(audio_path, "rb") as audio_file:
            transcription = client.audio.transcriptions.create(
                file=(audio_path.name, audio_file),
                model="whisper-large-v3",
            )
        
        logger.info(f"Transcription response: {transcription}")
        
        # Extract text - handle both string and object response
        if isinstance(transcription, str):
            full_text = transcription.strip()
        elif hasattr(transcription, 'text'):
            full_text = transcription.text.strip() if transcription.text else ""
        else:
            full_text = str(transcription).strip()
        
        logger.info(f"Extracted text length: {len(full_text)}")
        
        # Process segments if available
        segments: List[TranscriptionSegment] = []
        if hasattr(transcription, 'segments') and transcription.segments:
            for segment in transcription.segments:
                seg_dict = segment if isinstance(segment, dict) else vars(segment)
                segments.append(TranscriptionSegment(
                    start=seg_dict.get('start', 0.0),
                    end=seg_dict.get('end', 0.0),
                    text=seg_dict.get('text', '').strip()
                ))
        
        # Calculate duration
        duration = segments[-1].end if segments else 0.0
        
        # Get language
        language = getattr(transcription, 'language', None)
        
        logger.info(f"Transcription complete. Duration: {duration:.1f}s, Segments: {len(segments)}, Text: {full_text[:100]}...")
        
        return TranscriptionResult(
            success=True,
            text=full_text,
            segments=segments,
            language=language,
            duration=duration
        )
        
    except Exception as e:
        logger.error(f"Transcription failed: {e}", exc_info=True)
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
