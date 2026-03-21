# HELIX Medical NLP Engine

A production-ready medical NLP system for extracting structured medical information from OCR text, previous medical records, and generating context-aware clinical summaries.

## 🏥 Features

- **Medical Entity Extraction**: Diseases, symptoms, medications, procedures, tests, and measurements
- **Smart Text Cleaning**: Handles OCR noise, abbreviations, and medical terminology
- **Medical Term Normalization**: Standardizes medical terms with UMLS-style mapping
- **Context Integration**: Merges current findings with patient history for better understanding
- **Intelligent Summarization**: Both short (1-2 sentence) and long comprehensive summaries
- **Risk Detection**: Identifies critical conditions, drug interactions, symptom clusters
- **Confidence Scoring**: Transparency through confidence metrics on extractions and summaries
- **Doctor-Friendly Output**: Structured JSON optimized for medical workflows
- **Render Ready**: Cloud-deployable with included configuration

## 📋 Architecture

```
HELIX Medical NLP Pipeline:
1. OCR Text Cleaning      → Remove noise, normalize abbreviations
2. Entity Extraction      → Extract medical concepts (scispaCy + patterns)
3. Term Normalization     → Map to standard medical terminology
4. Context Merging        → Integrate patient history
5. Summarization          → Generate clinical summaries (FLAN-T5)
6. Risk Detection         → Identify alerts and flags
7. Confidence Scoring     → Quality metrics
8. Response Generation    → Doctor-friendly JSON output
```

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd helix_medical_nlp

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download required models (optional, will auto-download on first use)
python -m spacy download en_core_sci_md
```

### Environment Setup

```bash
# Copy and customize env file
cp .env.example .env

# Edit as needed
nano .env
```

### Run Locally

```bash
# Start the server
python -m uvicorn app.main:app --reload

# Visit http://localhost:8000/docs for interactive API docs
```

## 📚 API Endpoints

### POST `/api/v1/analyze` - Main Analysis

Comprehensive medical text analysis with entity extraction, summarization, and risk detection.

**Request:**
```json
{
  "ocr_text": "Patient presents with chest pain...",
  "patient_id": "P12345",
  "age": 65,
  "sex": "M",
  "source_type": "emergency_department",
  "known_conditions": ["hypertension", "diabetes"],
  "previous_records": [...]
}
```

**Response:**
```json
{
  "patient_id": "P12345",
  "entities": {
    "diseases": [
      {
        "text": "myocardial infarction",
        "normalized": "Myocardial Infarction",
        "confidence": 0.92,
        "explanation": "ST elevation noted in ECG"
      }
    ],
    "symptoms": [...],
    "medications": [...],
    "tests": [...],
    "procedures": [...],
    "measurements": [...]
  },
  "normalized_terms": {...},
  "summary_short": "65-year-old male with inferior STEMI presenting with chest pain and dyspnea.",
  "summary_long": "Patient is a 65-year-old male with significant cardiac risk factors...",
  "history_integration": "New acute event compared to stable baseline from previous visit.",
  "risk_flags": [
    {
      "flag_type": "critical_disease",
      "severity": "critical",
      "description": "Critical condition detected: Myocardial Infarction",
      "explanation": "ST elevation MI requires immediate intervention",
      "recommended_action": "Urgent cardiac catheterization"
    }
  ],
  "confidence": {
    "entity_extraction": 0.87,
    "summarization": 0.89,
    "context_understanding": 0.75,
    "overall": 0.84
  },
  "notes_for_doctor": [
    "⚠️ ALERT: Critical condition detected: Myocardial Infarction",
    "Patient on aspirin and lisinopril - verify compliance"
  ],
  "warnings": [],
  "processing_time_ms": 245.3,
  "model_versions": {...}
}
```

### POST `/api/v1/summarize` - Summarization Only

Generate summaries without full entity extraction.

**Request:**
```json
{
  "text": "Patient medical text...",
  "previous_records": []
}
```

**Response:**
```json
{
  "short_summary": "Brief clinical summary",
  "long_summary": "Comprehensive narrative summary",
  "input_length": 2048,
  "cleaned_length": 1876
}
```

### POST `/api/v1/extract` - Entity Extraction Only

Extract medical entities without summarization.

**Request:**
```json
{
  "text": "Patient medical text..."
}
```

**Response:**
```json
{
  "entities": {
    "diseases": [...],
    "symptoms": [...],
    "medications": [...],
    "tests": [...],
    "procedures": [...],
    "measurements": [...]
  },
  "total_entities": 24
}
```

### GET `/api/v1/health` - Health Check

Check service status and model availability.

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
  "timestamp": "2024-03-20T15:30:00"
}
```

### GET `/api/v1/models` - Model Information

Get information about loaded models.

