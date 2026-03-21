"""FastAPI route handlers for medical NLP endpoints."""

import logging
from datetime import datetime
from fastapi import APIRouter, HTTPException
from app.models.schemas import (
    AnalysisRequest,
    AnalysisResponse,
    SummarizeRequest,
    ExtractRequest,
    HealthResponse,
)
from app.core.pipeline import get_pipeline

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["medical_nlp"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    try:
        pipeline = get_pipeline()

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            models_loaded={
                "entity_extractor": True,
                "summarizer": pipeline.summarizer is not None,
                "risk_detector": True,
            },
            timestamp=datetime.now(),
        )
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail="Service not healthy")


@router.post("/analyze", response_model=AnalysisResponse)
async def analyze_medical_text(request: AnalysisRequest) -> AnalysisResponse:
    """
    Analyze medical text and extract information.

    This is the main endpoint that processes OCR text, extracts medical entities,
    merges with patient history, generates summaries, detects risks, and returns
    a comprehensive medical intelligence report.

    Args:
        request: AnalysisRequest containing OCR text and optional metadata

    Returns:
        AnalysisResponse with extracted entities, summaries, risks, and confidence scores
    """
    try:
        logger.info(f"Received analysis request for patient: {request.patient_id}")

        if not request.ocr_text or len(request.ocr_text.strip()) == 0:
            raise HTTPException(status_code=400, detail="OCR text cannot be empty")

        # Get pipeline instance
        pipeline = get_pipeline()

        # Process request
        response = pipeline.process(request)

        logger.info(f"Analysis successful for patient: {request.patient_id}")
        return response

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Analysis failed: {str(e)}"
        )


@router.post("/summarize")
async def summarize_medical_text(request: SummarizeRequest) -> dict:
    """
    Generate medical summaries for given text.

    Returns both short (1-2 sentence) and long (paragraph) summaries
    with optional integration of patient history.

    Args:
        request: SummarizeRequest with text and optional previous records

    Returns:
        Dictionary with short_summary and long_summary fields
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        pipeline = get_pipeline()

        # Clean text first
        cleaned_text = pipeline.text_cleaner.clean(request.text)

        # Merge with history if provided
        if request.previous_records:
            merged_text, _, _ = pipeline.context_merger.merge_with_history(
                cleaned_text, [], request.previous_records
            )
        else:
            merged_text = cleaned_text

        # Generate summaries
        short_summary = pipeline.summarizer.generate_short_summary(merged_text)
        long_summary = pipeline.summarizer.generate_long_summary(merged_text)

        logger.info("Summarization completed successfully")

        return {
            "short_summary": short_summary,
            "long_summary": long_summary,
            "input_length": len(request.text),
            "cleaned_length": len(cleaned_text),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Summarization failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Summarization failed: {str(e)}"
        )


@router.post("/extract")
async def extract_entities(request: ExtractRequest) -> dict:
    """
    Extract medical entities from text.

    Returns entities grouped by type with normalized terms.

    Args:
        request: ExtractRequest with text to analyze

    Returns:
        Dictionary with extracted entities grouped by type
    """
    try:
        if not request.text or len(request.text.strip()) == 0:
            raise HTTPException(status_code=400, detail="Text cannot be empty")

        pipeline = get_pipeline()

        # Clean text
        cleaned_text = pipeline.text_cleaner.clean(request.text)

        # Extract entities
        entities_by_type = pipeline.extract_entities(cleaned_text)

        # Convert to JSON-serializable format
        result = {}
        for entity_type, entities in entities_by_type.items():
            result[entity_type] = [
                {
                    "text": e.text,
                    "normalized": e.normalized,
                    "confidence": e.confidence,
                    "synonyms": e.synonyms,
                }
                for e in entities
            ]

        logger.info(f"Entity extraction completed: {sum(len(v) for v in result.values())} entities")

        return {
            "entities": result,
            "total_entities": sum(len(v) for v in result.values()),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Entity extraction failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Entity extraction failed: {str(e)}"
        )


@router.get("/models")
async def get_models_info() -> dict:
    """Get information about loaded models."""
    try:
        pipeline = get_pipeline()

        return {
            "models": pipeline.model_versions,
            "entity_extraction": {
                "primary": "scispaCy (en_core_sci_md)",
                "secondary": "Custom rule-based patterns",
            },
            "summarization": {
                "model": "google/flan-t5-base",
                "type": "Sequence-to-sequence transformer",
            },
        }

    except Exception as e:
        logger.error(f"Failed to get models info: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve models info")
