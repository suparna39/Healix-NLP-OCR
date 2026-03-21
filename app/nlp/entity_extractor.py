"""Biomedical entity extraction using scispaCy and custom rules."""

import re
import logging
from typing import List, Dict, Optional, Tuple, TYPE_CHECKING
from dataclasses import dataclass
from app.models.schemas import MedicalEntity

if TYPE_CHECKING:
    from spacy.tokens import Doc

logger = logging.getLogger(__name__)


@dataclass
class EntityMatch:
    """Represents a matched entity."""
    text: str
    entity_type: str
    start: int
    end: int
    confidence: float
    explanation: str = ""


class MedicalEntityExtractor:
    """Extract medical entities from text using scispaCy and custom rules."""

    # Entity type mappings
    ENTITY_TYPES = {
        "DISEASE": "disease",
        "SYMPTOM": "symptom",
        "MEDICATION": "medication",
        "PROCEDURE": "procedure",
        "TEST": "test",
        "MEASUREMENT": "measurement",
        "ANATOMY": "anatomy",
    }

    # Common disease patterns
    DISEASE_PATTERNS = [
        (r'\bdiabetes\b', 'disease'),
        (r'\bhypertension\b', 'disease'),
        (r'\barrythmia\b', 'disease'),
        (r'\bfibrillation\b', 'disease'),
        (r'\binfection\b', 'disease'),
        (r'\bpneumonia\b', 'disease'),
        (r'\btuberculosis\b', 'disease'),
        (r'\bcancer\b', 'disease'),
        (r'\bmalignancy\b', 'disease'),
        (r'\binfection\b', 'disease'),
        (r'\bstroke\b', 'disease'),
        (r'\bparalysis\b', 'disease'),
        (r'\bthyroid\b', 'disease'),
        (r'\bgastritis\b', 'disease'),
        (r'\bhepatitis\b', 'disease'),
        (r'\bnephritis\b', 'disease'),
        (r'\basthma\b', 'disease'),
        (r'\bcopd\b', 'disease'),
        (r'\bcongestive\s+heart\s+failure\b', 'disease'),
        (r'\bcoronary\s+artery\s+disease\b', 'disease'),
        (r'\barrhythmia\b', 'disease'),
        (r'\bepilepsy\b', 'disease'),
        (r'\bseizure\b', 'disease'),
        (r'\bdepression\b', 'disease'),
        (r'\banxiety\b', 'disease'),
        (r'\bdementia\b', 'disease'),
        (r'\balzheimer\b', 'disease'),
        (r'\bparkinson\b', 'disease'),
        (r'\baids\b', 'disease'),
        (r'\bhiv\b', 'disease'),
        (r'\brheumatoid\s+arthritis\b', 'disease'),
        (r'\blupus\b', 'disease'),
        (r'\bfibrosis\b', 'disease'),
        (r'\bkidney\s+disease\b', 'disease'),
        (r'\bchronic\s+kidney\s+disease\b', 'disease'),
        (r'\bdia betic\s+neuropathy\b', 'disease'),
    ]

    # Common symptom patterns
    SYMPTOM_PATTERNS = [
        (r'\bfever\b', 'symptom'),
        (r'\bcough\b', 'symptom'),
        (r'\bchest\s+pain\b', 'symptom'),
        (r'\bshortness\s+of\s+breath\b', 'symptom'),
        (r'\bdyspnea\b', 'symptom'),
        (r'\bdizziness\b', 'symptom'),
        (r'\bheadache\b', 'symptom'),
        (r'\bnausea\b', 'symptom'),
        (r'\bvomiting\b', 'symptom'),
        (r'\bdiarrhea\b', 'symptom'),
        (r'\bconstipation\b', 'symptom'),
        (r'\babdominal\s+pain\b', 'symptom'),
        (r'\bfatigue\b', 'symptom'),
        (r'\bweakness\b', 'symptom'),
        (r'\bpain\b', 'symptom'),
        (r'\bswelling\b', 'symptom'),
        (r'\bedema\b', 'symptom'),
        (r'\brash\b', 'symptom'),
        (r'\bitching\b', 'symptom'),
        (r'\bpruritus\b', 'symptom'),
        (r'\bchills\b', 'symptom'),
        (r'\bsweating\b', 'symptom'),
        (r'\bloss\s+of\s+appetite\b', 'symptom'),
        (r'\bweight\s+loss\b', 'symptom'),
        (r'\bweight\s+gain\b', 'symptom'),
        (r'\binsomnia\b', 'symptom'),
        (r'\bsleeplessness\b', 'symptom'),
        (r'\bdisorientation\b', 'symptom'),
        (r'\bconfusion\b', 'symptom'),
        (r'\bmemory\s+loss\b', 'symptom'),
    ]

    # Common medication patterns
    MEDICATION_PATTERNS = [
        (r'\bmetformin\b', 'medication'),
        (r'\binsulin\b', 'medication'),
        (r'\baspirin\b', 'medication'),
        (r'\bibuprofen\b', 'medication'),
        (r'\bparacetamol\b', 'medication'),
        (r'\bacetaminophen\b', 'medication'),
        (r'\blisinopril\b', 'medication'),
        (r'\benalapril\b', 'medication'),
        (r'\bamlodipine\b', 'medication'),
        (r'\batenolol\b', 'medication'),
        (r'\bmetoprolol\b', 'medication'),
        (r'\bfurosemide\b', 'medication'),
        (r'\bhydrochlorothiazide\b', 'medication'),
        (r'\batorvastatin\b', 'medication'),
        (r'\bsimvastatin\b', 'medication'),
        (r'\blevothyroxine\b', 'medication'),
        (r'\bsertraline\b', 'medication'),
        (r'\bfluoxetine\b', 'medication'),
        (r'\bamoxicillin\b', 'medication'),
        (r'\bciprofloxacin\b', 'medication'),
        (r'\bazithromycin\b', 'medication'),
        (r'\bmetronidazole\b', 'medication'),
        (r'\bvitamin\s+[A-E]\b', 'medication'),
        (r'\bvitamin\b', 'medication'),
        (r'\boncolytics\b', 'medication'),
        (r'\bchemotherapy\b', 'medication'),
        (r'\bprednisolone\b', 'medication'),
        (r'\bprednisone\b', 'medication'),
        (r'\bdexamethasone\b', 'medication'),
        (r'\bhydrocortisone\b', 'medication'),
    ]

    # Common procedure patterns
    PROCEDURE_PATTERNS = [
        (r'\bsurgery\b', 'procedure'),
        (r'\bsurgical\b', 'procedure'),
        (r'\boperation\b', 'procedure'),
        (r'\bbiopsies\b', 'procedure'),
        (r'\bbiopsy\b', 'procedure'),
        (r'\bendoscopy\b', 'procedure'),
        (r'\bcolonoscopy\b', 'procedure'),
        (r'\blaparoscopy\b', 'procedure'),
        (r'\bsurgical\s+resection\b', 'procedure'),
        (r'\btransplant\b', 'procedure'),
        (r'\bintubation\b', 'procedure'),
        (r'\bextubation\b', 'procedure'),
        (r'\bcatheterization\b', 'procedure'),
        (r'\bcatheter\b', 'procedure'),
        (r'\bablation\b', 'procedure'),
        (r'\bstent\b', 'procedure'),
        (r'\bangioplasty\b', 'procedure'),
        (r'\bbypass\b', 'procedure'),
        (r'\btransfusion\b', 'procedure'),
        (r'\tdialysis\b', 'procedure'),
        (r'\bventilation\b', 'procedure'),
        (r'\bintubated\b', 'procedure'),
    ]

    # Common test patterns
    TEST_PATTERNS = [
        (r'\bblood\s+test\b', 'test'),
        (r'\blaboratory\b', 'test'),
        (r'\blab\b', 'test'),
        (r'\bx-ray\b', 'test'),
        (r'\bradiography\b', 'test'),
        (r'\bct\s+scan\b', 'test'),
        (r'\bmri\b', 'test'),
        (r'\bumsonography\b', 'test'),
        (r'\bultrasound\b', 'test'),
        (r'\becg\b', 'test'),
        (r'\bekg\b', 'test'),
        (r'\bechocardiogram\b', 'test'),
        (r'\becho\b', 'test'),
        (r'\beeg\b', 'test'),
        (r'\bpet\s+scan\b', 'test'),
        (r'\bspect\b', 'test'),
        (r'\blumbar\s+puncture\b', 'test'),
        (r'\bcsf\b', 'test'),
        (r'\bblood\s+pressure\b', 'test'),
        (r'\bglucose\s+test\b', 'test'),
        (r'\burine\s+test\b', 'test'),
        (r'\bculture\b', 'test'),
        (r'\bpathology\b', 'test'),
        (r'\bhistology\b', 'test'),
        (r'\bgenetic\s+test\b', 'test'),
        (r'\bscreen\b', 'test'),
        (r'\bcomplete\s+blood\s+count\b', 'test'),
        (r'\bliver\s+function\b', 'test'),
        (r'\brenal\s+function\b', 'test'),
    ]

    # Measurement patterns (values with units)
    MEASUREMENT_PATTERNS = [
        (r'\d+\s*(mg|g|kg|ml|l|mm|cm|m|inch|feet|ft)\b', 'measurement'),
        (r'\d+\s*(\bkg/m²\b|\bbmi\b)\b', 'measurement'),
        (r'\d+\s*(%)\b', 'measurement'),
        (r'\d+\s*(\bmmhg\b|\btorr\b)\b', 'measurement'),
        (r'\d+\s*(\bbpm\b|\b/min\b)\b', 'measurement'),
        (r'\d+\s*(\bcelsius\b|°c|°f|fahrenheit)\b', 'measurement'),
    ]

    def __init__(self, use_scispacy: bool = True):
        """Initialize the entity extractor."""
        self.use_scispacy = use_scispacy
        self.nlp = None
        self.abbreviations = {}

        if use_scispacy:
            try:
                # Try to load scispaCy model
                import spacy
                self.nlp = spacy.load("en_core_sci_md")
                logger.info("Loaded scispaCy model: en_core_sci_md")
            except OSError:
                logger.warning(
                    "scispaCy model not found. "
                    "Install with: python -m spacy download en_core_sci_md"
                )
                self.use_scispacy = False
            except ImportError:
                logger.warning("spacy package not installed, using pattern-based extraction")
                self.use_scispacy = False

    def extract_from_spacy(self, text: str, doc: "Doc") -> List[EntityMatch]:
        """Extract entities from spaCy document."""
        entities = []

        # Extract named entities from spaCy
        for ent in doc.ents:
            entity_type = self._map_spacy_label(ent.label_)
            if entity_type:
                match = EntityMatch(
                    text=ent.text,
                    entity_type=entity_type,
                    start=ent.start_char,
                    end=ent.end_char,
                    confidence=0.85,  # scispaCy confidence
                    explanation=f"Extracted by scispaCy as {ent.label_}"
                )
                entities.append(match)

        return entities

    @staticmethod
    def _map_spacy_label(label: str) -> Optional[str]:
        """Map spaCy label to our entity types."""
        mapping = {
            "DISEASE": "disease",
            "SYMPTOM": "symptom",
            "MEDICATION": "medication",
            "PROCEDURE": "procedure",
            "TEST": "test",
            "ANATOMY": "anatomy",
        }
        return mapping.get(label)

    @staticmethod
    def extract_pattern_matches(text: str, patterns: List[Tuple[str, str]]) -> List[EntityMatch]:
        """Extract entities using regex patterns."""
        entities = []

        for pattern, entity_type in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entity = EntityMatch(
                    text=match.group(0),
                    entity_type=entity_type,
                    start=match.start(),
                    end=match.end(),
                    confidence=0.75,
                    explanation=f"Matched by {entity_type} pattern"
                )
                entities.append(entity)

        return entities

    @staticmethod
    def deduplicate_entities(entities: List[EntityMatch]) -> List[EntityMatch]:
        """Remove overlapping entities, keeping higher confidence ones."""
        if not entities:
            return []

        # Sort by confidence descending, then by position
        sorted_entities = sorted(
            entities,
            key=lambda e: (-e.confidence, e.start)
        )

        unique = []
        for entity in sorted_entities:
            # Check if this entity overlaps with any already added
            overlaps = False
            for existing in unique:
                if not (entity.end <= existing.start or entity.start >= existing.end):
                    overlaps = True
                    break

            if not overlaps:
                unique.append(entity)

        # Sort back by position
        unique.sort(key=lambda e: e.start)
        return unique

    def extract(self, text: str) -> List[MedicalEntity]:
        """Extract all medical entities from text."""
        all_matches: List[EntityMatch] = []

        # 1. Use scispaCy if available
        if self.use_scispacy and self.nlp:
            try:
                doc = self.nlp(text)
                spacy_matches = self.extract_from_spacy(text, doc)
                all_matches.extend(spacy_matches)
            except Exception as e:
                logger.warning(f"Error during scispaCy extraction: {e}")

        # 2. Use pattern-based extraction
        all_matches.extend(self.extract_pattern_matches(text, self.DISEASE_PATTERNS))
        all_matches.extend(self.extract_pattern_matches(text, self.SYMPTOM_PATTERNS))
        all_matches.extend(self.extract_pattern_matches(text, self.MEDICATION_PATTERNS))
        all_matches.extend(self.extract_pattern_matches(text, self.PROCEDURE_PATTERNS))
        all_matches.extend(self.extract_pattern_matches(text, self.TEST_PATTERNS))
        all_matches.extend(self.extract_pattern_matches(text, self.MEASUREMENT_PATTERNS))

        # 3. Deduplicate
        unique_matches = self.deduplicate_entities(all_matches)

        # 4. Convert to MedicalEntity objects
        medical_entities = []
        for match in unique_matches:
            entity = MedicalEntity(
                text=match.text,
                entity_type=match.entity_type,
                normalized=None,  # Will be filled by normalization step
                confidence=match.confidence,
                start_pos=match.start,
                end_pos=match.end,
                explanation=match.explanation,
                synonyms=[],
                cui=None,
            )
            medical_entities.append(entity)

        logger.info(f"Extracted {len(medical_entities)} medical entities")
        return medical_entities