**Response:**
```json
{
  "models": {
    "entity_extractor": "scispacy-0.5.0 + custom rules",
    "summarization": "google/flan-t5-base",
    "system_version": "1.0.0"
  },
  "entity_extraction": {
    "primary": "scispaCy (en_core_sci_md)",
    "secondary": "Custom rule-based patterns"
  },
  "summarization": {
    "model": "google/flan-t5-base",
    "type": "Sequence-to-sequence transformer"
  }
}
```

## 🔧 Configuration

### Core Settings (`app/core/config.py`)

- **Model Selection**: Toggle between scispaCy, BioERT, etc.
- **Device**: CPU or CUDA GPU support
- **Summarization Model**: Switch to different FLAN-T5 sizes (base, large, xl)
- **History Settings**: Control how many previous records to consider
- **Rate Limiting**: API usage controls
- **Logging**: Debug level configuration

### Environment Variables

```bash
DEBUG=False                              # Development mode
PORT=8000                                # API port
LOG_LEVEL=INFO                          # Logging level
DEVICE=cpu                              # cpu or cuda
USE_SCISPACY=True                       # Enable scispaCy
SUMMARIZATION_MODEL=google/flan-t5-base # Model to use
STORAGE_PATH=./data/patient_records     # Data directory
UMLS_API_KEY=<your-key>                 # UMLS integration (optional)
```

## 📦 Project Structure

```
helix_medical_nlp/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app entry point
│   ├── api/
│   │   ├── __init__.py
│   │   └── routes.py           # API endpoint definitions
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py           # Configuration management
│   │   ├── logging_config.py   # Logging setup
│   │   └── pipeline.py         # Main NLP pipeline orchestration
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic data models
│   ├── nlp/
│   │   ├── __init__.py
│   │   ├── ocr_cleaner.py      # OCR text preprocessing
│   │   ├── entity_extractor.py # Medical entity NER
│   │   ├── normalizer.py       # Term normalization
│   │   ├── context_merger.py   # History integration
│   │   ├── summarizer.py       # Text summarization
│   │   └── risk_detector.py    # Risk/alert detection
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── __init__.py
│   └── test_components.py      # Unit tests
├── data/
│   ├── sample_data.py          # Sample OCR and test data
│   └── patient_records/        # Patient history storage
├── checkpoints/                # Model cache directory
├── logs/                        # Application logs
├── requirements.txt            # Python dependencies
├── .env.example               # Environment template
├── Procfile                    # Render deployment config
├── render.yaml                # Render service definition
└── README.md                  # This file
```

## 🧬 Entity Types

The system extracts and normalizes 7 primary medical entity types:

| Type | Examples | Normalization |
|------|----------|---------------|
| **Disease** | diabetes, hypertension, pneumonia, MI | UMLS-style mapping |
| **Symptom** | fever, chest pain, dyspnea, nausea | Comprehensive synonym database |
| **Medication** | aspirin, metformin, lisinopril | Brand/generic name mapping |
| **Test** | ECG, chest X-ray, blood test, MRI | Procedure standardization |
| **Procedure** | surgery, intubation, biopsy, catheterization | Procedural terminology |
| **Measurement** | glucose 280 mg/dL, BP 150/95 | Value extraction with units |
| **Anatomy** | heart, lungs, kidney | Anatomical structures |

## 🎯 Risk Detection

The system identifies several categories of medical risks:

1. **Critical Conditions**: Stroke, MI, sepsis, cardiac arrest
2. **Critical Symptoms**: Chest pain, difficulty breathing, loss of consciousness
3. **Medication Interactions**: Warfarin + Aspirin, Metformin + contrast dye
4. **Symptom Clusters**: ACS signs, sepsis indicators, DKA presentation
5. **Abnormal Values**: Lab values outside normal ranges
6. **Emergency Indicators**: Keywords suggesting urgent conditions

Each risk flag includes:
- Severity level (critical, high, medium, low)
- Clinical explanation
- Involved entities
- Recommended action

## 🔬 Summarization Models

The system supports multiple FLAN-T5 models:

- **`google/flan-t5-small`**: Fastest, ~77M parameters (good for Render free tier)
- **`google/flan-t5-base`**: Balanced, ~248M parameters (default)
- **`google/flan-t5-large`**: Better quality, ~783M parameters (requires more memory)

Fallback to rule-based extractive summarization if no model is available.

## 🧪 Testing

```bash
# Run all tests
pytest tests/

# Run specific test
pytest tests/test_components.py::TestOCRCleaner

# With coverage
pytest --cov=app tests/

# Integration test
python -c "from data.sample_data import get_sample_analysis_request; from app.core.pipeline import MedicalNLPPipeline; p = MedicalNLPPipeline(); r = p.process(get_sample_analysis_request()); print(r.summary_short)"
```

## 🌐 Deployment

