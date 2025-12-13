"""
Summary generation service.
Orchestrates the full processing pipeline and generates final documentation.
"""

import logging
import uuid
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.models.schemas import (
    ExtractedEntities,
    ClinicalSummary,
    SOAPNotes,
    WorkflowTask,
    TaskPriority,
    ProcessingResult,
    ProcessingStatus
)
from app.services.groq_client import extract_clinical_entities, generate_clinical_summary
from app.services.rag_pipeline import enhance_with_rag

logger = logging.getLogger(__name__)


def process_and_generate_summary(
    combined_text: str,
    session_id: str
) -> ProcessingResult:
    """
    Run the full processing pipeline: extraction -> RAG enhancement -> summary generation.
    
    Args:
        combined_text: Combined transcription and notes text
        session_id: Session identifier
        
    Returns:
        ProcessingResult with all outputs
    """
    start_time = datetime.now()
    
    try:
        # Step 1: Extract clinical entities
        logger.info(f"[{session_id}] Step 1: Extracting clinical entities")
        extraction_result = extract_clinical_entities(combined_text)
        
        if not extraction_result.success or not extraction_result.entities:
            return ProcessingResult(
                success=False,
                session_id=session_id,
                status=ProcessingStatus.FAILED,
                error=extraction_result.error or "Entity extraction failed"
            )
        
        entities = extraction_result.entities
        
        # Step 2: RAG enhancement - retrieve relevant guidelines
        logger.info(f"[{session_id}] Step 2: RAG enhancement")
        guidelines = enhance_with_rag(
            extracted_entities=entities.model_dump(),
            clinical_text=combined_text
        )
        
        # Step 3: Generate clinical summary with RAG context
        logger.info(f"[{session_id}] Step 3: Generating clinical summary")
        success, summary_dict, error = generate_clinical_summary(entities, guidelines)
        
        if not success:
            # Try to create a basic summary without RAG
            logger.warning(f"[{session_id}] Summary generation failed, creating fallback")
            summary_dict = create_fallback_summary(entities)
        
        # Parse summary into structured objects
        clinical_summary = parse_summary_dict(summary_dict, guidelines)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds()
        
        logger.info(f"[{session_id}] Processing complete in {processing_time:.1f}s")
        
        return ProcessingResult(
            success=True,
            session_id=session_id,
            status=ProcessingStatus.COMPLETED,
            extracted_entities=entities,
            clinical_summary=clinical_summary,
            processing_time_seconds=processing_time
        )
        
    except Exception as e:
        logger.error(f"[{session_id}] Processing failed: {e}")
        return ProcessingResult(
            success=False,
            session_id=session_id,
            status=ProcessingStatus.FAILED,
            error=str(e)
        )


def parse_summary_dict(
    summary_dict: Dict[str, Any],
    guidelines_used: List[str]
) -> ClinicalSummary:
    """
    Parse the summary dictionary into a ClinicalSummary object.
    
    Args:
        summary_dict: Raw summary dictionary from LLM
        guidelines_used: List of guidelines used for context
        
    Returns:
        ClinicalSummary object
    """
    # Parse SOAP notes
    soap_dict = summary_dict.get("soap_notes", {})
    soap_notes = SOAPNotes(
        subjective=soap_dict.get("subjective", ""),
        objective=soap_dict.get("objective", ""),
        assessment=soap_dict.get("assessment", ""),
        plan=soap_dict.get("plan", "")
    )
    
    # Parse tasks
    tasks = []
    tasks_list = summary_dict.get("tasks", [])
    
    for i, task_dict in enumerate(tasks_list):
        try:
            # Parse priority
            priority_str = task_dict.get("priority", "medium").lower()
            priority_map = {
                "low": TaskPriority.LOW,
                "medium": TaskPriority.MEDIUM,
                "high": TaskPriority.HIGH,
                "urgent": TaskPriority.URGENT
            }
            priority = priority_map.get(priority_str, TaskPriority.MEDIUM)
            
            task = WorkflowTask(
                id=task_dict.get("id", f"task_{i+1}"),
                title=task_dict.get("title", ""),
                description=task_dict.get("description", ""),
                priority=priority,
                category=task_dict.get("category", "follow-up"),
                due_date=task_dict.get("due_date"),
                completed=False
            )
            tasks.append(task)
        except Exception as e:
            logger.warning(f"Failed to parse task: {e}")
            continue
    
    # If no tasks were parsed, create default tasks
    if not tasks:
        tasks = create_default_tasks()
    
    # Create guideline references (shortened for display)
    rag_context = []
    for g in guidelines_used[:3]:
        # Extract just the title part
        if ":" in g:
            title = g.split(":")[0].strip()
            rag_context.append(title)
        else:
            rag_context.append(g[:100] + "..." if len(g) > 100 else g)
    
    return ClinicalSummary(
        narrative=summary_dict.get("narrative", ""),
        soap_notes=soap_notes,
        tasks=tasks,
        rag_context_used=rag_context
    )


