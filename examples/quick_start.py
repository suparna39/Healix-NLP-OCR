"""Quick start examples for HELIX Medical NLP."""

import json
from datetime import datetime
from app.models.schemas import AnalysisRequest, MedicalRecord
from app.core.pipeline import MedicalNLPPipeline


def example_1_basic_analysis():
    """Example 1: Basic analysis of OCR text."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Basic Medical Text Analysis")
    print("="*80)

    ocr_text = """
    PATIENT VISIT NOTE
    Date: 2024-03-20
    
    Chief Complaint: Fever and cough
    
    History of Present Illness:
    Patient reports 5 days of fever, productive cough with green sputum, and shortness 
    of breath. No recent travel. Denies chest pain.
    
    Past Medical History:
    - Asthma
    - Type 2 Diabetes
    
    Medications:
    - Albuterol inhaler as needed
    - Metformin 500mg twice daily
    
    Vital Signs:
    - Temperature: 38.5°C
    - Heart Rate: 96 bpm
    - Respiratory Rate: 24
    - BP: 128/82
    
    Physical Exam:
    Lungs: Crackles in left lower lobe
    
    Assessment:
    Suspected community-acquired pneumonia
    
    Plan:
    Start Amoxicillin 500mg three times daily
    """

    request = AnalysisRequest(
        ocr_text=ocr_text,
        patient_id="EX001",
        age=45,
        sex="F",
        source_type="clinic",
        date=None,
        known_conditions=None,
        previous_records=None,
    )

    pipeline = MedicalNLPPipeline()
    response = pipeline.process(request)

    print(f"\nPatient ID: {response.patient_id}")
    print(f"\nExtracted Diseases: {[d.normalized for d in response.entities['diseases']]}")
    print(f"Extracted Symptoms: {[s.normalized for s in response.entities['symptoms']]}")
    print(f"Extracted Medications: {[m.normalized for m in response.entities['medications']]}")
    print(f"\nShort Summary:\n{response.summary_short}")
    print(f"\nRisk Flags: {len(response.risk_flags)}")
    for flag in response.risk_flags:
        print(f"  - {flag.severity.value.upper()}: {flag.description}")
    print(f"\nOverall Confidence: {response.confidence.overall}")
    print(f"Processing Time: {response.processing_time_ms:.2f}ms")


def example_2_with_history():
    """Example 2: Analysis with patient history."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Analysis with Patient History")
    print("="*80)

    current_ocr = """
    FOLLOW-UP VISIT
    Date: 2024-03-20
    
    Chief Complaint: Increased shortness of breath
    
    Patient reports worsening dyspnea over past week. Chest pain for 2 days.
    
    Vital Signs:
    - BP: 145/92
    - HR: 105
    - SpO2: 91%
    
    Assessment:
    Possible CHF exacerbation
    """

    previous_record = MedicalRecord(
        record_id="PREV001",
        date=datetime(2024, 2, 15),
        document_type="clinic_visit",
        raw_text="""
        ROUTINE VISIT
        Patient has known congestive heart failure.
        BP stable at 130/85.
        On Lisinopril and Furosemide.
        No acute complaints.
        """
    )

    request = AnalysisRequest(
        ocr_text=current_ocr,
        patient_id="EX002",
        age=72,
        sex="M",
        date=None,
        source_type="clinic",
        known_conditions=["congestive heart failure", "hypertension"],
        previous_records=[previous_record],
    )

    pipeline = MedicalNLPPipeline()
    response = pipeline.process(request)

    print(f"\nHistory Integration: {response.history_integration}")
    print(f"\nShort Summary:\n{response.summary_short}")
    print(f"\nNotes for Doctor:")
    for note in response.notes_for_doctor:
        print(f"  • {note}")


def example_3_risk_detection():
    """Example 3: Risk detection and alerts."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Risk Detection")
    print("="*80)

    critical_ocr = """
    EMERGENCY DEPARTMENT NOTE
    
    Chief Complaint: Chest pain and difficulty breathing
    
    History:
    65-year-old male with history of diabetes, hypertension, CAD.
    Sudden onset severe chest pain radiating to left arm.
    Associated with dyspnea, nausea, diaphoresis.
    
    Medications:
    - Aspirin 81mg daily
    - Lisinopril 10mg daily
    - Metformin 1000mg BID
    
    Vital Signs:
    - BP: 155/95
    - HR: 110
    - RR: 28
    - Temp: 37.1
    - SpO2: 93%
    
    Labs:
    - Troponin: 0.15 (elevated)
    - Glucose: 320 mg/dL
    
    ECG: ST elevation II, III, aVF
    """

    request = AnalysisRequest(
        ocr_text=critical_ocr,
        patient_id="CRITICAL001",
        age=65,
        sex="M",
        date=None,
        source_type="emergency",
        known_conditions=["diabetes", "hypertension", "coronary artery disease"],
        previous_records=None,
    )

    pipeline = MedicalNLPPipeline()
    response = pipeline.process(request)

    print(f"\nTotal Risk Flags: {len(response.risk_flags)}")
    print("\nRisk Flags by Severity:")
    for flag in response.risk_flags:
        print(f"\n  [{flag.severity.value.upper()}] {flag.description}")
        print(f"    Explanation: {flag.explanation}")
        print(f"    Recommended Action: {flag.recommended_action}")

    print(f"\nWarnings: {response.warnings}")
    print(f"Confidence: {response.confidence.overall}")


def example_4_entity_only():
    """Example 4: Entity extraction only."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Entity Extraction Only")
    print("="*80)

    pipeline = MedicalNLPPipeline()

    text = "Patient with diabetes taking metformin presents with fever and cough. CT scan shows pneumonia."
    cleaned = pipeline.text_cleaner.clean(text)
    entities_by_type = pipeline.extract_entities(cleaned)

    for entity_type, entities in entities_by_type.items():
        if entities:
            print(f"\n{entity_type.upper()}:")
            for entity in entities:
                print(f"  • {entity.text} → {entity.normalized} (confidence: {entity.confidence})")


if __name__ == "__main__":
    print("\n🏥 HELIX Medical NLP System - Examples")
    print("=========================================\n")

    try:
        example_1_basic_analysis()
        example_2_with_history()
        example_3_risk_detection()
        example_4_entity_only()

        print("\n" + "="*80)
        print("✅ All examples completed successfully!")
        print("="*80 + "\n")

    except Exception as e:
        print(f"\n❌ Error running examples: {e}")
        import traceback
        traceback.print_exc()
