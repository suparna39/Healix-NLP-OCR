"""OCR text cleaning and preprocessing module."""

import re
import logging
from typing import List, Tuple
import unicodedata

logger = logging.getLogger(__name__)


class OCRTextCleaner:
    """Clean and preprocess OCR output."""

    # Common OCR errors and corrections
    COMMON_OCR_FIXES = {
        r'\b0\b': 'O',  # Common: 0 should be O in context
        r'\bl\b': '1',  # Common: l should be 1 in numbers
        r'\bO\b': '0',  # Context-dependent, handled carefully
    }

    # Medical abbreviations that should be preserved
    MEDICAL_ABBREVIATIONS = {
        'BP': 'blood pressure',
        'HR': 'heart rate',
        'RR': 'respiratory rate',
        'O2': 'oxygen saturation',
        'SpO2': 'oxygen saturation',
        'FiO2': 'fraction of inspired oxygen',
        'HbA1c': 'hemoglobin A1c',
        'BUN': 'blood urea nitrogen',
        'CBC': 'complete blood count',
        'CMP': 'comprehensive metabolic panel',
        'PT': 'prothrombin time',
        'PTT': 'partial thromboplastin time',
        'INR': 'international normalized ratio',
        'TSH': 'thyroid stimulating hormone',
        'T4': 'thyroxine',
        'LFT': 'liver function test',
        'AST': 'aspartate aminotransferase',
        'ALT': 'alanine aminotransferase',
        'ESR': 'erythrocyte sedimentation rate',
        'CRP': 'c-reactive protein',
        'WBC': 'white blood cell',
        'RBC': 'red blood cell',
        'Hgb': 'hemoglobin',
        'Hct': 'hematocrit',
        'PLT': 'platelet',
        'Na': 'sodium',
        'K': 'potassium',
        'Cl': 'chloride',
        'CO2': 'carbon dioxide',
        'Cr': 'creatinine',
        'DM': 'diabetes mellitus',
        'HTN': 'hypertension',
        'CAD': 'coronary artery disease',
        'CHF': 'congestive heart failure',
        'COPD': 'chronic obstructive pulmonary disease',
        'SOB': 'shortness of breath',
        'DOE': 'dyspnea on exertion',
        'PND': 'paroxysmal nocturnal dyspnea',
        'URI': 'upper respiratory infection',
        'UTI': 'urinary tract infection',
        'MI': 'myocardial infarction',
        'CVA': 'cerebrovascular accident',
        'PE': 'pulmonary embolism',
        'DVT': 'deep vein thrombosis',
        'GERD': 'gastroesophageal reflux disease',
        'PUD': 'peptic ulcer disease',
        'CKD': 'chronic kidney disease',
        'ESRD': 'end-stage renal disease',
        'ARDS': 'acute respiratory distress syndrome',
        'ICU': 'intensive care unit',
        'ER': 'emergency room',
        'OR': 'operating room',
        'ICL': 'intracluster linkage',
        'IV': 'intravenous',
        'IM': 'intramuscular',
        'PO': 'by mouth',
        'PRN': 'as needed',
        'BID': 'twice daily',
        'TID': 'three times daily',
        'QID': 'four times daily',
        'QHS': 'at bedtime',
        'QAM': 'every morning',
        'QPM': 'every evening',
        'QD': 'once daily',
        'QOD': 'every other day',
        'q4h': 'every 4 hours',
        'q6h': 'every 6 hours',
        'q8h': 'every 8 hours',
        'q12h': 'every 12 hours',
        's/p': 'status post',
        'c/o': 'complains of',
        'h/o': 'history of',
        'sx': 'symptoms',
        'tx': 'treatment',
        'dx': 'diagnosis',
        'fx': 'fracture',
        'Hx': 'history',
        'PMHx': 'past medical history',
        'PSHx': 'past surgical history',
        'ROS': 'review of systems',
        'HPI': 'history of present illness',
        'A&O': 'alert and oriented',
        'AAO': 'alert and oriented',
        'LOC': 'level of consciousness',
        'N&V': 'nausea and vomiting',
        'Abd': 'abdomen',
        'EXT': 'extremities',
        'HEENT': 'head, eyes, ears, nose, throat',
        'PERRL': 'pupils equal, round, reactive to light',
        'PERRLA': 'pupils equal, round, reactive to light and accommodation',
        'CN': 'cranial nerve',
    }

    # Common medical terms variations
    MEDICAL_SYNONYMS = {
        'glucose': ['blood glucose', 'blood sugar', 'plasma glucose'],
        'blood pressure': ['BP', 'systolic', 'diastolic'],
        'heart rate': ['HR', 'pulse', 'cardiac rate'],
        'temperature': ['temp', 'fever', 'temperature reading'],
        'chest pain': ['chest discomfort', 'chest tightness', 'angina'],
        'shortness of breath': ['SOB', 'dyspnea', 'breathlessness'],
        'diabetes': ['diabetes mellitus', 'DM', 'diabetes type 2', 'type 1 diabetes'],
    }

    @staticmethod
    def remove_control_characters(text: str) -> str:
        """Remove control characters and invalid Unicode."""
        return "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in "\n\t\r")

    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """Normalize whitespace: collapse multiple spaces, fix line breaks."""
        # Remove multiple spaces
        text = re.sub(r' +', ' ', text)
        # Remove space before punctuation
        text = re.sub(r' ([.,;:])', r'\1', text)
        # Normalize line breaks (keep single line breaks)
        text = re.sub(r'\n\s*\n+', '\n\n', text)
        text = re.sub(r'[ \t]+\n', '\n', text)
        return text.strip()

    @staticmethod
    def remove_duplicates_lines(text: str) -> str:
        """Remove duplicate consecutive lines."""
        lines = text.split('\n')
        unique_lines = []
        prev_line = ""
        for line in lines:
            stripped = line.strip()
            if stripped and stripped != prev_line:
                unique_lines.append(line)
                prev_line = stripped
        return '\n'.join(unique_lines)

    @staticmethod
    def remove_headers_footers(text: str) -> str:
        """Remove common headers, footers, and page numbers."""
        # Remove page numbers
        text = re.sub(r'[-–—]?\s*Page\s+\d+\s*[-–—]?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)
        # Remove common headers
        text = re.sub(r'^CONFIDENTIAL.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        text = re.sub(r'^.*MEDICAL RECORD.*$', '', text, flags=re.MULTILINE | re.IGNORECASE)
        # Remove date/time stamps (but preserve medical dates)
        text = re.sub(
            r'^(Printed|Generated|Created|Scanned).*$',
            '',
            text,
            flags=re.MULTILINE | re.IGNORECASE
        )
        return text

    @staticmethod
    def normalize_abbreviations(text: str) -> str:
        """Normalize common medical abbreviations."""
        # Create a pattern for whole-word matches
        for abbrev, expansion in OCRTextCleaner.MEDICAL_ABBREVIATIONS.items():
            # Word boundary aware replacement
            pattern = r'\b' + re.escape(abbrev) + r'\b'
            # Keep original and add normalized in parentheses for context
            text = re.sub(pattern, f"{abbrev} ({expansion})", text, flags=re.IGNORECASE)
        return text

    @staticmethod
    def extract_numbers_and_values(text: str) -> List[Tuple[str, float]]:
        """Extract numerical values that might be lab results."""
        # Pattern: number with optional decimal and optional unit
        pattern = r'(\d+\.?\d*)\s*([a-zA-Z/%]*)'
        matches = re.finditer(pattern, text)
        values = []
        for match in matches:
            try:
                num = float(match.group(1))
                unit = match.group(2).strip()
                values.append((f"{num} {unit}".strip(), num))
            except ValueError:
                continue
        return values

    def clean(self, text: str) -> str:
        """Full cleaning pipeline."""
        if not text:
            return ""

        logger.debug("Starting OCR text cleaning pipeline")

        # Step 1: Remove control characters
        text = self.remove_control_characters(text)
        logger.debug("Removed control characters")

        # Step 2: Normalize whitespace
        text = self.normalize_whitespace(text)
        logger.debug("Normalized whitespace")

        # Step 3: Remove duplicate lines
        text = self.remove_duplicates_lines(text)
        logger.debug("Removed duplicate lines")

        # Step 4: Remove headers/footers
        text = self.remove_headers_footers(text)
        logger.debug("Removed headers and footers")

        # Step 5: Normalize abbreviations (add expansions)
        text = self.normalize_abbreviations(text)
        logger.debug("Normalized abbreviations")

        logger.debug("Cleaning pipeline completed")
        return text
