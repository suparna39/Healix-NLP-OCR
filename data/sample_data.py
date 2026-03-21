"""Sample data for testing and demonstration."""

from app.models.schemas import MedicalRecord, AnalysisRequest
from datetime import datetime, timedelta

# Sample OCR text from a medical document
SAMPLE_OCR_TEXT = """
PATIENT MEDICAL RECORD
Date: 2024-03-20
Patient ID: P12345

CHIEF COMPLAINT:
Patient presents with chest pain and shortness of breath for 3 days.

HISTORY OF PRESENT ILLNESS:
The patient is a 65-year-old male with history of hypertension and diabetes mellitus 
who reports experiencing chest pain radiating to the left arm. Associated symptoms 
include shortness of breath, nausea, and diaphoresis. Patient denies recent trauma or 
injury. Symptoms began 3 days ago and have been worsening.

PAST MEDICAL HISTORY:
- Hypertension (HTN) - diagnosed 10 years ago
- Type 2 Diabetes Mellitus (T2DM) - diagnosed 8 years ago
- Hyperlipidemia
- Coronary Artery Disease (CAD)

MEDICATIONS:
- Lisinopril 10mg daily (BP management)
- Metformin 1000mg twice daily (diabetes control)
- Atorvastatin 40mg daily (cholesterol)
- Aspirin 81mg daily (antiplatelet)

VITAL SIGNS:
- BP: 150/95 mmHg
- HR: 102 bpm
- RR: 22 breaths/min
- Temperature: 37.2°C
- SpO2: 94%

PHYSICAL EXAMINATION:
General: Patient appears anxious and in mild distress
CV: Tachycardia present, irregularities noted
Lungs: Clear to auscultation bilaterally
Abdomen: Soft, non-tender

LABORATORY RESULTS:
- Blood glucose: 280 mg/dL (elevated)
- HbA1c: 8.5% (suboptimal control)
- Troponin I: 0.08 ng/mL (elevated)
- BUN: 25 mg/dL (mildly elevated)
- Creatinine: 1.4 mg/dL

IMAGING:
- ECG: ST elevation in leads II, III, aVF
- Chest X-ray: No acute findings

ASSESSMENT:
Acute Myocardial Infarction (STEMI) - Inferior wall

PLAN:
1. Admit to ICU for cardiac monitoring
2. Continue aspirin and lisinopril
3. Consider cardiac catheterization
4. Monitor troponin levels
5. Manage hypertension and diabetes
6. Cardiology consultation
"""

# Sample previous medical record
SAMPLE_PREVIOUS_RECORD = MedicalRecord(
    record_id="PR001",
    date=datetime.now() - timedelta(days=180),
    document_type="annual_physical",
    raw_text="""
    ANNUAL PHYSICAL EXAMINATION
    
    Patient: 65-year-old male
    Date: 2023-09-20
    
    HISTORY:
    - Well-controlled hypertension on Lisinopril
    - Diabetes mellitus type 2 with glucose levels 150-180 mg/dL
    - No recent hospitalizations
    
    PHYSICAL EXAM:
    - Vital signs stable
    - Cardiovascular exam: regular rate and rhythm
    - Chest exam: clear bilaterally
    
    LABS:
    - HbA1c: 7.2%
    - BP control: adequate
    - Lipid panel: acceptable
    
    ASSESSMENT: Stable chronic disease management
    
    PLAN: Continue current medications, follow up in 6 months
    """,
    source="Primary Care Clinic"
)

# Sample analysis request
SAMPLE_ANALYSIS_REQUEST = AnalysisRequest(
    ocr_text=SAMPLE_OCR_TEXT,
    patient_id="P12345",
    age=65,
    sex="M",
    date=datetime.now(),
    source_type="emergency_department",
    known_conditions=["hypertension", "diabetes mellitus", "coronary artery disease"],
    previous_records=[SAMPLE_PREVIOUS_RECORD],
)

# Another sample with pneumonia
PNEUMONIA_OCR = """
CLINICAL NOTE
Date: 2024-03-21
Patient: Female, 42 years old

CHIEF COMPLAINT:
Cough and fever for 5 days

HISTORY:
Patient reports persistent cough, fever, and shortness of breath. 
No recent travel. No known COVID exposure.

VITAL SIGNS:
- Temperature: 38.8°C (elevated)
- HR: 98 bpm
- RR: 24 breaths/min (tachypnea)
- BP: 128/82 mmHg
- SpO2: 92% on room air

EXAM:
Lungs: Crackles in left lower lobe
CV: Regular rate and rhythm

IMAGING:
Chest X-ray: Infiltrate in left lower lobe consistent with pneumonia

LABS:
- WBC: 14.2 (elevated)
- CRP: 45 mg/L (elevated)

ASSESSMENT:
Community-acquired pneumonia

PLAN:
- Start Amoxicillin 500mg TID
- Supportive care
- Follow up X-ray in 2 weeks
"""

# Minimal example for testing
MINIMAL_OCR = """
Patient presents with fever and cough.
History of diabetes.
Taking metformin and aspirin.
"""

# Example with few/no medical entities
POOR_OCR_QUALITY = """
Lhww pqtmslt yert epj gsyk.
Hstiry pf jreabsts.
Tqmomf osjr.
"""


def get_sample_analysis_request() -> AnalysisRequest:
    """Get sample analysis request."""
    return SAMPLE_ANALYSIS_REQUEST


def get_minimal_request() -> AnalysisRequest:
    """Get minimal test request."""
    return AnalysisRequest(
        ocr_text=MINIMAL_OCR,
        patient_id="TEST001",
        age=None,
        sex=None,
        date=None,
        source_type=None,
        known_conditions=None,
        previous_records=None,
    )


def get_pneumonia_request() -> AnalysisRequest:
    """Get pneumonia test request."""
    return AnalysisRequest(
        ocr_text=PNEUMONIA_OCR,
        patient_id="P42",
        age=42,
        sex="F",
        date=None,
        source_type=None,
        known_conditions=None,
        previous_records=None,
    )
