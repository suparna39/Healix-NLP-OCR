"""Unit tests for the medical NLP system."""

import pytest
from datetime import datetime
from app.nlp.ocr_cleaner import OCRTextCleaner
from app.nlp.entity_extractor import MedicalEntityExtractor
from app.nlp.normalizer import MedicalTermNormalizer
from app.nlp.context_merger import ContextMerger
from app.models.schemas import MedicalRecord, AnalysisRequest


class TestOCRCleaner:
    """Test OCR text cleaning."""

    def test_remove_control_characters(self):
        """Test removal of control characters."""
        text = "Patient has fever\x00 and cough."
        cleaned = OCRTextCleaner.remove_control_characters(text)
        assert "\x00" not in cleaned
        assert "fever" in cleaned

    def test_normalize_whitespace(self):
        """Test whitespace normalization."""
        text = "Patient  has   fever.  Cough  present."
        cleaned = OCRTextCleaner.normalize_whitespace(text)
        assert "  " not in cleaned
        assert "Patient has fever." in cleaned

    def test_remove_duplicate_lines(self):
        """Test duplicate line removal."""
        text = "Fever present\nFever present\nCough noted"
        cleaned = OCRTextCleaner.remove_duplicates_lines(text)
        lines = cleaned.strip().split("\n")
        assert len(lines) == 2

    def test_normalize_abbreviations(self):
        """Test abbreviation normalization."""
        text = "Patient has DM and HTN"
        cleaned = OCRTextCleaner.normalize_abbreviations(text)
        assert "diabetes mellitus" in cleaned
        assert "hypertension" in cleaned

    def test_full_cleaning_pipeline(self):
        """Test complete cleaning pipeline."""
        text = "  Patient   has   FEVER\n\nHistory   of   DM   and   HTN"
        cleaner = OCRTextCleaner()
        cleaned = cleaner.clean(text)
        assert len(cleaned) > 0
        assert "  " not in cleaned
        assert "fever" in cleaned or "FEVER" in cleaned


class TestEntityExtractor:
    """Test entity extraction."""

    def test_extract_diseases(self):
        """Test disease extraction."""
        extractor = MedicalEntityExtractor(use_scispacy=False)
        text = "Patient has diabetes and hypertension"
        entities = extractor.extract(text)

        disease_texts = [e.text for e in entities if e.entity_type == "disease"]
        assert any("diabetes" in d.lower() for d in disease_texts)
        assert any("hypertension" in d.lower() for d in disease_texts)

    def test_extract_medications(self):
        """Test medication extraction."""
        extractor = MedicalEntityExtractor(use_scispacy=False)
        text = "Patient taking aspirin and metformin"
        entities = extractor.extract(text)

        med_texts = [e.text for e in entities if e.entity_type == "medication"]
        assert any("aspirin" in m.lower() for m in med_texts)
        assert any("metformin" in m.lower() for m in med_texts)

    def test_extract_symptoms(self):
        """Test symptom extraction."""
        extractor = MedicalEntityExtractor(use_scispacy=False)
        text = "Patient presents with fever and cough"
        entities = extractor.extract(text)

        symptom_texts = [e.text for e in entities if e.entity_type == "symptom"]
        assert any("fever" in s.lower() for s in symptom_texts)
        assert any("cough" in s.lower() for s in symptom_texts)

    def test_confidence_scores(self):
        """Test confidence scores are reasonable."""
        extractor = MedicalEntityExtractor(use_scispacy=False)
        text = "Diabetes and aspirin"
        entities = extractor.extract(text)

        for entity in entities:
            assert 0 <= entity.confidence <= 1


class TestNormalizer:
    """Test medical term normalization."""

    def test_normalize_diabetes(self):
        """Test diabetes normalization."""
        normalizer = MedicalTermNormalizer()
        normalized, mapping = normalizer.normalize_term("dm")
        assert normalized == "Diabetes Mellitus"
        assert mapping is not None

    def test_normalize_hypertension(self):
        """Test hypertension normalization."""
        normalizer = MedicalTermNormalizer()
        normalized, mapping = normalizer.normalize_term("high blood pressure")
        assert normalized == "Hypertension"

    def test_get_synonyms(self):
        """Test getting synonyms."""
        normalizer = MedicalTermNormalizer()
        synonyms = normalizer.get_synonyms("Diabetes Mellitus")
        assert len(synonyms) > 0
        assert "dm" in [s.lower() for s in synonyms]

    def test_get_definition(self):
        """Test getting definition."""
        normalizer = MedicalTermNormalizer()
        definition = normalizer.get_definition("Myocardial Infarction")
        assert definition is not None
        assert len(definition) > 0


class TestContextMerger:
    """Test context merging."""

    def test_chronological_sort(self):
        """Test chronological sorting."""
        records = [
            MedicalRecord(
                record_id="1",
                date=datetime(2024, 1, 10),
                document_type="visit",
                raw_text="Visit 1"
            ),
            MedicalRecord(
                record_id="2",
                date=datetime(2024, 1, 5),
                document_type="visit",
                raw_text="Visit 2"
            ),
        ]

        sorted_records = ContextMerger.chronological_sort(records)
        assert sorted_records[0].date > sorted_records[1].date

    def test_filter_by_time_window(self):
        """Test time window filtering."""
        old_date = datetime(2020, 1, 1)
        recent_date = datetime.now()

        records = [
            MedicalRecord(
                record_id="1",
                date=recent_date,
                document_type="visit",
                raw_text="Recent"
            ),
            MedicalRecord(
                record_id="2",
                date=old_date,
                document_type="visit",
                raw_text="Old"
            ),
        ]

        filtered = ContextMerger.filter_by_time_window(records, days=365)
        assert len(filtered) == 1
        assert filtered[0].record_id == "1"


# Integration tests can be added here
@pytest.mark.asyncio
async def test_full_pipeline():
    """Test full pipeline integration."""
    from app.core.pipeline import MedicalNLPPipeline
    from data.sample_data import get_minimal_request

    pipeline = MedicalNLPPipeline()
    request = get_minimal_request()

    response = pipeline.process(request)

    assert response.patient_id == "TEST001"
    assert len(response.summary_short) > 0
    assert len(response.summary_long) > 0
    assert 0 <= response.confidence.overall <= 1
