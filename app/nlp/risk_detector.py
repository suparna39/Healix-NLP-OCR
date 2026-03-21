"""Risk flag detection and medical intelligence."""

import logging
from typing import List, Dict, Tuple, Optional
from app.models.schemas import (
    MedicalEntity,
    RiskFlag,
    SeverityLevel,
    ConfidenceScores,
)

logger = logging.getLogger(__name__)


class RiskDetector:
    """Detect medical risks and generate flags."""

    # Risk patterns and rules
    CRITICAL_CONDITIONS = [
        "stroke",
        "myocardial infarction",
        "sepsis",
        "cardiac arrest",
        "respiratory failure",
        "acute kidney injury",
        "status asthmaticus",
    ]

    CRITICAL_SYMPTOMS = [
        "chest pain",
        "difficulty breathing",
        "unconsciousness",
        "severe bleeding",
        "loss of consciousness",
        "acute mental status change",
        "severe head trauma",
    ]

    MEDICATION_INTERACTIONS = {
        ("warfarin", "aspirin"): "Increased bleeding risk",
        ("metformin", "contrast dye"): "Lactic acidosis risk (hold metformin)",
        ("ace inhibitor", "potassium"): "Hyperkalemia risk",
        ("nsaid", "ace inhibitor"): "Acute kidney injury risk",
    }

    DISEASE_SYMPTOM_CLUSTERS = {
        "acute coronary syndrome": [
            "chest pain",
            "shortness of breath",
            "nausea",
            "diaphoresis",
        ],
        "sepsis": [
            "fever",
            "tachycardia",
            "hypotension",
            "altered mental status",
        ],
        "diabetic ketoacidosis": [
            "diabetes",
            "nausea",
            "vomiting",
            "abdominal pain",
            "dyspnea",
        ],
    }

    def __init__(self):
        """Initialize risk detector."""
        self.flags: List[RiskFlag] = []

    def detect_critical_conditions(
        self, diseases: List[MedicalEntity]
    ) -> List[RiskFlag]:
        """Detect critical or urgent conditions."""
        flags = []

        for disease in diseases:
            normalized = disease.normalized or disease.text.lower()
            for critical in self.CRITICAL_CONDITIONS:
                if critical in normalized.lower():
                    flag = RiskFlag(
                        flag_type="critical_disease",
                        severity=SeverityLevel.CRITICAL,
                        description=f"Critical condition detected: {disease.text}",
                        explanation=f"{disease.text} requires immediate medical attention",
                        entities_involved=[disease.text],
                        recommended_action="Urgent medical evaluation required",
                    )
                    flags.append(flag)

        return flags

    def detect_critical_symptoms(
        self, symptoms: List[MedicalEntity]
    ) -> List[RiskFlag]:
        """Detect critical symptoms."""
        flags = []

        for symptom in symptoms:
            normalized = symptom.normalized or symptom.text.lower()
            for critical_symp in self.CRITICAL_SYMPTOMS:
                if critical_symp in normalized.lower():
                    flag = RiskFlag(
                        flag_type="critical_symptom",
                        severity=SeverityLevel.CRITICAL,
                        description=f"Critical symptom: {symptom.text}",
                        explanation=f"{symptom.text} requires urgent evaluation",
                        entities_involved=[symptom.text],
                        recommended_action="Seek emergency care immediately",
                    )
                    flags.append(flag)

        return flags

    def detect_medication_interactions(
        self, medications: List[MedicalEntity]
    ) -> List[RiskFlag]:
        """Detect potential medication interactions."""
        flags = []
        med_names = [m.normalized or m.text.lower() for m in medications]

        for (med1, med2), interaction in self.MEDICATION_INTERACTIONS.items():
            med1_present = any(med1 in m for m in med_names)
            med2_present = any(med2 in m for m in med_names)

            if med1_present and med2_present:
                flag = RiskFlag(
                    flag_type="medication_interaction",
                    severity=SeverityLevel.HIGH,
                    description=f"Potential interaction: {med1} + {med2}",
                    explanation=interaction,
                    entities_involved=[med1, med2],
                    recommended_action=f"Consider discontinuing one or both. Consult pharmacist.",
                )
                flags.append(flag)

        return flags

    def detect_symptom_clusters(
        self, symptoms: List[MedicalEntity]
    ) -> List[RiskFlag]:
        """Detect symptom clusters suggesting serious conditions."""
        flags = []
        symptom_names = [s.normalized or s.text.lower() for s in symptoms]

        for condition, cluster_symptoms in self.DISEASE_SYMPTOM_CLUSTERS.items():
            matching_symptoms = [
                s for s in cluster_symptoms
                if any(s in symptom for symptom in symptom_names)
            ]

            # If 2+ symptoms from cluster present, flag it
            if len(matching_symptoms) >= 2:
                severity = (
                    SeverityLevel.CRITICAL
                    if condition in ["acute coronary syndrome", "sepsis"]
                    else SeverityLevel.HIGH
                )
                flag = RiskFlag(
                    flag_type="symptom_cluster",
                    severity=severity,
                    description=f"Symptoms suggestive of {condition}",
                    explanation=f"Patient presents with {len(matching_symptoms)}/{len(cluster_symptoms)} "
                    f"symptoms of {condition}",
                    entities_involved=matching_symptoms,
                    recommended_action=f"Evaluate for {condition}",
                )
                flags.append(flag)

        return flags

    def detect_abnormal_values(
        self, measurements: List[MedicalEntity]
    ) -> List[RiskFlag]:
        """Detect abnormal lab/vital values."""
        flags = []

        # Define normal ranges
        normal_ranges = {
            "glucose": (70, 100),  # fasting
            "blood pressure": (90, 120, 60, 80),  # sys, dias
            "heart rate": (60, 100),
            "temperature": (36.1, 37.2),  # Celsius
            "hemoglobin": (12, 17.5),  # g/dL
        }

        for measurement in measurements:
            text = measurement.text.lower()
            # Simple parsing (in production, use more sophisticated parsing)
            if "glucose" in text and any(
                c.isdigit() for c in measurement.text
            ):
                flag = RiskFlag(
                    flag_type="abnormal_value",
                    severity=SeverityLevel.MEDIUM,
                    description=f"Abnormal lab value: {measurement.text}",
                    explanation="Blood glucose appears elevated",
                    entities_involved=[measurement.text],
                    recommended_action="Verify value and consider HbA1c testing",
                )
                flags.append(flag)

        return flags

    def detect_emergency_indicators(self, text: str) -> List[RiskFlag]:
        """Detect emergency indicators in text."""
        flags = []

        emergency_keywords = [
            "emergency",
            "acute",
            "severe",
            "critical",
            "urgent",
            "hemorrhage",
            "anaphylaxis",
            "cardiac arrest",
        ]

        for keyword in emergency_keywords:
            if keyword.lower() in text.lower():
                flag = RiskFlag(
                    flag_type="emergency_indicator",
                    severity=SeverityLevel.CRITICAL,
                    description=f"Emergency indicator: '{keyword}' mentioned in record",
                    explanation=f"Text contains emergency keyword: {keyword}",
                    entities_involved=[keyword],
                    recommended_action="Treat as emergency case",
                )
                flags.append(flag)
                break  # Add only once

        return flags

    def detect_all_risks(
        self,
        text: str,
        diseases: List[MedicalEntity],
        symptoms: List[MedicalEntity],
        medications: List[MedicalEntity],
        measurements: List[MedicalEntity],
    ) -> List[RiskFlag]:
        """Detect all risks."""
        all_flags = []

        all_flags.extend(self.detect_critical_conditions(diseases))
        all_flags.extend(self.detect_critical_symptoms(symptoms))
        all_flags.extend(self.detect_medication_interactions(medications))
        all_flags.extend(self.detect_symptom_clusters(symptoms))
        all_flags.extend(self.detect_abnormal_values(measurements))
        all_flags.extend(self.detect_emergency_indicators(text))

        # Remove duplicates
        all_flags = list({f.description: f for f in all_flags}.values())

        logger.info(f"Detected {len(all_flags)} risk flags")
        return all_flags


