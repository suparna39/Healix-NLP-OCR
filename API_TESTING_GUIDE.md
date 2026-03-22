# HELIX Medical NLP - API Testing Guide

**Live API:** `https://healix-nlp-ocr.onrender.com`

**Interactive Docs:** `https://healix-nlp-ocr.onrender.com/docs`

---

## Available Endpoints

### 1. **Health Check** ✅
**Purpose:** Verify service is running and models are loaded

**Endpoint:** `GET /api/v1/health`

**Response:**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": {
    "entity_extractor": true,
    "summarizer": true,
    "risk_detector": true
  },
  "timestamp": "2026-03-22T04:13:59.997500"
}
```

**cURL:**
```bash
curl -s "https://healix-nlp-ocr.onrender.com/api/v1/health"
```

---

### 2. **Extract Entities** 🏥
**Purpose:** Extract medical entities from text (diseases, medications, symptoms, tests, etc.)

**Endpoint:** `POST /api/v1/extract`

**Request Body:**
```json
{
  "text": "Patient has diabetes and hypertension. Prescribed metformin 500mg twice daily and lisinopril 10mg once daily. Blood pressure 140/85 mmHg."
}
```

**Response:**
```json
{
  "entities": {
    "diseases": [
      {
        "text": "diabetes",
        "normalized": "diabetes mellitus",
        "confidence": 0.95,
        "synonyms": ["DM", "diabetes"]
      },
      {
        "text": "hypertension",
        "normalized": "hypertension",
        "confidence": 0.92,
        "synonyms": ["high blood pressure", "HTN"]
      }
    ],
    "medications": [
      {
        "text": "metformin 500mg",
        "normalized": "metformin",
        "confidence": 0.98,
        "synonyms": []
      },
      {
        "text": "lisinopril 10mg",
        "normalized": "lisinopril",
        "confidence": 0.97,
        "synonyms": []
      }
    ],
    "measurements": [
      {
        "text": "140/85 mmHg",
        "normalized": "systolic 140 / diastolic 85 mmHg",
        "confidence": 0.99,
        "synonyms": []
      }
    ],
    "symptoms": [],
    "tests": [],
    "procedures": [],
    "anatomy": []
  }
}
```

**cURL:**
```bash
curl -X POST "https://healix-nlp-ocr.onrender.com/api/v1/extract" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient has diabetes and hypertension. Prescribed metformin 500mg twice daily and lisinopril 10mg once daily. Blood pressure 140/85 mmHg."
  }'
```

---

### 3. **Summarize Text** 📝
**Purpose:** Generate short and long summaries of medical text

**Endpoint:** `POST /api/v1/summarize`

**Request Body:**
```json
{
  "text": "Patient presented with persistent headache and fever for 3 days. Vital signs: BP 145/90, HR 88. Physical examination revealed mild cervical stiffness. Lab work ordered. Patient prescribed acetaminophen and advised rest. Follow-up appointment in 5 days."
}
```

**Response:**
```json
{
  "short_summary": "Patient with 3-day headache and fever, mild cervical stiffness, prescribed acetaminophen.",
  "long_summary": "Patient presented with a 3-day history of headache and fever with mild cervical stiffness on examination. Vital signs show BP 145/90 mmHg with heart rate 88 bpm. Laboratory work has been ordered for further evaluation. Treatment includes acetaminophen, rest, and follow-up in 5 days.",
  "input_length": 287,
  "cleaned_length": 287
}
```

**cURL:**
```bash
curl -X POST "https://healix-nlp-ocr.onrender.com/api/v1/summarize" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient presented with persistent headache and fever for 3 days. Vital signs: BP 145/90, HR 88. Physical examination revealed mild cervical stiffness. Lab work ordered. Patient prescribed acetaminophen and advised rest. Follow-up appointment in 5 days."
  }'
