# OCR Integration Guide

This document explains how to connect OCR systems to HELIX Medical NLP.

## Overview

HELIX Medical NLP accepts OCR output from any source via its simple API. The system is designed to work with:

- Tesseract (open-source)
- AWS Textract
- Google Cloud Vision
- Azure Computer Vision
- Paddle OCR
- Any custom OCR system

## Integration Pattern

### Option 1: Direct API Call (Recommended for most use cases)

```python
import requests
import json
from your_ocr_system import extract_text_from_image

def analyze_medical_document(image_path, patient_id):
    """Extract text from image and analyze with HELIX."""
    
    # Step 1: Extract OCR text from image
    ocr_text = extract_text_from_image(image_path)
    
    # Step 2: Prepare analysis request
    payload = {
        "ocr_text": ocr_text,
        "patient_id": patient_id,
        "age": 65,  # Optional: add demographics
        "sex": "M",
        "source_type": "medical_record"
    }
    
    # Step 3: Call HELIX API
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json=payload
    )
    
    # Step 4: Process response
    if response.status_code == 200:
        analysis = response.json()
        return analysis
    else:
        print(f"Error: {response.status_code}")
        return None

# Usage
result = analyze_medical_document("scan.jpg", "P12345")
print(f"Diseases found: {[d['normalized'] for d in result['entities']['diseases']]}")
print(f"Summary: {result['summary_short']}")
```

### Option 2: Library Integration (For Python applications)

```python
from app.core.pipeline import MedicalNLPPipeline
from app.models.schemas import AnalysisRequest
from your_ocr_system import extract_text_from_image

def analyze_with_library(image_path, patient_id):
    """Analyze medical document using HELIX library directly."""
    
    # Extract OCR text
    ocr_text = extract_text_from_image(image_path)
    
    # Create pipeline
    pipeline = MedicalNLPPipeline()
    
    # Prepare request
    request = AnalysisRequest(
        ocr_text=ocr_text,
        patient_id=patient_id,
        age=65,
        sex="M"
    )
    
    # Process
    response = pipeline.process(request)
    
    # Use response
    return response

result = analyze_with_library("scan.jpg", "P12345")
```

### Option 3: Batch Processing

```python
import json
from pathlib import Path
from your_ocr_system import extract_text_from_image
from app.core.pipeline import MedicalNLPPipeline
from app.models.schemas import AnalysisRequest

def batch_analyze(image_folder, patient_mapping):
    """Process multiple medical documents."""
    
    pipeline = MedicalNLPPipeline()
    results = []
    
    for image_file in Path(image_folder).glob("*.jpg"):
        patient_id = patient_mapping.get(image_file.name)
        if not patient_id:
            continue
        
        # Extract OCR
        ocr_text = extract_text_from_image(str(image_file))
        
        # Analyze
        request = AnalysisRequest(ocr_text=ocr_text, patient_id=patient_id)
        response = pipeline.process(request)
        
        results.append({
            "file": image_file.name,
            "patient_id": patient_id,
            "analysis": response.dict()
        })
    
    # Save results
    with open("batch_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    return results

# Usage
patient_map = {
    "patient1_scan.jpg": "P001",
    "patient2_scan.jpg": "P002",
}
batch_analyze("./scans", patient_map)
```

## Connecting Specific OCR Systems

### Tesseract (Open Source)

```bash
# Install Tesseract
pip install pytesseract
apt-get install tesseract-ocr  # Linux
brew install tesseract          # macOS
```

```python
import pytesseract
from PIL import Image

def extract_with_tesseract(image_path):
    """Extract text using Tesseract."""
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    return text

# Use with HELIX
ocr_text = extract_with_tesseract("medical_scan.jpg")
response = analyze_medical_document(ocr_text, "P12345")
```

### AWS Textract

```bash
pip install boto3
```

```python
import boto3
import json

def extract_with_aws_textract(image_path):
    """Extract text using AWS Textract."""
    client = boto3.client('textract', region_name='us-east-1')
    
    with open(image_path, 'rb') as document:
        response = client.detect_document_text(Document={'Bytes': document.read()})
    
    text = ""
    for item in response['Blocks']:
        if item['BlockType'] == 'LINE':
            text += item['Text'] + "\n"
    
    return text

# Use with HELIX
ocr_text = extract_with_aws_textract("medical_scan.jpg")
response = analyze_medical_document(ocr_text, "P12345")
```

