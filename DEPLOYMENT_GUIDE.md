# HELIX Medical NLP - Deployment Guide for Render

## Overview

This guide provides step-by-step instructions to deploy the HELIX Medical NLP System to Render.com, a modern cloud platform.

## Prerequisites

1. **GitHub Account** - Repository to host code
2. **Render Account** - Free tier available at render.com
3. **Git** - For version control

## System Architecture

```
Client Request
    ↓
[Load Balancer - Render]
    ↓
[FastAPI Application]
    ├── /api/v1/health - Health check
    ├── /api/v1/analyze - Main analysis endpoint
    ├── /api/v1/summarize - Summarization endpoint
    ├── /api/v1/extract - Entity extraction endpoint
    └── /api/v1/models - Model information
```

## Deployment Steps

### Step 1: Prepare GitHub Repository

```bash
# Initialize git (if not done)
cd helix_medical_nlp
git init
git add .
git commit -m "Initial commit: HELIX Medical NLP System"

# Create GitHub repository at github.com/new
# Then push:
git remote add origin https://github.com/YOUR_USERNAME/helix-medical-nlp.git
git branch -M main
git push -u origin main
```

### Step 2: Login to Render

1. Go to https://render.com
2. Sign up or login with GitHub
3. Click "New +" button

### Step 3: Create Web Service

1. **Select Repository Type:** Web Service
2. **Connect Repository:** Select your helix-medical-nlp repository
3. **Service Settings:**
   - **Name:** helix-medical-nlp
   - **Environment:** Python
   - **Region:** Select closest region
   - **Branch:** main
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 4: Configure Environment Variables

In Render dashboard, add these environment variables:

```
USE_SCISPACY=false
SUMMARIZATION_MODEL=default
LOG_LEVEL=INFO
DEVICE=cpu
DEBUG=False
```

### Step 5: Deploy

1. Click "Create Web Service"
2. Wait for deployment (2-5 minutes)
3. You'll get a URL like: `https://helix-medical-nlp.onrender.com`

## Verification

### Check Health Endpoint

```bash
curl https://helix-medical-nlp.onrender.com/api/v1/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "models_loaded": {
    "entity_extractor": true,
    "summarizer": true,
    "risk_detector": true
  },
  "timestamp": "2026-03-22T12:00:00"
}
```

### Test Analyze Endpoint

```bash
curl -X POST https://helix-medical-nlp.onrender.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_text": "Patient presents with cough and fever. Prescribed Amoxycillin 500mg",
    "patient_id": "TEST-001",
    "age": 45,
    "sex": "M"
  }'
```

### View API Documentation

- **Swagger UI:** `https://helix-medical-nlp.onrender.com/docs`
- **ReDoc:** `https://helix-medical-nlp.onrender.com/redoc`
- **OpenAPI JSON:** `https://helix-medical-nlp.onrender.com/openapi.json`

## Available Endpoints

### 1. Health Check
- **Endpoint:** `GET /api/v1/health`
- **Purpose:** Verify service is running
- **Response:** Service status, loaded models, timestamp

### 2. Analyze Medical Text
- **Endpoint:** `POST /api/v1/analyze`
- **Purpose:** Complete medical analysis
- **Request:**
  ```json
  {
    "ocr_text": "string (required)",
    "patient_id": "string (optional)",
    "age": "integer (optional)",
    "sex": "string (optional)",
    "date": "datetime (optional)",
    "source_type": "string (optional)",
    "known_conditions": ["string"],
    "previous_records": [...]
  }
  ```
- **Response:**
  ```json
  {
    "patient_id": "string",
    "entities": {
      "diseases": [...],
      "symptoms": [...],
      "medications": [...],
      "tests": [...],
      "procedures": [...],
      "measurements": [...]
    },
    "summary_short": "string",
    "summary_long": "string",
    "risk_flags": [...],
    "confidence": {...},
    "processing_time_ms": number
  }
  ```

### 3. Summarize Text
- **Endpoint:** `POST /api/v1/summarize`
- **Purpose:** Generate medical summaries
- **Request:**
  ```json
  {
    "text": "string (required)",
    "previous_records": [...]
  }
  ```
