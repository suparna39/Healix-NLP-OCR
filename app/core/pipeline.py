"""Core medical NLP pipeline and orchestration."""

import logging
import time
from typing import Optional, Dict, Any, List
from datetime import datetime
from app.core.config import settings
from app.models.schemas import AnalysisRequest, AnalysisResponse, MedicalEntity, MedicalRecord
from app.nlp.ocr_cleaner import OCRTextCleaner
from app.nlp.entity_extractor import MedicalEntityExtractor
from app.nlp.normalizer import MedicalTermNormalizer
from app.nlp.context_merger import ContextMerger
from app.nlp.summarizer import create_summarizer
from app.nlp.risk_detector import RiskDetector, ConfidenceScorer

logger = logging.getLogger(__name__)
_pipeline_instance = None


class MedicalNLPPipeline:
    """Complete medical NLP processing pipeline."""

    def __init__(self):
        """Initialize all pipeline components."""
        try:
            logger.info("Initializing HELIX Medical NLP Pipeline")
            logger.info("Initializing OCR text cleaner...")
            self.text_cleaner = OCRTextCleaner()
            logger.info("Text cleaner initialized")
            
            logger.info("Initializing entity extractor...")
            self.entity_extractor = MedicalEntityExtractor(use_scispacy=settings.USE_SCISPACY)
            logger.info("Entity extractor initialized")
            
            logger.info("Initializing term normalizer...")
            self.term_normalizer = MedicalTermNormalizer()
            logger.info("Term normalizer initialized")
            
            logger.info("Initializing context merger...")
            self.context_merger = ContextMerger()
            logger.info("Context merger initialized")
            
            logger.info(f"Initializing summarizer with model: {settings.SUMMARIZATION_MODEL}")
            self.summarizer = create_summarizer(settings.SUMMARIZATION_MODEL)
            logger.info("Summarizer initialized")
            
            logger.info("Initializing risk detector...")
            self.risk_detector = RiskDetector()
            logger.info("Risk detector initialized")
            
            logger.info("Initializing confidence scorer...")
            self.confidence_scorer = ConfidenceScorer()
            logger.info("Confidence scorer initialized")
            
            self.model_versions = {
                "entity_extractor": "pattern-based + optional scispacy",
                "summarization": settings.SUMMARIZATION_MODEL or "rule-based fallback",
                "system_version": "1.0.0",
            }
            logger.info("Pipeline initialized successfully")
        except Exception as e:
            logger.critical(f"Failed to initialize pipeline: {e}", exc_info=True)
            raise

    def process(self, request: AnalysisRequest) -> AnalysisResponse:
        """Main processing method."""
        start_time = time.time()
        logger.info(f"Processing analysis for patient: {request.patient_id}")

        try:
            # Stage 1: Clean text
            cleaned_text = self.text_cleaner.clean(request.ocr_text)

            # Stage 2: Extract entities
            entities = self.entity_extractor.extract(cleaned_text)
            entities = self.term_normalizer.normalize_entities(entities)

            # Group entities
            grouped_entities = {
                "diseases": [e for e in entities if e.entity_type == "disease"],
                "symptoms": [e for e in entities if e.entity_type == "symptom"],
                "medications": [e for e in entities if e.entity_type == "medication"],
                "tests": [e for e in entities if e.entity_type == "test"],
                "procedures": [e for e in entities if e.entity_type == "procedure"],
                "measurements": [e for e in entities if e.entity_type == "measurement"],
                "anatomy": [e for e in entities if e.entity_type == "anatomy"],
            }

            # Stage 3: Merge history
            history_summary = "No previous records available."
            if request.previous_records:
                merged_text, _, history_summary = self.context_merger.merge_with_history(
                    cleaned_text, entities, request.previous_records
                )
            else:
                merged_text = cleaned_text

            # Stage 4: Generate summaries
            short_summary = self.summarizer.generate_short_summary(merged_text)
            long_summary = self.summarizer.generate_long_summary(merged_text)

            # Stage 5: Detect risks
            risks = self.risk_detector.detect_all_risks(
                text=merged_text,
                diseases=grouped_entities["diseases"],
                symptoms=grouped_entities["symptoms"],
                medications=grouped_entities["medications"],
                measurements=grouped_entities["measurements"],
            )

            # Stage 6: Score confidence
            confidence_scores = self.confidence_scorer.generate_scores(
                text=merged_text,
                entities=entities,
                summary=long_summary,
                historical_entities=[],
                integration_text=merged_text
            )

            # Build response
            processing_time = (time.time() - start_time) * 1000

            response = AnalysisResponse(
                patient_id=request.patient_id or "UNKNOWN",
                entities={
                    "diseases": [e.model_dump() for e in grouped_entities["diseases"]],
                    "symptoms": [e.model_dump() for e in grouped_entities["symptoms"]],
                    "medications": [e.model_dump() for e in grouped_entities["medications"]],
                    "tests": [e.model_dump() for e in grouped_entities["tests"]],
                    "procedures": [e.model_dump() for e in grouped_entities["procedures"]],
                    "measurements": [e.model_dump() for e in grouped_entities["measurements"]],
                    "anatomy": [e.model_dump() for e in grouped_entities["anatomy"]],
                },
                normalized_terms={e.text: e.normalized for e in entities if e.normalized},
                summary_short=short_summary,
                summary_long=long_summary,
                history_integration=history_summary,
                risk_flags=[r.model_dump() if hasattr(r, 'model_dump') else vars(r) for r in risks],
                confidence=confidence_scores,
                notes_for_doctor=self._generate_notes(grouped_entities, risks),
                warnings=self._generate_warnings(grouped_entities, risks),
                processing_time_ms=processing_time,
                model_versions=self.model_versions,
            )

            logger.info(f"Analysis successful for patient: {request.patient_id}")
            return response

        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            raise

    @staticmethod
    def _generate_notes(grouped_entities: Dict, risks: List) -> List[str]:
        """Generate clinical notes."""
        notes = []
        if not grouped_entities.get("diseases") and not grouped_entities.get("symptoms"):
            notes.append("Limited medical information extracted")
        if len(risks) > 0:
            notes.append(f"Review {len(risks)} detected risk(s)")
        if not notes:
            notes.append("Analysis complete - review results")
        return notes

    @staticmethod
    def _generate_warnings(grouped_entities: Dict, risks: List) -> List[str]:
        """Generate warnings."""
        warnings = []
        total = sum(len(v) for v in grouped_entities.values())
        if total < 5:
            warnings.append("Low entity count - check OCR quality")
        if len(risks) > 3:
            warnings.append("Multiple risks detected")
        return warnings


def initialize_pipeline() -> MedicalNLPPipeline:
    """Initialize global pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = MedicalNLPPipeline()
        logger.info("Global pipeline initialized")
    return _pipeline_instance


def get_pipeline() -> MedicalNLPPipeline:
    """Get global pipeline instance."""
    global _pipeline_instance
    if _pipeline_instance is None:
        _pipeline_instance = initialize_pipeline()
    return _pipeline_instance