### Google Cloud Vision

```bash
pip install google-cloud-vision
```

```python
from google.cloud import vision

def extract_with_google_vision(image_path):
    """Extract text using Google Cloud Vision."""
    client = vision.ImageAnnotatorClient()
    
    with open(image_path, 'rb') as image_file:
        content = image_file.read()
    
    image = vision.Image(content=content)
    response = client.document_text_detection(image=image)
    
    return response.full_text

# Use with HELIX
ocr_text = extract_with_google_vision("medical_scan.jpg")
response = analyze_medical_document(ocr_text, "P12345")
```

### Azure Computer Vision

```bash
pip install azure-cognitiveservices-vision-computervision
```

```python
from azure.cognitiveservices.vision.computervision import ComputerVisionClient
from msrest.authentication import CognitiveServicesCredentials

def extract_with_azure_vision(image_path, endpoint, key):
    """Extract text using Azure Computer Vision."""
    client = ComputerVisionClient(endpoint, CognitiveServicesCredentials(key))
    
    with open(image_path, 'rb') as image_file:
        read_response = client.read_in_stream(image_file, raw=True)
    
    # Get operation ID from response header
    read_operation_location = read_response.headers["Operation-Location"]
    operation_id = read_operation_location.split("/")[-1]
    
    # Wait for result
    import time
    import requests
    while True:
        result = requests.get(
            f"{endpoint}/vision/v3.0/read/analyzeResults/{operation_id}",
            headers={"Ocp-Apim-Subscription-Key": key}
        ).json()
        
        if result["status"] != "notStarted" and result["status"] != "running":
            break
        time.sleep(1)
    
    # Extract text
    text = ""
    for page in result["analyzeResult"]["readResults"]:
        for line in page["lines"]:
            text += line["text"] + "\n"
    
    return text

# Use with HELIX
ocr_text = extract_with_azure_vision("medical_scan.jpg", "endpoint", "key")
response = analyze_medical_document(ocr_text, "P12345")
```

### Paddle OCR (Multilingual)

```bash
pip install paddleocr
```

```python
from paddleocr import PaddleOCR

def extract_with_paddle_ocr(image_path, language='en'):
    """Extract text using Paddle OCR."""
    ocr = PaddleOCR(use_angle_cls=True, lang=language)
    result = ocr.ocr(image_path, cls=True)
    
    text = ""
    for line in result:
        for word_info in line:
            text += word_info[1][0] + " "
        text += "\n"
    
    return text

# Use with HELIX
ocr_text = extract_with_paddle_ocr("medical_scan.jpg")
response = analyze_medical_document(ocr_text, "P12345")
```

## Full End-to-End Example

