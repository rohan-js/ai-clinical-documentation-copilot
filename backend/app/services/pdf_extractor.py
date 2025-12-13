"""
PDF and text extraction service.
Extracts text content from PDF files and plain text files.
"""

import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


def extract_text_from_file(file_path: str) -> tuple[bool, str, Optional[str]]:
    """
    Extract text from a file (PDF or plain text).
    
    Args:
        file_path: Path to the file
        
    Returns:
        Tuple of (success, extracted_text, error_message)
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            return False, "", f"File not found: {file_path}"
        
        extension = path.suffix.lower()
        
        if extension == ".pdf":
            return extract_from_pdf(file_path)
        elif extension in [".txt", ".text"]:
            return extract_from_text(file_path)
        elif extension in [".doc", ".docx"]:
            return extract_from_docx(file_path)
        else:
            # Try reading as plain text
            return extract_from_text(file_path)
            
    except Exception as e:
        logger.error(f"Text extraction failed: {e}")
        return False, "", f"Text extraction failed: {str(e)}"


def extract_from_pdf(file_path: str) -> tuple[bool, str, Optional[str]]:
    """
    Extract text from a PDF file using PyMuPDF.
    
    Args:
        file_path: Path to the PDF file
        
    Returns:
        Tuple of (success, extracted_text, error_message)
    """
    try:
        import fitz  # PyMuPDF
        
        logger.info(f"Extracting text from PDF: {file_path}")
        
        doc = fitz.open(file_path)
        text_parts = []
        
        for page_num, page in enumerate(doc):
            text = page.get_text()
            if text.strip():
                text_parts.append(f"--- Page {page_num + 1} ---\n{text}")
        
        doc.close()
        
        full_text = "\n\n".join(text_parts)
        
        if not full_text.strip():
            return False, "", "PDF appears to be empty or contains only images"
        
        logger.info(f"Extracted {len(full_text)} characters from PDF")
        return True, full_text.strip(), None
        
    except ImportError:
        return False, "", "PyMuPDF (fitz) is not installed"
    except Exception as e:
        logger.error(f"PDF extraction failed: {e}")
        return False, "", f"PDF extraction failed: {str(e)}"


def extract_from_text(file_path: str) -> tuple[bool, str, Optional[str]]:
    """
    Extract text from a plain text file.
    
    Args:
        file_path: Path to the text file
        
    Returns:
        Tuple of (success, extracted_text, error_message)
    """
    try:
        logger.info(f"Reading text file: {file_path}")
        
        # Try different encodings
        encodings = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    text = f.read()
                
                if text.strip():
                    logger.info(f"Read {len(text)} characters from text file")
                    return True, text.strip(), None
                    
            except UnicodeDecodeError:
                continue
        
        return False, "", "Could not decode the text file with supported encodings"
        
    except Exception as e:
        logger.error(f"Text file reading failed: {e}")
        return False, "", f"Text file reading failed: {str(e)}"


def extract_from_docx(file_path: str) -> tuple[bool, str, Optional[str]]:
    """
    Extract text from a DOCX file.
    Falls back to basic XML parsing if python-docx is not available.
    
    Args:
        file_path: Path to the DOCX file
        
    Returns:
        Tuple of (success, extracted_text, error_message)
    """
    try:
        # Try using python-docx
        try:
            from docx import Document
            
            logger.info(f"Extracting text from DOCX: {file_path}")
            doc = Document(file_path)
            
            text_parts = []
            for paragraph in doc.paragraphs:
                if paragraph.text.strip():
                    text_parts.append(paragraph.text)
            
            full_text = "\n\n".join(text_parts)
            
            if full_text.strip():
                logger.info(f"Extracted {len(full_text)} characters from DOCX")
                return True, full_text.strip(), None
            else:
                return False, "", "DOCX appears to be empty"
                
        except ImportError:
            # Fallback: basic XML parsing
            return extract_docx_fallback(file_path)
            
    except Exception as e:
        logger.error(f"DOCX extraction failed: {e}")
        return False, "", f"DOCX extraction failed: {str(e)}"


def extract_docx_fallback(file_path: str) -> tuple[bool, str, Optional[str]]:
    """
    Fallback DOCX extraction using zipfile and XML parsing.
    """
    try:
        import zipfile
        import xml.etree.ElementTree as ET
        
        with zipfile.ZipFile(file_path) as z:
            with z.open('word/document.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                
                # Define namespace
                ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
                
                # Extract all text
                text_parts = []
                for elem in root.iter():
                    if elem.tag.endswith('}t'):
                        if elem.text:
                            text_parts.append(elem.text)
                
                full_text = " ".join(text_parts)
                
                if full_text.strip():
                    return True, full_text.strip(), None
                else:
                    return False, "", "DOCX appears to be empty"
                    
    except Exception as e:
        return False, "", f"DOCX fallback extraction failed: {str(e)}"


def combine_texts(transcription: Optional[str], notes: Optional[str]) -> str:
    """
    Combine transcription and notes into a single text.
    
    Args:
        transcription: Transcribed audio text
        notes: Extracted notes text
        
    Returns:
        Combined text
    """
    parts = []
    
    if transcription and transcription.strip():
        parts.append("=== AUDIO TRANSCRIPTION ===\n" + transcription.strip())
    
    if notes and notes.strip():
        parts.append("=== CLINICAL NOTES ===\n" + notes.strip())
    
    return "\n\n".join(parts)


def get_text_preview(text: str, max_length: int = 200) -> str:
    """
    Get a preview of the text.
    
    Args:
        text: Full text
        max_length: Maximum preview length
        
    Returns:
        Preview string
    """
    if not text:
        return ""
    
    # Remove section headers for preview
    preview = text.replace("=== AUDIO TRANSCRIPTION ===", "").replace("=== CLINICAL NOTES ===", "")
    preview = preview.strip()
    
    if len(preview) > max_length:
        preview = preview[:max_length - 3] + "..."
    
    return preview