def create_fallback_summary(entities: ExtractedEntities) -> Dict[str, Any]:
    """
    Create a fallback summary when LLM generation fails.
    
    Args:
        entities: Extracted clinical entities
        
    Returns:
        Basic summary dictionary
    """
    # Create narrative from entities
    narrative_parts = []
    
    if entities.symptoms:
        narrative_parts.append(f"Patient presents with: {', '.join(entities.symptoms)}.")
    
    if entities.patient_history:
        narrative_parts.append(f"Relevant history includes: {', '.join(entities.patient_history)}.")
    
    if entities.clinician_observations:
        narrative_parts.append(f"Clinical observations: {', '.join(entities.clinician_observations)}.")
    
    if entities.assessments:
        narrative_parts.append(f"Assessment: {', '.join(entities.assessments)}.")
    
    if entities.recommendations:
        narrative_parts.append(f"Recommendations: {', '.join(entities.recommendations)}.")
    
    narrative = " ".join(narrative_parts) if narrative_parts else "Unable to generate clinical narrative."
    
    return {
        "narrative": narrative,
        "soap_notes": {
            "subjective": ", ".join(entities.symptoms) if entities.symptoms else "See clinical notes.",
            "objective": ", ".join(entities.clinician_observations) if entities.clinician_observations else "See examination findings.",
            "assessment": ", ".join(entities.assessments) if entities.assessments else "Assessment pending.",
            "plan": ", ".join(entities.recommendations) if entities.recommendations else "Plan to be determined."
        },
        "tasks": []
    }


def create_default_tasks() -> List[WorkflowTask]:
    """Create default workflow tasks when none are generated."""
    return [
        WorkflowTask(
            id="task_review",
            title="Review Clinical Notes",
            description="Review and verify the extracted clinical information",
            priority=TaskPriority.HIGH,
            category="review"
        ),
        WorkflowTask(
            id="task_followup",
            title="Schedule Follow-up",
            description="Schedule follow-up appointment as needed",
            priority=TaskPriority.MEDIUM,
            category="follow-up"
        ),
        WorkflowTask(
            id="task_documentation",
            title="Finalize Documentation",
            description="Complete and sign off on clinical documentation",
            priority=TaskPriority.MEDIUM,
            category="documentation"
        )
    ]


def format_entities_for_display(entities: ExtractedEntities) -> Dict[str, List[str]]:
    """
    Format extracted entities for UI display.
    
    Args:
        entities: ExtractedEntities object
        
    Returns:
        Dictionary with formatted entity lists
    """
    return {
        "Symptoms": entities.symptoms,
        "Patient History": entities.patient_history,
        "Clinician Observations": entities.clinician_observations,
        "Assessments": entities.assessments,
        "Recommendations": entities.recommendations,
        "Medications": entities.medications,
        "Audiological Findings": entities.audiological_findings,
        "Vital Signs": [f"{k}: {v}" for k, v in entities.vital_signs.items()] if entities.vital_signs else []
    }


def generate_task_id() -> str:
    """Generate a unique task ID."""
    return f"task_{uuid.uuid4().hex[:8]}"
