# HELIX Medical NLP - Complete User Guide

## Welcome to HELIX Medical NLP! 🏥

This guide will help you get started quickly and understand how to use the system.

---

## 📚 Table of Contents

1. [What is HELIX?](#what-is-helix)
2. [Quick Start (5 minutes)](#quick-start-5-minutes)
3. [Understanding the Output](#understanding-the-output)
4. [Using the API](#using-the-api)
5. [Connecting OCR Systems](#connecting-ocr-systems)
6. [Troubleshooting](#troubleshooting)
7. [Advanced Usage](#advanced-usage)

---

## What is HELIX?

**HELIX Medical NLP** is an AI-powered system that transforms raw medical documents into structured, actionable intelligence.

### What it does:
- 📝 Extracts medical information from OCR text
- 🔍 Identifies diseases, symptoms, medications, tests
- 📊 Generates clinical summaries
- ⚠️ Detects risks and alerts
- 🎯 Provides confidence scores

### What it's for:
- Medical record processing
- Clinical decision support
- Document summarization
- Information extraction
- Data organization

---

## Quick Start (5 minutes)

### Step 1: Install (2 minutes)

```bash
# Navigate to project
cd helix_medical_nlp

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Mac/Linux)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Server (1 minute)

```bash
python -m uvicorn app.main:app --reload
```

You should see:
```
Uvicorn running on http://127.0.0.1:8000
```

### Step 3: Test it (2 minutes)

**Option A: Interactive Testing (Recommended)**
1. Open browser: http://localhost:8000/docs
2. Click on **POST /api/v1/analyze**
3. Click **Try it out**
4. Paste this in the request body:

```json
{
  "ocr_text": "Patient with diabetes presents with fever and cough. Taking metformin and aspirin.",
  "patient_id": "P001"
}
```

5. Click **Execute**
6. Scroll down to see the response!

**Option B: Command Line**

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"ocr_text": "Patient with diabetes takes metformin", "patient_id": "P001"}'
```

---

## Understanding the Output

### Response Structure

Every response from HELIX includes:

```json
{
  "patient_id": "P001",
  
  "entities": {
    "diseases": [
      {
        "text": "diabetes",
        "normalized": "Diabetes Mellitus",
        "confidence": 0.90,
        "explanation": "Mentioned in text"
      }
    ],
    "symptoms": [...],
    "medications": [...],
    "tests": [...],
    "procedures": [...],
    "measurements": [...]
  },
  
  "summary_short": "Patient with diabetes...",
  "summary_long": "More detailed summary...",
  
  "risk_flags": [
    {
      "severity": "high",
      "description": "Patient on multiple medications",
      "recommended_action": "Review medication interactions"
    }
  ],
  
  "confidence": {
    "entity_extraction": 0.87,
    "summarization": 0.89,
    "overall": 0.84
  },
  
  "notes_for_doctor": [
    "Review patient medications",
    "Follow up on symptoms"
  ]
}
```

### Interpreting Results

**Confidence Scores**:
- `0.85+` - High confidence ✅
- `0.70-0.84` - Moderate confidence ⚠️
- `0.50-0.69` - Low confidence ⚠️⚠️
- `<0.50` - Very low confidence ❌

**Risk Severity**:
- `CRITICAL` - Immediate action needed 🚨
- `HIGH` - Important, review soon ⚠️
- `MEDIUM` - Monitor and consider 📋
- `LOW` - Informational only ℹ️

---

## Using the API

### Endpoint 1: Full Analysis

**POST** `/api/v1/analyze`

**Request:**
```json
{
  "ocr_text": "Medical text from OCR...",
  "patient_id": "P12345",
  "age": 65,
  "sex": "M",
  "source_type": "clinic_visit",
  "known_conditions": ["diabetes", "hypertension"],
  "previous_records": null
}
```

**Response**: Complete analysis with all fields

---

### Endpoint 2: Summarization Only

**POST** `/api/v1/summarize`

Use when you only need summaries without entity extraction.

**Request:**
```json
{
  "text": "Long medical text...",
  "previous_records": null
}
```

**Response:**
```json
{
  "short_summary": "Brief summary",
  "long_summary": "Detailed summary"
}
```

---

### Endpoint 3: Entity Extraction Only

**POST** `/api/v1/extract`

Use to extract entities without summarization.

**Request:**
```json
{
  "text": "Medical text..."
}
```

**Response:**
```json
{
  "entities": {
    "diseases": [...],
    "symptoms": [...],
    "medications": [...],
    ...
  },
  "total_entities": 24
}
```

---

### Endpoint 4: Health Check

**GET** `/api/v1/health`

Check if service is running and models are loaded.

**Response:**
```json
{
  "status": "healthy",
  "models_loaded": {
    "entity_extractor": true,
    "summarizer": true
  }
}
```

---

### Endpoint 5: Model Information

**GET** `/api/v1/models`

Get details about loaded models.

---

## Connecting OCR Systems

### Basic Pattern

```python
from your_ocr import extract_text
import requests

# Step 1: Extract OCR text
ocr_text = extract_text("medical_scan.jpg")

# Step 2: Send to HELIX
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "ocr_text": ocr_text,
        "patient_id": "P12345"
    }
)

# Step 3: Use response
analysis = response.json()
print(analysis['summary_short'])
```

### Example: Using Tesseract

```python
import pytesseract
from PIL import Image
import requests

# Extract text
image = Image.open("medical_scan.jpg")
ocr_text = pytesseract.image_to_string(image)

# Analyze
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"ocr_text": ocr_text, "patient_id": "P001"}
)

print(response.json()['summary_short'])
```

See `OCR_INTEGRATION_GUIDE.md` for more examples.

---

## Troubleshooting

### Problem: "Module not found" error

**Solution**: Install dependencies
```bash
pip install -r requirements.txt
```

### Problem: Port 8000 already in use

**Solution**: Use different port
```bash
python -m uvicorn app.main:app --port 8080
```

### Problem: Low confidence scores

**Possible causes**:
- Poor OCR quality
- Rare medical terminology
- Insufficient patient context

**Solutions**:
- Improve OCR preprocessing
- Provide patient history if available
- Check OCR confidence

### Problem: "CUDA out of memory"

**Solution**: Use CPU (default)
```bash
# In .env
DEVICE=cpu
```

### Problem: Missing models

**Solution**: Models auto-download on first use (~3GB)
- Be patient on first run
- Ensure internet connection
- Check disk space

---

## Advanced Usage

### Using with Patient History

```python
from app.models.schemas import MedicalRecord, AnalysisRequest
from datetime import datetime

# Previous record
prev_record = MedicalRecord(
    record_id="PREV001",
    date=datetime(2024, 2, 15),
    document_type="clinic_visit",
    raw_text="Patient had diabetes. BP stable."
)

# Current analysis request
request = AnalysisRequest(
    ocr_text="Patient presents with fever",
    patient_id="P001",
    previous_records=[prev_record]
)

# Analyze
response = pipeline.process(request)
print(response.history_integration)
```

### Batch Processing

```python
from pathlib import Path
import json

results = []
for ocr_file in Path("ocr_texts/").glob("*.txt"):
    with open(ocr_file) as f:
        ocr_text = f.read()
    
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json={
            "ocr_text": ocr_text,
            "patient_id": ocr_file.stem
        }
    )
    
    results.append(response.json())

# Save results
with open("analysis_results.json", "w") as f:
    json.dump(results, f, indent=2)
```

### Custom Configuration

Edit `.env` to customize:

```bash
# Model selection
SUMMARIZATION_MODEL=google/flan-t5-large

# Hardware
DEVICE=cuda

# Logging
LOG_LEVEL=DEBUG

# Rate limiting
RATE_LIMIT_REQUESTS=1000
```

### Running Tests

```bash
# All tests
pytest tests/

# Specific test
pytest tests/test_components.py::TestOCRCleaner

# With coverage
pytest --cov=app tests/
```

### Running Examples

```bash
cd examples
python quick_start.py
```

---

## Common Use Cases

### Use Case 1: Summarize Long Medical Records

```python
request_body = {
    "text": "Long medical record text...",
}
response = requests.post(
    "http://localhost:8000/api/v1/summarize",
    json=request_body
)
print(response.json()['long_summary'])
```

### Use Case 2: Extract Medications

```python
request_body = {
    "text": "Patient taking aspirin, metformin, lisinopril..."
}
response = requests.post(
    "http://localhost:8000/api/v1/extract",
    json=request_body
)
medications = response.json()['entities']['medications']
for med in medications:
    print(f"- {med['text']} ({med['normalized']})")
```

### Use Case 3: Alert on Critical Conditions

```python
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={"ocr_text": ocr_text, "patient_id": patient_id}
).json()

for flag in response['risk_flags']:
    if flag['severity'] == 'critical':
        send_alert(flag['description'], patient_id)
```

### Use Case 4: Generate Clinical Report

```python
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={...}
).json()

report = f"""
Patient ID: {response['patient_id']}
Summary: {response['summary_long']}

Key Findings:
{json.dumps(response['entities'], indent=2)}

Risks: {len(response['risk_flags'])} flagged
"""
```

---

## Best Practices

### ✅ DO:
- ✅ Provide clean OCR text
- ✅ Include patient context when available
- ✅ Monitor confidence scores
- ✅ Review critical alerts
- ✅ Use patient history for better accuracy
- ✅ Handle errors gracefully

### ❌ DON'T:
- ❌ Rely on system alone for diagnosis
- ❌ Use poor quality OCR
- ❌ Ignore low confidence scores
- ❌ Skip security/privacy checks
- ❌ Ignore critical alerts
- ❌ Process without error handling

---

## Performance Tips

### For Better Results:
1. **High quality OCR** - Better text = better analysis
2. **Patient context** - Provide age, sex, known conditions
3. **Previous history** - Include past records when available
4. **Realistic expectations** - System is support tool, not replacement

### For Better Speed:
1. **Use CPU** - GPU not needed for medical NLP (CPU fast enough)
2. **Batch processing** - Process multiple documents together
3. **Adequate resources** - Minimum 2GB RAM, 10GB disk
4. **Monitor memory** - Long documents use more memory

### For Better Reliability:
1. **Error handling** - Wrap API calls in try-except
2. **Retry logic** - Retry failed requests
3. **Logging** - Log all interactions
4. **Health checks** - Monitor system health regularly

---

## Next Steps

### For Beginners:
1. Read this guide thoroughly
2. Run `/docs` endpoint and try examples
3. Read `QUICKSTART.md` for setup help
4. Run `examples/quick_start.py` to see it in action

### For Developers:
1. Review `ARCHITECTURE.md` for technical details
2. Read the inline code documentation
3. Explore `app/` module structure
4. Run unit tests: `pytest tests/`

### For Integration:
1. Read `OCR_INTEGRATION_GUIDE.md`
2. Choose your OCR system
3. Implement the integration pattern
4. Test thoroughly with sample documents

### For Deployment:
1. Review `README.md` deployment section
2. Use provided `Procfile` and `render.yaml`
3. Set environment variables
4. Deploy to Render or similar platform

---

## Support Resources

### Documentation Files
- **README.md** - Complete system documentation
- **QUICKSTART.md** - 5-minute setup
- **ARCHITECTURE.md** - Technical deep dive
- **OCR_INTEGRATION_GUIDE.md** - Integration examples
- **INDEX.md** - File structure and navigation

### API Documentation
- Visit `/docs` endpoint while server running
- Interactive Swagger UI with try-it-out
- Full request/response schemas

### Code Examples
- `examples/quick_start.py` - 4 working examples
- `examples/sample_request.json` - Example request
- `examples/sample_response.json` - Example response
- `data/sample_data.py` - Test data

---

## FAQ

**Q: Can this diagnose patients?**
A: No. This is a clinical support tool. Always consult qualified physicians for diagnosis.

**Q: How accurate is the system?**
A: Check confidence scores (85%+ = high, <50% = low). Accuracy depends on OCR quality and medical complexity.

**Q: Can I use this offline?**
A: Models download on first use. After that, system works fully offline (CPU only).

**Q: How do I improve results?**
A: Better OCR, provide patient context, include history, check confidence scores.

**Q: Can I customize entity types?**
A: Yes. Edit `app/nlp/entity_extractor.py` to add patterns.

**Q: What's the cost?**
A: Free to use locally. Deploy on Render (minimal cost) or your infrastructure.

---

## Getting Help

1. **Setup Issues** → See `QUICKSTART.md`
2. **Technical Questions** → See `ARCHITECTURE.md`
3. **API Usage** → Visit `/docs` endpoint
4. **Integration** → See `OCR_INTEGRATION_GUIDE.md`
5. **Code Issues** → Check inline documentation

---

## Success! 🎉

You're now ready to use HELIX Medical NLP!

**Next**: Connect your OCR system and start analyzing medical documents.

For questions, refer to the comprehensive documentation in the project root.

---

**Version**: 1.0.0
**Status**: Production Ready ✅
**Last Updated**: March 2024
