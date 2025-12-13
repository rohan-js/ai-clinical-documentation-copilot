"""
Groq API client wrapper.
Handles LLM calls for clinical information extraction and summarization.
"""

import json
import logging
from typing import Optional, Dict, Any, List
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from groq import Groq
from groq._exceptions import RateLimitError, APIError

from app.config import settings
from app.models.schemas import ExtractedEntities, ExtractionResult
from app.utils.helpers import sanitize_json_response

logger = logging.getLogger(__name__)

# Global client instance
_groq_client = None


def get_groq_client() -> Groq:
    """Get or initialize the Groq client."""
    global _groq_client
    
    if _groq_client is None:
        _groq_client = Groq(api_key=settings.groq_api_key)
        logger.info("Groq client initialized")
    
    return _groq_client


# Extraction prompt template
EXTRACTION_PROMPT = """You are a clinical documentation specialist. Analyze the following clinical conversation or notes and extract structured information.

Extract the following categories:
1. **Symptoms**: Patient-reported symptoms and complaints
2. **Patient History**: Relevant medical history, medications, allergies
3. **Clinician Observations**: Clinical observations made during the visit
4. **Assessments**: Clinical assessments, diagnoses, or differential diagnoses
5. **Recommendations**: Treatment recommendations or advice given
6. **Medications**: Current medications or newly prescribed ones
7. **Vital Signs**: Any vital signs mentioned (as key-value pairs)
8. **Audiological Findings**: Hearing test results, audiogram data, or audiology-specific findings (leave empty if not applicable)

IMPORTANT: Return your response as valid JSON with this exact structure:
```json
{{
    "symptoms": ["symptom1", "symptom2"],
    "patient_history": ["history item 1", "history item 2"],
    "clinician_observations": ["observation 1", "observation 2"],
    "assessments": ["assessment 1", "assessment 2"],
    "recommendations": ["recommendation 1", "recommendation 2"],
    "medications": ["medication 1", "medication 2"],
    "vital_signs": {{"key": "value"}},
    "audiological_findings": ["finding 1", "finding 2"]
}}
```

If a category has no relevant information, use an empty array [] or empty object {{}}.

Clinical Text to Analyze:
---
{text}
---

Return only the JSON, no additional text."""



SUMMARY_PROMPT = """You are a clinical documentation specialist. Based on the extracted clinical information and relevant guidelines, generate comprehensive clinical documentation.

Extracted Information:
{entities}

Relevant Clinical Guidelines:
{guidelines}

Generate the following:

1. **Clinical Narrative**: A well-formatted paragraph summarizing the patient encounter, written in professional clinical language.

2. **SOAP Notes**:
   - **Subjective**: Patient's chief complaint, symptoms, and relevant history in their own words
   - **Objective**: Clinical observations, examination findings, test results
   - **Assessment**: Clinical assessment, diagnosis, or differential diagnoses
   - **Plan**: Treatment plan, medications, follow-up recommendations

3. **Workflow Tasks**: A list of follow-up tasks with priorities. Include tasks like:
   - Schedule follow-up appointments
   - Order tests (hearing test, lab work, imaging)
   - Referrals to specialists
   - Medication management
   - Patient education items

Return as valid JSON:
```json
{{
    "narrative": "Clinical narrative text here...",
    "soap_notes": {{
        "subjective": "Subjective findings...",
        "objective": "Objective findings...",
        "assessment": "Assessment...",
        "plan": "Plan..."
    }},
    "tasks": [
        {{
            "id": "task_1",
            "title": "Task title",
            "description": "Task description",
            "priority": "high|medium|low|urgent",
            "category": "follow-up|testing|referral|medication|education",
            "due_date": "Optional date or timeframe"
        }}
    ]
}}
```

Return only valid JSON."""


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((RateLimitError, APIError))
)
def call_groq_api(
    prompt: str,
    system_message: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tokens: Optional[int] = None
) -> tuple[bool, str, Optional[str]]:
    """
    Make a call to the Groq API with retry logic.
    
    Args:
        prompt: The user prompt
        system_message: Optional system message
        temperature: Optional temperature override
        max_tokens: Optional max tokens override
        
    Returns:
        Tuple of (success, response_text, error_message)
    """
    try:
        client = get_groq_client()
        
        messages = []
        
        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })
        
        messages.append({
            "role": "user",
            "content": prompt
        })
        
        response = client.chat.completions.create(
            model=settings.groq_model,
            messages=messages,
            temperature=temperature or settings.groq_temperature,
            max_tokens=max_tokens or settings.groq_max_tokens
        )
        
        content = response.choices[0].message.content
        logger.info(f"Groq API call successful, received {len(content)} characters")
        
        return True, content, None
        
    except RateLimitError as e:
        logger.warning(f"Rate limit hit: {e}")
        raise  # Let retry handle it
    except APIError as e:
        logger.warning(f"API error: {e}")
        raise  # Let retry handle it
    except Exception as e:
        logger.error(f"Groq API call failed: {e}")
        return False, "", str(e)