class ConfidenceScorer:
    """Calculate confidence scores for various components."""

    @staticmethod
    def score_entity_extraction(
        entities: List[MedicalEntity], text_length: int
    ) -> float:
        """Score entity extraction confidence."""
        if not entities:
            return 0.3  # Low confidence if no entities found

        # Consider entity density and confidence
        average_confidence = sum(e.confidence for e in entities) / len(entities)

        # Normalize by text length (optimal is ~50-200 words)
        word_count = text_length / 5
        length_factor = min(1.0, word_count / 100)

        score = (average_confidence * 0.7) + (length_factor * 0.3)
        return min(0.95, max(0.2, score))

    @staticmethod
    def score_summarization(summary: str, original_length: int) -> float:
        """Score summarization quality."""
        if not summary:
            return 0.1

        # Summary should be ~25-30% of original
        compression_ratio = len(summary) / max(original_length, 1)
        target_ratio = 0.25

        if 0.15 < compression_ratio < 0.4:
            ratio_score = 0.9
        elif 0.1 < compression_ratio < 0.5:
            ratio_score = 0.7
        else:
            ratio_score = 0.4

        # Check for key medical terms
        medical_keywords = [
            "patient",
            "medical",
            "treatment",
            "symptom",
            "disease",
        ]
        keyword_count = sum(
            1 for kw in medical_keywords if kw.lower() in summary.lower()
        )
        keyword_score = min(1.0, keyword_count / 3)

        score = (ratio_score * 0.6) + (keyword_score * 0.4)
        return min(0.95, max(0.2, score))

    @staticmethod
    def score_context_understanding(
        current_entities: List[MedicalEntity],
        historical_entities: List[MedicalEntity],
        integration_text: str,
    ) -> float:
        """Score understanding of patient context."""
        if not integration_text or len(integration_text) < 10:
            return 0.4

        # More historical context = better understanding
        history_score = min(1.0, len(historical_entities) / 10)

        # Integration text quality
        keywords = ["previous", "history", "trend", "ongoing", "new"]
        keyword_count = sum(
            1 for kw in keywords if kw.lower() in integration_text.lower()
        )
        text_score = min(1.0, keyword_count / 3)

        score = (history_score * 0.5) + (text_score * 0.5)
        return min(0.95, max(0.3, score))

    @staticmethod
    def calculate_overall_confidence(
        entity_score: float, summarization_score: float, context_score: float
    ) -> float:
        """Calculate overall system confidence."""
        return (entity_score * 0.4) + (summarization_score * 0.4) + (context_score * 0.2)

    @staticmethod
    def generate_scores(
        text: str,
        entities: List[MedicalEntity],
        summary: str,
        historical_entities: Optional[List[MedicalEntity]] = None,
        integration_text: Optional[str] = None,
    ) -> ConfidenceScores:
        """Generate all confidence scores."""
        if historical_entities is None:
            historical_entities = []
        if integration_text is None:
            integration_text = ""

        entity_score = ConfidenceScorer.score_entity_extraction(entities, len(text))
        summarization_score = ConfidenceScorer.score_summarization(summary, len(text))
        context_score = ConfidenceScorer.score_context_understanding(
            entities, historical_entities, integration_text
        )
        overall_score = ConfidenceScorer.calculate_overall_confidence(
            entity_score, summarization_score, context_score
        )

        return ConfidenceScores(
            entity_extraction=round(entity_score, 2),
            summarization=round(summarization_score, 2),
            context_understanding=round(context_score, 2),
            overall=round(overall_score, 2),
        )
