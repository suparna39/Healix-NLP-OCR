# QUICKSTART.md - Get HELIX Medical NLP Running in 5 Minutes

## Prerequisites

- Python 3.9+
- ~2GB RAM
- ~3GB disk space (for models)

## Installation & Setup

### Step 1: Clone and Setup

```bash
# Clone the repository
git clone <repo-url>
cd helix_medical_nlp

# Create virtual environment
python -m venv venv

# Activate
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Start the Server

```bash
# Run the API server
python -m uvicorn app.main:app --reload

# Output:
# Uvicorn running on http://127.0.0.1:8000
# Visit http://127.0.0.1:8000/docs for interactive API docs
```

### Step 3: Test the API

```bash
# In another terminal, test the health endpoint
curl http://localhost:8000/api/v1/health

# Response:
# {"status":"healthy","version":"1.0.0",...}
```

## Quick API Examples

### Example 1: Full Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "ocr_text": "Patient with diabetes presents with fever and cough. History of hypertension. Taking metformin.",
    "patient_id": "P12345"
  }'
```

### Example 2: Just Extraction

```bash
curl -X POST http://localhost:8000/api/v1/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient taking aspirin and lisinopril"
  }'
```

### Example 3: Just Summarization

```bash
curl -X POST http://localhost:8000/api/v1/summarize \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Patient with extensive history of... [long text]"
  }'
```

## Interactive Testing

Visit **http://localhost:8000/docs** for an interactive Swagger UI where you can:

1. Try all endpoints
2. See full request/response schemas
3. Test with different parameters
4. View documentation

## Running Examples

```bash
# Run the example scripts
cd examples
python quick_start.py

# Output will show:
# - Basic analysis
# - Analysis with patient history
# - Risk detection examples
# - Entity extraction
```

## Testing

```bash
# Run unit tests
pytest tests/

# Run specific test
pytest tests/test_components.py::TestOCRCleaner::test_remove_control_characters

# Run with coverage
pytest --cov=app tests/
```

## Common Issues

### Issue: "spacy model not found"
```bash
# Download scispaCy model
python -m spacy download en_core_sci_md
```

### Issue: "transformers not found"
```bash
# Models will be auto-downloaded on first use (~3GB)
# Or pre-download:
python -c "from transformers import AutoModelForSeq2SeqLM; AutoModelForSeq2SeqLM.from_pretrained('google/flan-t5-base')"
```

### Issue: Port 8000 already in use
```bash
# Run on different port
python -m uvicorn app.main:app --port 8080
```

## Next Steps

1. **Try Examples**: Run `examples/quick_start.py`
2. **Read API Docs**: Visit `/docs` endpoint
3. **Integrate OCR**: Connect your OCR system to `/api/v1/analyze`
4. **Connect EHR**: Load patient history in `previous_records`
5. **Deploy to Render**: See README.md deployment section

## API Response Structure

Every `/analyze` response includes:

```
{
  "entities": {...},           # Extracted medical concepts
  "summary_short": "...",      # 1-2 sentence summary
  "summary_long": "...",       # Full summary
  "risk_flags": [...],         # Detected risks/alerts
  "confidence": {...},         # Confidence scores
  "notes_for_doctor": [...],   # Actionable items
  "processing_time_ms": 250    # Performance metric
}
```

## Performance Benchmarks

On a typical laptop:

- **Minimal text** (~100 words): 100-150ms
- **Standard medical record** (~500 words): 200-350ms
- **Long document** (~2000 words): 400-600ms

## Next: Production Deployment

When ready to deploy to production:

1. Set `DEBUG=False` in .env
2. Use appropriate worker count
3. Enable rate limiting
4. Set up monitoring/logging
5. Deploy to Render or your infrastructure

See README.md for detailed deployment instructions.

---

🎉 **You're all set!** Medical NLP is now running locally.