def extract_clinical_entities(text: str) -> ExtractionResult:
    """
    Extract clinical entities from text using the LLM.
    
    Args:
        text: Combined clinical text (transcription + notes)
        
    Returns:
        ExtractionResult with extracted entities
    """
    if not text or not text.strip():
        return ExtractionResult(
            success=False,
            error="No text provided for extraction"
        )
    
    try:
        prompt = EXTRACTION_PROMPT.format(text=text)
        
        success, response, error = call_groq_api(
            prompt=prompt,
            system_message="You are a medical documentation AI assistant. Always respond with valid JSON only, no explanations.",
            temperature=0.1  # Lower temperature for more consistent extraction
        )
        
        if not success:
            return ExtractionResult(
                success=False,
                raw_response=response,
                error=error
            )
        
        # Log raw response for debugging
        logger.debug(f"Raw LLM response (first 500 chars): {response[:500]}")
        
        # Parse the JSON response
        parsed = sanitize_json_response(response)
        
        if not parsed:
            logger.error(f"Failed to parse JSON. Response preview: {response[:200]}")
            return ExtractionResult(
                success=False,
                raw_response=response,
                error=f"Failed to parse LLM response as JSON. Response starts with: {response[:100]}..."
            )
        
        # Create ExtractedEntities from parsed data
        entities = ExtractedEntities(
            symptoms=parsed.get("symptoms", []),
            patient_history=parsed.get("patient_history", []),
            clinician_observations=parsed.get("clinician_observations", []),
            assessments=parsed.get("assessments", []),
            recommendations=parsed.get("recommendations", []),
            medications=parsed.get("medications", []),
            vital_signs=parsed.get("vital_signs", {}),
            audiological_findings=parsed.get("audiological_findings", [])
        )
        
        logger.info("Clinical entities extracted successfully")
        
        return ExtractionResult(
            success=True,
            entities=entities,
            raw_response=response
        )
        
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}", exc_info=True)
        return ExtractionResult(
            success=False,
            error=f"Entity extraction failed: {str(e)}"
        )


def generate_clinical_summary(
    entities: ExtractedEntities,
    guidelines: List[str]
) -> tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Generate a clinical summary using the LLM with RAG context.
    
    Args:
        entities: Extracted clinical entities
        guidelines: Retrieved guideline snippets for context
        
    Returns:
        Tuple of (success, summary_dict, error_message)
    """
    try:
        # Format entities for prompt
        entities_str = json.dumps(entities.model_dump(), indent=2)
        
        # Format guidelines
        guidelines_str = "\n\n".join([
            f"- {g}" for g in guidelines
        ]) if guidelines else "No specific guidelines retrieved."
        
        prompt = SUMMARY_PROMPT.format(
            entities=entities_str,
            guidelines=guidelines_str
        )
        
        success, response, error = call_groq_api(
            prompt=prompt,
            system_message="You are a clinical documentation specialist. Generate comprehensive, professional medical documentation.",
            temperature=0.3
        )
        
        if not success:
            return False, {}, error
        
        # Parse the JSON response
        parsed = sanitize_json_response(response)
        
        if not parsed:
            # Try to create a basic summary from the raw response
            return False, {"raw_response": response}, "Failed to parse summary as JSON"
        
        logger.info("Clinical summary generated successfully")
        
        return True, parsed, None
        
    except Exception as e:
        logger.error(f"Summary generation failed: {e}")
        return False, {}, str(e)


def refine_with_context(
    original_summary: Dict[str, Any],
    additional_context: str
) -> tuple[bool, Dict[str, Any], Optional[str]]:
    """
    Refine an existing summary with additional context.
    
    Args:
        original_summary: The original summary dict
        additional_context: Additional context to incorporate
        
    Returns:
        Tuple of (success, refined_summary, error_message)
    """
    refine_prompt = f"""Review and refine the following clinical summary based on the additional clinical guidelines provided.

Original Summary:
{json.dumps(original_summary, indent=2)}

Additional Clinical Guidelines to Consider:
{additional_context}

Enhance the summary by:
1. Adding relevant clinical terminology from the guidelines
2. Ensuring recommendations align with best practices
3. Adding any missing follow-up tasks based on guidelines
4. Improving the clinical narrative with appropriate context

Return the refined summary in the same JSON format as the original."""

    try:
        success, response, error = call_groq_api(
            prompt=refine_prompt,
            system_message="You are a clinical documentation specialist refining medical documentation.",
            temperature=0.3
        )
        
        if not success:
            return False, original_summary, error
        
        parsed = sanitize_json_response(response)
        
        if not parsed:
            return False, original_summary, "Failed to parse refined summary"
        
        return True, parsed, None
        
    except Exception as e:
        logger.error(f"Summary refinement failed: {e}")
        return False, original_summary, str(e)