### Local Development

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build
docker build -t helix-medical-nlp .

# Run
docker run -p 8000:8000 -e PORT=8000 helix-medical-nlp
```

### Render.com Deployment

1. **Connect Repository**: Push code to GitHub
2. **Create Web Service**:
   - Name: `helix-medical-nlp`
   - Environment: Python 3.11
   - Build command: `pip install -r requirements.txt`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
3. **Environment Variables**: Set via Render dashboard
4. **Disk**: Allocate 10GB for model cache

**Procfile** handles model download on deployment:
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
release: python -m spacy download en_core_sci_md || true
```

### Production Considerations

- **Model Caching**: Models are cached in `./checkpoints/`
- **Memory**: Minimum 2GB RAM recommended
- **GPU**: Optional, but improves inference speed
- **Concurrency**: Use appropriate worker count for your environment
- **Rate Limiting**: Enable in production via config
- **Monitoring**: Check logs in `./logs/`

## 🔮 Future Enhancements

### Phase 2
- [ ] Fine-tune entity extraction on proprietary medical data
- [ ] Add UMLS API integration for concept mapping
- [ ] Implement multi-language support
- [ ] Add drug interaction database (FDA/DrugBank)
- [ ] Real-time patient timeline visualization

### Phase 3
- [ ] Custom model training endpoint
- [ ] Batch processing for large document sets
- [ ] Electronic health record (EHR) system integration
- [ ] Patient outcome prediction models
- [ ] Quality metrics tracking and feedback loop

### Phase 4
- [ ] Real-time clinical decision support
- [ ] Integration with OCR systems (Tesseract, AWS Textract, Google Vision)
- [ ] Mobile app for clinical note entry
- [ ] Multi-modal analysis (text + images)

## 🔌 Integration Points

### Connecting to OCR Systems

The system is designed to work with any OCR provider:

```python
from app.core.pipeline import get_pipeline
from ocr_provider import extract_text_from_image  # Your OCR system

# Get OCR text
ocr_text = extract_text_from_image(image_file)

# Analyze
pipeline = get_pipeline()
response = pipeline.process(AnalysisRequest(
    ocr_text=ocr_text,
    patient_id=patient_id,
    # ... other fields
))

# Return to frontend
return response.dict()
```

### Supported OCR Backends
- Tesseract (open-source)
- AWS Textract
- Google Cloud Vision
- Azure Computer Vision
- Paddle OCR (multilingual)

### Connecting to EHR Systems

The system can integrate with hospital systems:

```python
# Load previous records from EHR
ehr_records = ehr_system.get_patient_history(patient_id)
previous_records = [
    MedicalRecord(
        record_id=r.id,
        date=r.created_at,
        document_type=r.type,
        raw_text=r.text
    )
    for r in ehr_records
]

# Pass to analysis
response = pipeline.process(AnalysisRequest(
    ocr_text=current_ocr,
    patient_id=patient_id,
    previous_records=previous_records
))

# Save results back to EHR
ehr_system.save_analysis(patient_id, response.dict())
```

## 📊 Performance Metrics

On a typical system:

| Operation | Time (ms) | Notes |
|-----------|-----------|-------|
| OCR Cleaning | 5-10 | Text preprocessing |
| Entity Extraction | 30-50 | Pattern matching + scispaCy |
| Summarization | 150-300 | Transformer inference |
| Full Pipeline | 200-400 | End-to-end processing |

Memory usage: ~1.5GB with base FLAN-T5 model

## 🛡️ Safety & Validation

The system includes several safety mechanisms:

1. **Confidence Thresholding**: Only reports entities above threshold
2. **Contradiction Detection**: Flags inconsistencies with history
3. **Hallucination Prevention**: Outputs only mentioned conditions
4. **Uncertainty Expression**: Uses "possible" vs "likely" appropriately
5. **Manual Review Flags**: Alerts for complex cases requiring verification

## 📝 Citation

If using this system in research:

```bibtex
@software{helix_medical_nlp_2024,
  title={HELIX Medical NLP Engine},
  author={HELIX Team},
  year={2024},
  url={https://github.com/yourusername/helix-medical-nlp}
}
```

## 📄 License

MIT License - See LICENSE file

## 🤝 Contributing

Contributions welcome! Please:

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 🆘 Support & Issues

- **Documentation**: See `/docs` endpoint on running server
- **Issues**: Report via GitHub Issues
- **Questions**: Check existing issues or ask in Discussions
- **Email**: support@helixhealth.com

## ⚖️ Medical Disclaimer

This tool is for research and clinical support purposes only. It is NOT intended for autonomous diagnosis or treatment decisions. Always consult qualified healthcare professionals for patient care decisions.

---

**Version**: 1.0.0  
**Last Updated**: March 2024  
**Status**: Production Ready
