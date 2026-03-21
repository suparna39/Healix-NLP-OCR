"""Context and history merging for patient records."""

import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from app.models.schemas import MedicalRecord, MedicalEntity

logger = logging.getLogger(__name__)


class ContextMerger:
    """Merge current medical findings with patient history."""

    def __init__(self):
        """Initialize the context merger."""
        self.current_entities: List[MedicalEntity] = []
        self.history_entities: List[MedicalEntity] = []
        self.merged_context: str = ""

    def load_patient_history(
        self, patient_id: str, max_records: int = 5
    ) -> List[MedicalRecord]:
        """Load previous medical records for a patient."""
        # In a real system, this would query a database
        # For now, return empty list (records passed in request)
        logger.debug(f"Attempting to load history for patient {patient_id}")
        return []

    @staticmethod
    def deduplicate_entities(
        current: List[MedicalEntity], history: List[MedicalEntity]
    ) -> Tuple[List[MedicalEntity], List[MedicalEntity]]:
        """Remove duplicate entities between current and history."""
        current_normalized = {e.normalized or e.text.lower(): e for e in current}
        history_normalized = {e.normalized or e.text.lower(): e for e in history}

        # Keep current entities, remove duplicates from history
        unique_history = [
            e for key, e in history_normalized.items()
            if key not in current_normalized
        ]

        return list(current_normalized.values()), unique_history

    @staticmethod
    def chronological_sort(records: List[MedicalRecord]) -> List[MedicalRecord]:
        """Sort records chronologically (newest first)."""
        return sorted(records, key=lambda r: r.date, reverse=True)

    @staticmethod
    def filter_by_time_window(
        records: List[MedicalRecord], days: int = 365
    ) -> List[MedicalRecord]:
        """Filter records within time window."""
        cutoff = datetime.now() - timedelta(days=days)
        return [r for r in records if r.date >= cutoff]

    @staticmethod
    def resolve_contradictions(
        current_value: str, historical_value: str, entity_type: str
    ) -> Tuple[str, bool]:
        """Resolve contradictions between current and historical values."""
        # Simple contradiction detection
        if current_value.lower() == historical_value.lower():
            return current_value, False  # No contradiction

        # For specific entity types, apply rules
        if entity_type == "medication":
            # If medication changed, both are valid
            return f"{current_value} (previously: {historical_value})", False

        if entity_type == "test":
            # Flag contradictory test results
            return current_value, True

        if entity_type == "disease":
            # Flag if disease status changed unexpectedly
            return current_value, True

        return current_value, False

    def merge_with_history(
        self,
        current_text: str,
        current_entities: List[MedicalEntity],
        previous_records: Optional[List[MedicalRecord]] = None,
    ) -> Tuple[str, List[MedicalEntity], str]:
        """
        Merge current findings with patient history.

        Returns:
            - merged_text: Combined context for summarization
            - merged_entities: Deduplicated entity list
            - integration_summary: Text summary of how current relates to history
        """
        if not previous_records:
            previous_records = []

        logger.info(f"Merging current findings with {len(previous_records)} historical records")

        # Sort by date
        sorted_records = self.chronological_sort(previous_records)

        # Build merged text
        merged_text_parts = ["CURRENT VISIT:\n" + current_text]

        # Extract entities from history
        history_entities: List[MedicalEntity] = []
        for record in sorted_records:
            merged_text_parts.append(
                f"\n\n[Previous: {record.date.strftime('%Y-%m-%d')} - {record.document_type}]\n{record.raw_text}"
            )

        merged_text = "\n".join(merged_text_parts)

        # Deduplicate entities
        merged_current, unique_history = self.deduplicate_entities(
            current_entities, history_entities
        )

        # Build integration summary
        integration_summary = self._build_integration_summary(
            current_entities,
            unique_history,
            previous_records,
            sorted_records
        )

        return merged_text, merged_current + unique_history, integration_summary

    @staticmethod
    def _build_integration_summary(
        current: List[MedicalEntity],
        history: List[MedicalEntity],
        all_previous: List[MedicalRecord],
        sorted_previous: List[MedicalRecord],
    ) -> str:
        """Build a narrative summary of how current findings relate to history."""
        parts = []

        # Count previous records
        if sorted_previous:
            parts.append(
                f"Patient has {len(all_previous)} previous records with most recent from "
                f"{sorted_previous[0].date.strftime('%Y-%m-%d')}."
            )

        # Identify new conditions
        current_normalized = {(e.normalized or e.text).lower() for e in current}
        history_normalized = {(e.normalized or e.text).lower() for e in history}
        new_conditions = current_normalized - history_normalized

        if new_conditions:
            parts.append(f"New findings: {', '.join(list(new_conditions)[:3])}.")

        # Identify ongoing conditions
        ongoing = current_normalized & history_normalized
        if ongoing:
            parts.append(f"Ongoing: {', '.join(list(ongoing)[:3])}.")

        if not parts:
            parts.append("Current findings consistent with patient history.")

        return " ".join(parts)

    @staticmethod
    def get_timeline(records: List[MedicalRecord]) -> str:
        """Generate a timeline of patient history."""
        if not records:
            return "No previous records."

        timeline_parts = []
        for record in ContextMerger.chronological_sort(records):
            timeline_parts.append(
                f"• {record.date.strftime('%Y-%m-%d')}: {record.document_type}"
            )

        return "Patient History Timeline:\n" + "\n".join(timeline_parts)

    @staticmethod
    def identify_trends(records: List[MedicalRecord]) -> List[str]:
        """Identify trends in patient records."""
        trends = []

        if len(records) < 2:
            return trends

        # Sort chronologically
        sorted_records = ContextMerger.chronological_sort(records)
        sorted_records.reverse()  # Oldest first

        # Simple trend detection
        disease_mentions = {}
        medication_mentions = {}

        for record in sorted_records:
            # Count disease mentions
            if "diabetes" in record.raw_text.lower():
                disease_mentions["diabetes"] = disease_mentions.get("diabetes", 0) + 1
            if "hypertension" in record.raw_text.lower():
                disease_mentions["hypertension"] = disease_mentions.get("hypertension", 0) + 1

        # Report trends
        for disease, count in disease_mentions.items():
            if count >= 2:
                trends.append(f"Chronic {disease} documented in {count} previous records.")

        return trends