```

**⏱️ First Request:** Will take 2-3 minutes (downloading FLAN-T5 model ~900MB)
**⚡ Subsequent Requests:** Will be instant (model cached in memory)

---

### 4. **Analyze (Full Pipeline)** 🔬
**Purpose:** Complete analysis - extract entities, summarize, detect risks

**Endpoint:** `POST /api/v1/analyze`

**Request Body:**
```json
{
  "ocr_text": "Patient: John Doe, Age 45, M. Presenting with chest pain and shortness of breath. BP 160/95, HR 105. EKG shows ST elevation. Troponin levels elevated. Diagnosed with acute myocardial infarction. Patient transferred to CCU. Prescribed aspirin, heparin, and nitrates.",
  "patient_id": "PAT-001",
  "age": 45,
  "sex": "M",
  "source_type": "emergency_report"
}
```

**Response:**
```json
{
  "patient_id": "PAT-001",
  "entities": {
    "diseases": [
      {
        "text": "chest pain",
        "entity_type": "symptom",
        "normalized": "chest pain",
        "confidence": 0.95,
        "start_pos": 40,
        "end_pos": 50
      },
      {
        "text": "acute myocardial infarction",
        "entity_type": "disease",
        "normalized": "acute myocardial infarction",
        "confidence": 0.98,
        "start_pos": 140,
        "end_pos": 167
      }
    ],
    "medications": [
      {
        "text": "aspirin",
        "entity_type": "medication",
        "normalized": "aspirin",
        "confidence": 0.99,
        "start_pos": 210,
        "end_pos": 217
      }
    ]
  },
  "summary_short": "45-year-old male with acute MI presenting with chest pain and dyspnea.",
  "summary_long": "Patient is a 45-year-old male presenting to emergency with chest pain and shortness of breath. Vital signs show hypertension (160/95) and tachycardia (105). EKG demonstrates ST elevation concerning for acute MI. Troponin levels are elevated confirming myocardial infarction. Patient transferred to CCU for intensive monitoring and management with aspirin, heparin, and nitrates.",
  "risk_flags": [
    {
      "flag_type": "critical",
      "severity": "critical",
      "description": "Acute myocardial infarction detected",
      "explanation": "ST elevation on EKG with elevated troponin confirms acute MI",
      "entities_involved": ["chest pain", "acute myocardial infarction"],
      "recommended_action": "Immediate cardiology consultation, continue CCU monitoring"
    },
    {
      "flag_type": "high_bp",
      "severity": "high",
      "description": "Hypertension (160/95 mmHg)",
      "explanation": "Significantly elevated blood pressure",
      "entities_involved": ["BP 160/95"],
      "recommended_action": "Antihypertensive medication adjustment"
    }
  ],
  "confidence": {
    "entity_extraction": 0.94,
    "summarization": 0.89,
    "context_understanding": 0.91,
    "overall": 0.91
  },
  "notes_for_doctor": [
    "Critical: Acute MI confirmed - immediate specialist review needed",
    "Monitor cardiac markers and vital signs continuously",
    "Consider cardiac imaging (echo, angiography) as needed"
  ],
  "warnings": [
    "CRITICAL: This patient requires immediate intensive care",
    "Risk of cardiogenic shock - continuous monitoring essential"
  ],
  "processing_time_ms": 1245,
  "model_versions": {
    "entity_extractor": "pattern-based + optional scispacy",
    "summarization": "google/flan-t5-base",
    "system_version": "1.0.0"
  }
}
```

**cURL:**
```bash
curl -X POST "https://healix-nlp-ocr.onrender.com/api/v1/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_text": "Patient: John Doe, Age 45, M. Presenting with chest pain and shortness of breath. BP 160/95, HR 105. EKG shows ST elevation. Troponin levels elevated. Diagnosed with acute myocardial infarction. Patient transferred to CCU. Prescribed aspirin, heparin, and nitrates.",
    "patient_id": "PAT-001",
    "age": 45,
    "sex": "M",
    "source_type": "emergency_report"
  }'
```

---

### 5. **Get Models Info** ℹ️
**Purpose:** Get information about loaded models

**Endpoint:** `GET /api/v1/models`

**Response:**
```json
{
  "entity_extractor": "pattern-based + optional scispacy",
  "summarization": "google/flan-t5-base",
  "system_version": "1.0.0"
}
```

**cURL:**
```bash
curl -s "https://healix-nlp-ocr.onrender.com/api/v1/models"
```

---

## Testing Recommendations

### **Test Order (from fastest to slowest):**

1. ✅ **Health Check** (instant) - Verify service is up
2. ✅ **Models Info** (instant) - Check loaded models
3. ✅ **Extract Entities** (1-2 seconds) - Test entity recognition
4. ⏱️ **Summarize** (2-3 mins first call, then instant) - Test summarization
5. ⏱️ **Analyze** (2-3 mins first call, then 2-5 seconds) - Full pipeline test

### **Important Notes:**

- **First request to summarize/analyze will take 2-3 minutes** (downloading ~900MB FLAN-T5 model)
- **Subsequent requests will be fast** (model cached in memory)
- **Render free tier has 512MB RAM limit** - model takes ~1.2GB in memory
- **Health check must pass** before accessing other endpoints

---

## Python Example

```python
import requests
import json

BASE_URL = "https://healix-nlp-ocr.onrender.com"

# 1. Health check
response = requests.get(f"{BASE_URL}/api/v1/health")
print("Health:", response.json())

# 2. Extract entities
extract_data = {
    "text": "Patient diagnosed with type 2 diabetes. Prescribed metformin 1000mg daily."
}
response = requests.post(f"{BASE_URL}/api/v1/extract", json=extract_data)
print("Entities:", response.json())

# 3. Summarize text (will take 2-3 minutes on first call)
summarize_data = {
    "text": "Patient presented with persistent cough for 2 weeks. Chest X-ray shows infiltrates. Given antibiotics and advised to return in 1 week."
}
response = requests.post(f"{BASE_URL}/api/v1/summarize", json=summarize_data)
print("Summary:", response.json())

# 4. Full analysis
analyze_data = {
    "ocr_text": "Patient has hypertension and diabetes. BP 150/90, glucose 280 mg/dL.",
    "patient_id": "PAT-123",
    "age": 55,
    "sex": "M"
}
response = requests.post(f"{BASE_URL}/api/v1/analyze", json=analyze_data)
print("Analysis:", response.json())
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `502 Bad Gateway` | Service is restarting, wait 1-2 minutes |
| `Service Unavailable` | Render free tier went to sleep, restart the service |
| Request times out after 30s | First request to summarizer is downloading model, wait 2-3 minutes |
| `422 Validation Error` | Check JSON format matches schema |
| Empty results | Input text too short or no matching patterns |

---

## Rate Limits

- **Render Free Tier:** No specific rate limits, but performance may degrade under high load
- **Recommended:** 1-2 requests per second for optimal performance

---

## Next Steps

1. Deploy the latest code to Render
2. Visit interactive docs: `https://healix-nlp-ocr.onrender.com/docs`
3. Test each endpoint in order
4. Monitor Render logs for any issues
5. First summarize request will trigger model download (~2-3 mins)
