"""Core data models for the medical NLP system."""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


class SeverityLevel(str, Enum):
    """Severity levels for medical findings."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFORMATIONAL = "informational"


class MedicalEntity(BaseModel):
    """Represents an extracted medical entity."""
    text: str = Field(..., description="The original text of the entity")
    entity_type: str = Field(..., description="Type: disease, symptom, medication, procedure, test, measurement, anatomy")
    normalized: Optional[str] = Field(None, description="Normalized medical term")
    confidence: float = Field(..., description="Confidence score 0-1")
    start_pos: int = Field(..., description="Starting character position in text")
    end_pos: int = Field(..., description="Ending character position in text")
    explanation: Optional[str] = Field(None, description="Why this entity was extracted")
    synonyms: List[str] = Field(default_factory=list, description="Known synonyms")
    cui: Optional[str] = Field(None, description="UMLS Concept Unique Identifier if available")


class MedicalRecord(BaseModel):
    """Represents a patient's medical record."""
    record_id: str
    date: datetime
    document_type: str  # e.g., "lab_report", "discharge_summary", "consultation"
    raw_text: str
    source: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Request for medical text analysis."""
    ocr_text: str = Field(..., description="Raw OCR text from medical document")
    patient_id: Optional[str] = Field(None, description="Patient identifier")
    age: Optional[int] = Field(None, description="Patient age")
    sex: Optional[str] = Field(None, description="Patient sex (M/F/Other)")
    date: Optional[datetime] = Field(None, description="Document date")
    source_type: Optional[str] = Field(None, description="Type of medical document")
    known_conditions: Optional[List[str]] = Field(None, description="Known medical conditions")
    previous_records: Optional[List[MedicalRecord]] = Field(None, description="Previous medical records")


class ConfidenceScores(BaseModel):
    """Confidence scores for different components."""
    entity_extraction: float = Field(..., description="Confidence in entity extraction (0-1)")
    summarization: float = Field(..., description="Confidence in summarization (0-1)")
    context_understanding: float = Field(..., description="Confidence in understanding context (0-1)")
    overall: float = Field(..., description="Overall system confidence (0-1)")


class RiskFlag(BaseModel):
    """Represents a detected risk or flag."""
    flag_type: str  # e.g., "disease", "symptom_cluster", "medication_interaction", "abnormal_value"
    severity: SeverityLevel
    description: str
    explanation: str
    entities_involved: List[str]
    recommended_action: Optional[str] = None


class AnalysisResponse(BaseModel):
    """Complete response from medical text analysis."""
    patient_id: Optional[str]
    entities: Dict[str, List[MedicalEntity]] = Field(
        default_factory=lambda: {
            "diseases": [],
            "symptoms": [],
            "medications": [],
            "tests": [],
            "procedures": [],
            "measurements": [],
            "anatomy": [],
        },
        description="Extracted medical entities grouped by type"
    )
    normalized_terms: Dict[str, str] = Field(default_factory=dict, description="Original -> Normalized mappings")
    
    summary_short: str = Field(..., description="Brief clinical summary (1-2 sentences)")
    summary_long: str = Field(..., description="Comprehensive summary with context")
    
    history_integration: Optional[str] = Field(None, description="How current findings relate to history")
    
    risk_flags: List[RiskFlag] = Field(default_factory=list, description="Detected risks and alerts")
    
    confidence: ConfidenceScores
    
    notes_for_doctor: List[str] = Field(default_factory=list, description="Action items for clinician")
    warnings: List[str] = Field(default_factory=list, description="Safety warnings")
    
    processing_time_ms: float = Field(..., description="Time taken to process request")
    model_versions: Dict[str, str] = Field(default_factory=dict, description="Versions of models used")


class SummarizeRequest(BaseModel):
    """Request for text summarization."""
    text: str = Field(..., description="Medical text to summarize")
    previous_records: Optional[List[MedicalRecord]] = Field(None, description="Previous medical records")
    max_length: Optional[int] = Field(None, description="Maximum summary length")


class ExtractRequest(BaseModel):
    """Request for entity extraction."""
    text: str = Field(..., description="Medical text to analyze")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    models_loaded: Dict[str, bool]
    timestamp: datetime