```python
"""
Complete example: Image → OCR → HELIX Analysis → Display
"""

import requests
from pathlib import Path
from PIL import Image
import pytesseract
import json

class MedicalDocumentAnalyzer:
    def __init__(self, helix_url="http://localhost:8000"):
        self.helix_url = helix_url
    
    def extract_ocr(self, image_path):
        """Extract text from medical image."""
        image = Image.open(image_path)
        text = pytesseract.image_to_string(image)
        return text
    
    def analyze(self, image_path, patient_id, age=None, sex=None):
        """Full analysis pipeline."""
        
        # Step 1: OCR extraction
        print(f"🔍 Extracting text from {image_path}...")
        ocr_text = self.extract_ocr(image_path)
        
        # Step 2: Call HELIX API
        print("📊 Analyzing with HELIX...")
        payload = {
            "ocr_text": ocr_text,
            "patient_id": patient_id,
            "age": age,
            "sex": sex,
            "source_type": "medical_record"
        }
        
        response = requests.post(
            f"{self.helix_url}/api/v1/analyze",
            json=payload
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            return None
        
        analysis = response.json()
        
        # Step 3: Display results
        self.print_results(analysis)
        
        return analysis
    
    def print_results(self, analysis):
        """Display analysis results."""
        print("\n" + "="*60)
        print("HELIX MEDICAL ANALYSIS RESULTS")
        print("="*60)
        
        print(f"\n👤 Patient ID: {analysis['patient_id']}")
        print(f"⏱️  Processing Time: {analysis['processing_time_ms']:.0f}ms")
        
        # Entities
        print("\n📋 EXTRACTED ENTITIES:")
        for entity_type, entities in analysis['entities'].items():
            if entities:
                print(f"\n  {entity_type.upper()}:")
                for entity in entities[:3]:  # Show top 3
                    print(f"    • {entity['text']} → {entity['normalized']} ({entity['confidence']:.0%})")
        
        # Summary
        print(f"\n📝 SHORT SUMMARY:")
        print(f"  {analysis['summary_short']}")
        
        print(f"\n📖 LONG SUMMARY:")
        print(f"  {analysis['summary_long'][:200]}...")
        
        # Risks
        if analysis['risk_flags']:
            print(f"\n⚠️  RISK FLAGS ({len(analysis['risk_flags'])}):")
            for flag in analysis['risk_flags'][:3]:
                print(f"    [{flag['severity'].upper()}] {flag['description']}")
        
        # Confidence
        print(f"\n📈 CONFIDENCE SCORES:")
        print(f"    Entity Extraction: {analysis['confidence']['entity_extraction']:.0%}")
        print(f"    Summarization: {analysis['confidence']['summarization']:.0%}")
        print(f"    Overall: {analysis['confidence']['overall']:.0%}")
        
        # Notes for doctor
        if analysis['notes_for_doctor']:
            print(f"\n👨‍⚕️  NOTES FOR DOCTOR:")
            for note in analysis['notes_for_doctor']:
                print(f"    • {note}")
        
        print("\n" + "="*60)

# Usage
if __name__ == "__main__":
    analyzer = MedicalDocumentAnalyzer()
    
    # Analyze a medical document
    result = analyzer.analyze(
        image_path="medical_scan.jpg",
        patient_id="P12345",
        age=65,
        sex="M"
    )
```

## API Response Processing

The response from HELIX includes rich structured data:

```python
def process_helix_response(response):
    """Example: Process HELIX response for various use cases."""
    
    # Save to database
    db.save_analysis(response['patient_id'], response)
    
    # Send alerts if critical
    for flag in response['risk_flags']:
        if flag['severity'] == 'critical':
            send_alert(flag['description'], response['patient_id'])
    
    # Generate report
    report = generate_pdf_report(response)
    report.save(f"report_{response['patient_id']}.pdf")
    
    # Update patient record
    ehr_system.update_patient(
        patient_id=response['patient_id'],
        summary=response['summary_short'],
        entities=response['entities'],
        risks=response['risk_flags']
    )
```

## Troubleshooting

### Issue: "OCR text is empty"
```python
# Check OCR quality
if len(ocr_text.strip()) == 0:
    print("❌ OCR failed - image quality may be too low")
    # Try:
    # 1. Increase image resolution
    # 2. Improve lighting
    # 3. Try different OCR engine
```

### Issue: "HELIX API connection failed"
```python
# Verify HELIX is running
import requests
try:
    health = requests.get("http://localhost:8000/api/v1/health")
    print(f"HELIX Status: {health.json()['status']}")
except:
    print("❌ HELIX not running - start with: python -m uvicorn app.main:app")
```

### Issue: "Low confidence scores"
```python
# Check OCR quality
# Low entity scores may mean:
# - Poor OCR text quality
# - Medical terminology not recognized
# - Document type not standard

# Try improving OCR:
# - Better image preprocessing
# - Higher resolution
# - Different OCR engine
```

## Best Practices

1. **Validate OCR Quality**: Check that extracted text is readable
2. **Use Patient Context**: Provide age, sex, known conditions when available
3. **Load History**: Include previous records for better analysis
4. **Handle Confidence**: Don't rely solely on low-confidence extractions
5. **Monitor Alerts**: Implement proper handling of critical flags
6. **Log Everything**: Keep audit trails of documents processed
7. **Error Handling**: Gracefully handle OCR failures

---

**Next Steps**:
1. Choose your OCR system
2. Implement OCR extraction function
3. Connect to HELIX using examples above
4. Test with sample medical documents
5. Integrate with your application

For questions or issues, check the README.md or ARCHITECTURE.md files.
