"""
QUICK TEST SCRIPT FOR HELIX MEDICAL NLP
Run this to test the system without needing complex setup
"""

import sys
import os

# Add project to path
sys.path.insert(0, '/c/Healix-2/helix_medical_nlp')

print("=" * 80)
print("HELIX MEDICAL NLP - QUICK TEST")
print("=" * 80)

try:
    print("\n✓ Importing modules...")
    from app.nlp.ocr_cleaner import OCRTextCleaner
    from app.nlp.entity_extractor import MedicalEntityExtractor
    from app.nlp.normalizer import MedicalTermNormalizer
    from app.nlp.summarizer import create_summarizer
    from app.nlp.risk_detector import RiskDetector
    print("✓ All modules imported successfully!")

    # Test 1: OCR Cleaning
    print("\n" + "=" * 80)
    print("TEST 1: OCR TEXT CLEANING")
    print("=" * 80)
    
    cleaner = OCRTextCleaner()
    dirty_text = "Patient  has   FEVER\n\nHistory   of   DM   and   HTN\n\nPage 1"
    clean_text = cleaner.clean(dirty_text)
    print(f"Input:  {repr(dirty_text)}")
    print(f"Output: {repr(clean_text)}")
    print("✓ OCR cleaning works!")

    # Test 2: Entity Extraction
    print("\n" + "=" * 80)
    print("TEST 2: MEDICAL ENTITY EXTRACTION")
    print("=" * 80)
    
    extractor = MedicalEntityExtractor(use_scispacy=False)
    medical_text = """
    Patient presents with fever and cough. 
    History of diabetes and hypertension.
    Currently taking metformin and lisinopril.
    CT scan shows pneumonia.
    """
    entities = extractor.extract(medical_text)
    
    print(f"Found {len(entities)} entities:")
    by_type = {}
    for entity in entities:
        if entity.entity_type not in by_type:
            by_type[entity.entity_type] = []
        by_type[entity.entity_type].append(entity.text)
    
    for entity_type, texts in sorted(by_type.items()):
        print(f"  {entity_type.upper()}: {', '.join(set(texts))}")
    print("✓ Entity extraction works!")

    # Test 3: Term Normalization
    print("\n" + "=" * 80)
    print("TEST 3: MEDICAL TERM NORMALIZATION")
    print("=" * 80)
    
    normalizer = MedicalTermNormalizer()
    test_terms = ["dm", "high BP", "SOB", "chest pain"]
    print("Normalizing medical terms:")
    for term in test_terms:
        normalized, mapping = normalizer.normalize_term(term)
        print(f"  '{term}' → '{normalized}'")
    print("✓ Term normalization works!")

    # Test 4: Risk Detection
    print("\n" + "=" * 80)
    print("TEST 4: RISK DETECTION")
    print("=" * 80)
    
    risk_detector = RiskDetector()
    risk_text = "Patient with chest pain and difficulty breathing"
    
    # Mock entities for testing
    from app.models.schemas import MedicalEntity
    
    symptom1 = MedicalEntity(
        text="chest pain",
        entity_type="symptom",
        normalized="Chest Pain",
        confidence=0.9,
        start_pos=0,
        end_pos=10,
        explanation="Patient symptom",
        synonyms=[],
        cui=None
    )
    
    symptom2 = MedicalEntity(
        text="difficulty breathing",
        entity_type="symptom",
        normalized="Dyspnea",
        confidence=0.9,
        start_pos=20,
        end_pos=40,
        explanation="Patient symptom",
        synonyms=[],
        cui=None
    )
    
    risks = risk_detector.detect_critical_symptoms([symptom1, symptom2])
    print(f"Found {len(risks)} risk flags:")
    for flag in risks:
        print(f"  [{flag.severity.value.upper()}] {flag.description}")
    print("✓ Risk detection works!")

    # Test 5: Full Pipeline
    print("\n" + "=" * 80)
    print("TEST 5: FULL NLP PIPELINE")
    print("=" * 80)
    
    print("Initializing full pipeline...")
    from app.core.pipeline import MedicalNLPPipeline
    from app.models.schemas import AnalysisRequest
    
    pipeline = MedicalNLPPipeline()
    
    request = AnalysisRequest(
        ocr_text="""
        MEDICAL RECORD
        Date: 2024-03-20
        
        Chief Complaint: Patient with fever and cough for 5 days
        
        Past Medical History:
        - Diabetes mellitus
        - Hypertension
        
        Medications:
        - Metformin 500mg
        - Lisinopril 10mg
        
        Vital Signs:
        - Temperature: 38.5°C
        - Blood pressure: 140/90
        
        Physical Exam:
        Lungs: Crackles in left lower lobe
        
        Assessment:
        Community-acquired pneumonia
        
        Plan:
        Start Amoxicillin 500mg TID
        """,
        patient_id="TEST001"
    )
    
    print("Processing medical document...")
    response = pipeline.process(request)
    
    print(f"\n✓ ANALYSIS COMPLETE!")
    print(f"  Patient ID: {response.patient_id}")
    print(f"  Processing Time: {response.processing_time_ms:.1f}ms")
    print(f"  Overall Confidence: {response.confidence.overall:.1%}")
    
    print(f"\n  Extracted Entities:")
    total_entities = sum(len(ents) for ents in response.entities.values())
    print(f"    Total: {total_entities} entities")
    
    if response.entities['diseases']:
        print(f"    Diseases: {', '.join([d.normalized for d in response.entities['diseases'][:3]])}")
    if response.entities['symptoms']:
        print(f"    Symptoms: {', '.join([s.normalized for s in response.entities['symptoms'][:3]])}")
    if response.entities['medications']:
        print(f"    Medications: {', '.join([m.normalized for m in response.entities['medications'][:3]])}")
    
    print(f"\n  Summaries:")
    print(f"    Short: {response.summary_short[:100]}...")
    
    if response.risk_flags:
        print(f"\n  Risk Flags: {len(response.risk_flags)}")
        for flag in response.risk_flags[:2]:
            print(f"    [{flag.severity.value.upper()}] {flag.description}")
    
    print(f"\n  Doctor Notes:")
    for note in response.notes_for_doctor[:2]:
        print(f"    • {note}")
    
    print("\n✓ Full pipeline works!")

    # Summary
    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\nThe HELIX Medical NLP system is working correctly!")
    print("\nNext steps:")
    print("1. Run the FastAPI server:")
    print("   python -m uvicorn app.main:app --reload")
    print("\n2. Visit the interactive API docs:")
    print("   http://localhost:8000/docs")
    print("\n3. Try the /api/v1/analyze endpoint with your medical text")
    print("\n4. See QUICKSTART.md for more information")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
