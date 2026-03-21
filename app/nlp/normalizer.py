"""Medical term normalization and synonym resolution."""

import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from app.models.schemas import MedicalEntity

logger = logging.getLogger(__name__)


@dataclass
class NormalizationMapping:
    """Represents a normalized medical term with alternatives."""
    preferred: str
    aliases: List[str]
    category: str
    definition: Optional[str] = None


class MedicalTermNormalizer:
    """Normalize medical terms and resolve synonyms."""

    # Comprehensive medical term normalizations
    NORMALIZATIONS: Dict[str, NormalizationMapping] = {
        # Diseases
        "diabetes": NormalizationMapping(
            preferred="Diabetes Mellitus",
            aliases=["dm", "diabetes mellitus", "t1dm", "t2dm", "type 1 diabetes", "type 2 diabetes"],
            category="disease",
            definition="Metabolic disorder characterized by elevated blood glucose"
        ),
        "hypertension": NormalizationMapping(
            preferred="Hypertension",
            aliases=["high blood pressure", "htn", "elevated bp", "blood pressure elevation"],
            category="disease",
            definition="Persistently elevated arterial blood pressure"
        ),
        "myocardial infarction": NormalizationMapping(
            preferred="Myocardial Infarction",
            aliases=["mi", "heart attack", "acute mi", "ami"],
            category="disease",
            definition="Acute necrosis of myocardial tissue from coronary artery occlusion"
        ),
        "congestive heart failure": NormalizationMapping(
            preferred="Congestive Heart Failure",
            aliases=["chf", "heart failure", "systolic failure", "diastolic failure", "acute hf"],
            category="disease",
            definition="Heart inability to supply oxygen-rich blood to meet metabolic needs"
        ),
        "pneumonia": NormalizationMapping(
            preferred="Pneumonia",
            aliases=["bacterial pneumonia", "viral pneumonia", "community-acquired pneumonia", "cap"],
            category="disease",
            definition="Inflammation of lung alveoli with fluid accumulation"
        ),
        "chronic obstructive pulmonary disease": NormalizationMapping(
            preferred="Chronic Obstructive Pulmonary Disease",
            aliases=["copd", "emphysema", "chronic bronchitis"],
            category="disease",
            definition="Group of lung diseases blocking airflow and making breathing difficult"
        ),
        "asthma": NormalizationMapping(
            preferred="Asthma",
            aliases=["allergic asthma", "exercise-induced asthma", "occupational asthma"],
            category="disease",
            definition="Chronic inflammatory airway disease with bronchial hyperresponsiveness"
        ),
        "stroke": NormalizationMapping(
            preferred="Cerebrovascular Accident (Stroke)",
            aliases=["cva", "brain attack", "ischemic stroke", "hemorrhagic stroke", "acute stroke"],
            category="disease",
            definition="Sudden interruption of blood supply to the brain"
        ),
        "cancer": NormalizationMapping(
            preferred="Malignancy",
            aliases=["carcinoma", "tumor", "neoplasm", "malignant neoplasm"],
            category="disease",
            definition="Uncontrolled growth and spread of abnormal cells"
        ),
        "urinary tract infection": NormalizationMapping(
            preferred="Urinary Tract Infection",
            aliases=["uti", "cystitis", "pyelonephritis", "urosepsis"],
            category="disease",
            definition="Bacterial infection of any part of the urinary system"
        ),
        "hepatitis": NormalizationMapping(
            preferred="Hepatitis",
            aliases=["viral hepatitis", "hepatitis a", "hepatitis b", "hepatitis c", "alcoholic hepatitis"],
            category="disease",
            definition="Inflammation of the liver from viral or other etiologies"
        ),
        "kidney disease": NormalizationMapping(
            preferred="Chronic Kidney Disease",
            aliases=["ckd", "renal disease", "nephritis", "glomerulonephritis", "end-stage renal disease", "esrd"],
            category="disease",
            definition="Gradual loss of kidney function over time"
        ),
        "arthritis": NormalizationMapping(
            preferred="Arthritis",
            aliases=["rheumatoid arthritis", "osteoarthritis", "ra", "oa"],
            category="disease",
            definition="Inflammatory joint disease with pain and stiffness"
        ),
        "anxiety": NormalizationMapping(
            preferred="Anxiety Disorder",
            aliases=["generalized anxiety", "gad", "anxiety neurosis", "nervousness"],
            category="disease",
            definition="Mental disorder with persistent worry and tension"
        ),
        "depression": NormalizationMapping(
            preferred="Major Depressive Disorder",
            aliases=["major depression", "mdd", "depressive disorder", "clinical depression"],
            category="disease",
            definition="Persistent low mood affecting functioning and quality of life"
        ),

        # Symptoms
        "fever": NormalizationMapping(
            preferred="Fever",
            aliases=["elevated temperature", "high temperature", "pyrexia", "febrile"],
            category="symptom",
            definition="Body temperature above normal range (typically >38°C)"
        ),
        "cough": NormalizationMapping(
            preferred="Cough",
            aliases=["productive cough", "dry cough", "persistent cough"],
            category="symptom",
            definition="Forceful expulsion of air from lungs"
        ),
        "shortness of breath": NormalizationMapping(
            preferred="Dyspnea",
            aliases=["sob", "breathing difficulty", "breathlessness", "dyspnea on exertion", "doe"],
            category="symptom",
            definition="Uncomfortable sensation of difficult or labored breathing"
        ),
        "chest pain": NormalizationMapping(
            preferred="Chest Pain",
            aliases=["chest discomfort", "chest tightness", "angina", "anginal pain"],
            category="symptom",
            definition="Pain or discomfort in the anterior chest wall"
        ),
        "dizziness": NormalizationMapping(
            preferred="Dizziness",
            aliases=["vertigo", "lightheadedness", "syncope", "presyncope"],
            category="symptom",
            definition="Sensation of spinning or unsteadiness"
        ),
        "headache": NormalizationMapping(
            preferred="Headache",
            aliases=["migraine", "tension headache", "cluster headache", "cephalgia"],
            category="symptom",
            definition="Pain in the head or upper neck region"
        ),
        "nausea": NormalizationMapping(
            preferred="Nausea",
            aliases=["feeling of sickness", "queasiness", "sick feeling"],
            category="symptom",
            definition="Feeling of sickness without vomiting"
        ),
        "vomiting": NormalizationMapping(
            preferred="Vomiting",
            aliases=["emesis", "throwing up", "regurgitation"],
            category="symptom",
            definition="Forceful expulsion of stomach contents through mouth"
        ),
        "abdominal pain": NormalizationMapping(
            preferred="Abdominal Pain",
            aliases=["belly pain", "stomach pain", "abdominal discomfort"],
            category="symptom",
            definition="Pain localized to the abdomen"
        ),
        "fatigue": NormalizationMapping(
            preferred="Fatigue",
            aliases=["tiredness", "exhaustion", "weakness", "asthenia"],
            category="symptom",
            definition="Extreme tiredness and lack of energy"
        ),
        "swelling": NormalizationMapping(
            preferred="Edema",
            aliases=["puffiness", "inflammation", "enlargement"],
            category="symptom",
            definition="Abnormal accumulation of fluid in body tissues"
        ),

        # Medications
        "metformin": NormalizationMapping(
            preferred="Metformin",
            aliases=["glucophage", "metformin hcl"],
            category="medication",
            definition="First-line antidiabetic medication reducing hepatic glucose production"
        ),
        "insulin": NormalizationMapping(
            preferred="Insulin",
            aliases=["insulin injection", "insulin glargine", "insulin aspart", "regular insulin"],
            category="medication",
            definition="Hormone regulating blood glucose levels"
        ),
        "lisinopril": NormalizationMapping(
            preferred="Lisinopril",
            aliases=["zestril", "prinivil", "ace inhibitor"],
            category="medication",
            definition="ACE inhibitor for hypertension and heart failure"
        ),
        "atorvastatin": NormalizationMapping(
            preferred="Atorvastatin",
            aliases=["lipitor", "statin", "cholesterol medication"],
            category="medication",
            definition="Statin reducing cholesterol and cardiovascular risk"
        ),
        "aspirin": NormalizationMapping(
            preferred="Aspirin",
            aliases=["acetylsalicylic acid", "asa", "pain reliever"],
            category="medication",
            definition="NSAID with antiplatelet properties"
        ),
        "ibuprofen": NormalizationMapping(
            preferred="Ibuprofen",
            aliases=["advil", "motrin", "nsaid", "pain reliever"],
            category="medication",
            definition="NSAID for pain, inflammation, and fever"
        ),
        "amoxicillin": NormalizationMapping(
            preferred="Amoxicillin",
            aliases=["amoxil", "antibiotic", "penicillin"],
            category="medication",
            definition="Beta-lactam antibiotic for bacterial infections"
        ),
        "ciprofloxacin": NormalizationMapping(
            preferred="Ciprofloxacin",
            aliases=["cipro", "fluoroquinolone", "antibiotic"],
            category="medication",
            definition="Fluoroquinolone antibiotic for gram-negative infections"
        ),
        "levothyroxine": NormalizationMapping(
            preferred="Levothyroxine",
            aliases=["synthroid", "t4", "thyroid hormone"],
            category="medication",
            definition="Synthetic thyroid hormone replacement"
        ),

        # Tests
        "blood test": NormalizationMapping(
            preferred="Blood Test",
            aliases=["lab work", "laboratory test", "hematology"],
            category="test",
            definition="Sampling and analysis of blood for diagnostic purposes"
        ),
        "x-ray": NormalizationMapping(
            preferred="Radiography",
            aliases=["x-ray imaging", "roentgen", "chest x-ray", "cxr"],
            category="test",
            definition="Imaging using electromagnetic radiation"
        ),
        "mri": NormalizationMapping(
            preferred="Magnetic Resonance Imaging",
            aliases=["magnetic resonance", "nmr", "mri scan"],
            category="test",
            definition="Imaging using magnetic fields and radio waves"
        ),
        "ct scan": NormalizationMapping(
            preferred="Computed Tomography",
            aliases=["cat scan", "ct imaging", "tomography"],
            category="test",
            definition="Cross-sectional imaging using x-rays"
        ),
        "ultrasound": NormalizationMapping(
            preferred="Ultrasonography",
            aliases=["sonography", "ultrasonic imaging", "echo"],
            category="test",
            definition="Imaging using ultrasonic sound waves"
        ),
        "ecg": NormalizationMapping(
            preferred="Electrocardiogram",
            aliases=["ekg", "cardiac monitoring", "heart tracing"],
            category="test",
            definition="Electrical recording of heart activity"
        ),
        "echocardiogram": NormalizationMapping(
            preferred="Echocardiography",
            aliases=["echo", "cardiac ultrasound", "heart echo"],
            category="test",
            definition="Ultrasound imaging of the heart"
        ),

        # Procedures
        "surgery": NormalizationMapping(
            preferred="Surgery",
            aliases=["surgical procedure", "surgical operation", "operative procedure"],
            category="procedure",
            definition="Manual and instrumental treatment of disease"
        ),
        "biopsy": NormalizationMapping(
            preferred="Biopsy",
            aliases=["tissue biopsy", "needle biopsy", "excision biopsy"],
            category="procedure",
            definition="Removal and examination of tissue for diagnosis"
        ),
        "endoscopy": NormalizationMapping(
            preferred="Endoscopy",
            aliases=["internal examination", "scopy"],
            category="procedure",
            definition="Visual examination of internal organs"
        ),
        "colonoscopy": NormalizationMapping(
            preferred="Colonoscopy",
            aliases=["colon examination", "lower endoscopy"],
            category="procedure",
            definition="Examination of the colon with endoscope"
        ),
        "intubation": NormalizationMapping(
            preferred="Endotracheal Intubation",
            aliases=["intubated", "tube placement", "mechanical ventilation"],
            category="procedure",
            definition="Placement of tube in trachea for ventilation"
        ),
    }

    @staticmethod
    def normalize_term(term: str) -> Tuple[Optional[str], Optional[NormalizationMapping]]:
        """Normalize a medical term, returning preferred term and mapping."""
        term_lower = term.lower().strip()

        # Direct match
        if term_lower in MedicalTermNormalizer.NORMALIZATIONS:
            mapping = MedicalTermNormalizer.NORMALIZATIONS[term_lower]
            return mapping.preferred, mapping

        # Check aliases
        for preferred, mapping in MedicalTermNormalizer.NORMALIZATIONS.items():
            if term_lower in mapping.aliases:
                return mapping.preferred, mapping

        # Partial match (for flexibility)
        for preferred, mapping in MedicalTermNormalizer.NORMALIZATIONS.items():
            if term_lower in preferred.lower():
                return mapping.preferred, mapping
            for alias in mapping.aliases:
                if term_lower in alias.lower():
                    return mapping.preferred, mapping

        # No match found
        return None, None

    def normalize_entities(self, entities: List[MedicalEntity]) -> List[MedicalEntity]:
        """Normalize all entities in a list."""
        normalized = []

        for entity in entities:
            normalized_term, mapping = self.normalize_term(entity.text)

            if normalized_term:
                entity.normalized = normalized_term
                if mapping:
                    entity.synonyms = mapping.aliases
            else:
                # If no normalization found, use original
                entity.normalized = entity.text

            normalized.append(entity)

        return normalized

    def get_normalization_mapping(self) -> Dict[str, str]:
        """Get a dictionary of original -> normalized terms."""
        mapping = {}
        for original, norm_obj in self.NORMALIZATIONS.items():
            mapping[original] = norm_obj.preferred
            for alias in norm_obj.aliases:
                mapping[alias] = norm_obj.preferred
        return mapping

    @staticmethod
    def get_synonyms(normalized_term: str) -> List[str]:
        """Get all synonyms for a normalized term."""
        for term, mapping in MedicalTermNormalizer.NORMALIZATIONS.items():
            if mapping.preferred == normalized_term:
                return mapping.aliases
        return []

    @staticmethod
    def get_definition(normalized_term: str) -> Optional[str]:
        """Get definition of a normalized term."""
        for term, mapping in MedicalTermNormalizer.NORMALIZATIONS.items():
            if mapping.preferred == normalized_term:
                return mapping.definition
        return None