- **Response:**
  ```json
  {
    "short_summary": "string",
    "long_summary": "string",
    "input_length": number,
    "cleaned_length": number
  }
  ```

### 4. Extract Entities
- **Endpoint:** `POST /api/v1/extract`
- **Purpose:** Extract medical entities only
- **Request:**
  ```json
  {
    "text": "string (required)"
  }
  ```
- **Response:**
  ```json
  {
    "entities": {
      "diseases": [...],
      "symptoms": [...],
      ...
    },
    "total_entities": number
  }
  ```

### 5. Get Models Info
- **Endpoint:** `GET /api/v1/models`
- **Purpose:** View loaded models and versions
- **Response:**
  ```json
  {
    "models": {...},
    "entity_extraction": {...},
    "summarization": {...}
  }
  ```

## Integration Example

### Python

```python
import requests
import json

URL = "https://helix-medical-nlp.onrender.com"

# Check health
health = requests.get(f"{URL}/api/v1/health").json()
print(f"Status: {health['status']}")

# Analyze prescription
prescription_text = """
Dr. Smith
Patient: John Doe

Chief Complaint: Cough with fever for 3 days
Vitals: Temp 38.5C, SpO2 92%, RR 22

Diagnosis: Suspected pneumonia

Medications:
1. Augmentin 625mg - 1-0-1 for 7 days
2. Paracetamol 500mg - SOS

Investigations:
- Chest X-ray
- Blood culture
"""

response = requests.post(
    f"{URL}/api/v1/analyze",
    json={
        "ocr_text": prescription_text,
        "patient_id": "DOE-001",
        "age": 45,
        "sex": "M",
        "source_type": "prescription"
    }
)

result = response.json()
print(json.dumps(result, indent=2))
```

### JavaScript

```javascript
const BASE_URL = "https://helix-medical-nlp.onrender.com";

async function analyzeText(ocrText, patientId) {
  const response = await fetch(`${BASE_URL}/api/v1/analyze`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      ocr_text: ocrText,
      patient_id: patientId,
      source_type: "prescription"
    })
  });

  return await response.json();
}

// Usage
analyzeText("Cough with fever for 3 days...", "TEST-001")
  .then(result => console.log(result))
  .catch(error => console.error(error));
```

### cURL

```bash
# Health check
curl https://helix-medical-nlp.onrender.com/api/v1/health

# Analyze
curl -X POST https://helix-medical-nlp.onrender.com/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_text": "Patient has cough and fever. Prescribed Amoxycillin.",
    "patient_id": "TEST-001"
  }'
```

## Monitoring

### View Logs

1. Go to Render Dashboard
2. Select your service
3. Click "Logs" tab
4. Monitor real-time logs

### Check Performance

- **Response Time:** Should be < 1 second for most requests
- **CPU Usage:** Low (< 20%) for typical loads
- **Memory:** ~500MB base + ~100MB per request

## Troubleshooting

### Deployment Fails

**Error:** "Build failed"
- Check requirements.txt syntax
- Verify Python 3.11 compatibility
- Check for missing dependencies

**Error:** "Port binding failed"
- Render automatically assigns PORT environment variable
- Ensure app uses `$PORT` variable

### Service Won't Start

**Error:** "Service fails to start"
- Check logs in Render dashboard
- Verify all imports work correctly
- Test locally: `uvicorn app.main:app`

**Error:** "Module not found"
- Add missing dependency to requirements.txt
- Redeploy service

### Slow Responses

**Issue:** Endpoints take > 5 seconds
- First request loads models (slow)
- Subsequent requests should be fast
- Check Render resource allocation

## Auto-Deployment

Enable auto-deployment from GitHub:

1. Go to Service Settings
2. Find "Auto-Deploy"
3. Toggle "Yes" for "Auto-deploy on push to branch"
4. Now any commit to `main` triggers deployment

## Custom Domain (Optional)

1. Go to Service Settings
2. Click "Add Custom Domain"
3. Enter your domain
4. Update DNS records as shown
5. SSL certificate auto-generated

## Scaling

### Free Tier Limits
- 1 web service
- 0.5GB RAM
- Limited compute time
- Auto-sleep after 15 minutes inactive

### Paid Tiers
- Multiple services
- Dedicated resources
