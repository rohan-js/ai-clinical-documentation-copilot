"""
Utility helper functions for the application.
"""

import os
import re
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime

from app.config import settings


def generate_session_id() -> str:
    """Generate a unique session ID."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    unique_id = str(uuid.uuid4())[:8]
    return f"session_{timestamp}_{unique_id}"


def validate_audio_file(filename: str, file_size: int) -> Tuple[bool, str]:
    """
    Validate an uploaded audio file.
    
    Args:
        filename: Name of the file
        file_size: Size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_audio_extensions:
        return False, f"Invalid audio format. Allowed: {', '.join(settings.allowed_audio_extensions)}"
    
    # Check size
    max_size = settings.max_audio_size_mb * 1024 * 1024
    if file_size > max_size:
        return False, f"File too large. Maximum size: {settings.max_audio_size_mb}MB"
    
    return True, ""


def validate_notes_file(filename: str, file_size: int) -> Tuple[bool, str]:
    """
    Validate an uploaded notes file.
    
    Args:
        filename: Name of the file
        file_size: Size in bytes
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    # Check extension
    ext = Path(filename).suffix.lower()
    if ext not in settings.allowed_notes_extensions:
        return False, f"Invalid notes format. Allowed: {', '.join(settings.allowed_notes_extensions)}"
    
    # Check size
    max_size = settings.max_notes_size_mb * 1024 * 1024
    if file_size > max_size:
        return False, f"File too large. Maximum size: {settings.max_notes_size_mb}MB"
    
    return True, ""


def sanitize_json_response(response: str) -> Optional[Dict[str, Any]]:
    """
    Sanitize and parse a JSON response from an LLM.
    
    Args:
        response: Raw LLM response string
        
    Returns:
        Parsed JSON dict or None if parsing fails
    """
    if not response:
        return None
    
    # Clean the response
    cleaned = response.strip()
    
    # Try to find JSON code block first (```json ... ```)
    json_block_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', cleaned)
    if json_block_match:
        json_str = json_block_match.group(1).strip()
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            pass
    
    # Find the outermost JSON object by matching braces
    # Start from the first { and find the matching }
    start_idx = cleaned.find('{')
    if start_idx != -1:
        brace_count = 0
        end_idx = start_idx
        in_string = False
        escape = False
        
        for i, char in enumerate(cleaned[start_idx:], start_idx):
            if escape:
                escape = False
                continue
            if char == '\\':
                escape = True
                continue
            if char == '"' and not escape:
                in_string = not in_string
                continue
            if in_string:
                continue
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = i
                    break
        
        if brace_count == 0:
            json_str = cleaned[start_idx:end_idx + 1]
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                pass
    
    # Try parsing the whole response as JSON
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    
    # Last resort: try to fix common JSON issues
    try:
        # Remove trailing commas before } or ]
        fixed = re.sub(r',\s*([}\]])', r'\1', cleaned)
        # Try again
        start_idx = fixed.find('{')
        if start_idx != -1:
            end_idx = fixed.rfind('}')
            if end_idx > start_idx:
                json_str = fixed[start_idx:end_idx + 1]
                return json.loads(json_str)
    except json.JSONDecodeError:
        pass
    
    return None


def clean_text(text: str) -> str:
    """
    Clean and normalize text.
    
    Args:
        text: Input text
        
    Returns:
        Cleaned text
    """
    if not text:
        return ""
    
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove control characters (except newlines)
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    
    return text.strip()


def truncate_text(text: str, max_length: int = 500) -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Input text
        max_length: Maximum characters
        
    Returns:
        Truncated text with ellipsis if needed
    """
    if not text or len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to a human-readable string.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string (e.g., "2m 30s")
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"
    
    hours = int(minutes // 60)
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m"


def ensure_directory(path: Path) -> None:
    """Ensure a directory exists."""
    path.mkdir(parents=True, exist_ok=True)


def safe_file_name(filename: str) -> str:
    """
    Make a filename safe for the filesystem.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # Limit length
    name, ext = os.path.splitext(safe_name)
    if len(name) > 200:
        name = name[:200]
    
    return name + ext


def get_file_extension(filename: str) -> str:
    """Get the lowercase file extension."""
    return Path(filename).suffix.lower()


def format_error_message(error: Exception) -> str:
    """Format an exception into a user-friendly message."""
    error_type = type(error).__name__
    error_msg = str(error)
    
    # Make common errors more user-friendly
    friendly_errors = {
        "FileNotFoundError": "The requested file could not be found.",
        "PermissionError": "Permission denied when accessing the file.",
        "JSONDecodeError": "Failed to parse the response. Please try again.",
        "ConnectionError": "Failed to connect to the service. Please check your internet connection.",
        "TimeoutError": "The request timed out. Please try again.",
    }
    
    if error_type in friendly_errors:
        return friendly_errors[error_type]
    
    # Truncate very long error messages
    if len(error_msg) > 200:
        error_msg = error_msg[:200] + "..."
    
    return f"{error_type}: {error_msg}"
