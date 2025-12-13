"""
SQLite database models and session management.
Uses SQLAlchemy for ORM with async support.
"""

import json
from datetime import datetime
from typing import Optional, Dict, Any
from sqlalchemy import create_engine, Column, String, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from app.config import settings

# Create database directory if needed
settings.db_path.parent.mkdir(parents=True, exist_ok=True)

# Database setup
DATABASE_URL = f"sqlite:///{settings.db_path}"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class SessionModel(Base):
    """SQLAlchemy model for clinical documentation sessions."""
    
    __tablename__ = "sessions"
    
    id = Column(String, primary_key=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    status = Column(String, default="pending")
    
    # File paths
    audio_file_path = Column(String, nullable=True)
    audio_filename = Column(String, nullable=True)
    notes_file_path = Column(String, nullable=True)
    notes_filename = Column(String, nullable=True)
    
    # Processing results (stored as JSON strings)
    transcription_json = Column(Text, nullable=True)
    extracted_entities_json = Column(Text, nullable=True)
    clinical_summary_json = Column(Text, nullable=True)
    combined_text = Column(Text, nullable=True)
    
    # Error tracking
    error_message = Column(Text, nullable=True)
    
    def set_transcription(self, data: Dict[str, Any]):
        """Store transcription result as JSON."""
        self.transcription_json = json.dumps(data, default=str)
    
    def get_transcription(self) -> Optional[Dict[str, Any]]:
        """Retrieve transcription result from JSON."""
        if self.transcription_json:
            return json.loads(self.transcription_json)
        return None
    
    def set_extracted_entities(self, data: Dict[str, Any]):
        """Store extracted entities as JSON."""
        self.extracted_entities_json = json.dumps(data, default=str)
    
    def get_extracted_entities(self) -> Optional[Dict[str, Any]]:
        """Retrieve extracted entities from JSON."""
        if self.extracted_entities_json:
            return json.loads(self.extracted_entities_json)
        return None
    
    def set_clinical_summary(self, data: Dict[str, Any]):
        """Store clinical summary as JSON."""
        self.clinical_summary_json = json.dumps(data, default=str)
    
    def get_clinical_summary(self) -> Optional[Dict[str, Any]]:
        """Retrieve clinical summary from JSON."""
        if self.clinical_summary_json:
            return json.loads(self.clinical_summary_json)
        return None


# Create all tables
def init_db():
    """Initialize the database tables."""
    Base.metadata.create_all(bind=engine)


def get_db():
    """Get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Database helper functions
class SessionRepository:
    """Repository for session CRUD operations."""
    
    @staticmethod
    def create(db, session_id: str) -> SessionModel:
        """Create a new session."""
        session = SessionModel(id=session_id)
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get(db, session_id: str) -> Optional[SessionModel]:
        """Get a session by ID."""
        return db.query(SessionModel).filter(SessionModel.id == session_id).first()
    
    @staticmethod
    def get_all(db, skip: int = 0, limit: int = 100) -> list:
        """Get all sessions."""
        return db.query(SessionModel).order_by(
            SessionModel.created_at.desc()
        ).offset(skip).limit(limit).all()
    
    @staticmethod
    def update(db, session_id: str, **kwargs) -> Optional[SessionModel]:
        """Update a session."""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            for key, value in kwargs.items():
                if hasattr(session, key):
                    setattr(session, key, value)
            session.updated_at = datetime.utcnow()
            db.commit()
            db.refresh(session)
        return session
    
    @staticmethod
    def delete(db, session_id: str) -> bool:
        """Delete a session."""
        session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
        if session:
            db.delete(session)
            db.commit()
            return True
        return False
    
    @staticmethod
    def count(db) -> int:
        """Count total sessions."""
        return db.query(SessionModel).count()


# Initialize database on module load
init_db()
