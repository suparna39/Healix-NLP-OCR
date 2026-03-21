# RUN THE SYSTEM - Step by Step Guide

## 🚀 Option 1: Quick Test (No Server Needed)

Run the test script to verify everything works:

```bash
cd C:\Healix-2\helix_medical_nlp
python test_system.py
```

This will:
- ✅ Test OCR text cleaning
- ✅ Test entity extraction
- ✅ Test term normalization
- ✅ Test risk detection
- ✅ Run full pipeline

**Expected output**: Green checkmarks and test results

---

## 🌐 Option 2: Run the API Server

Start the FastAPI server:

```bash
cd C:\Healix-2\helix_medical_nlp
python -m uvicorn app.main:app --reload
```

Then visit: **http://localhost:8000/docs**

You can:
- 🔍 See all API endpoints
- 📝 Try each endpoint
- 📋 See request/response schemas
- 🧪 Test with your own data

---

## 📸 Option 3: Process an Image (With OCR)

### Step 1: Install OCR
```bash
pip install pytesseract
# Windows: Download Tesseract from https://github.com/UB-Mannheim/tesseract/wiki
# Mac: brew install tesseract
# Linux: apt-get install tesseract-ocr
```

### Step 2: Create a test script
```python
import pytesseract
from PIL import Image
import requests

# Extract text from image
image = Image.open("your_medical_scan.png")
ocr_text = pytesseract.image_to_string(image)

# Send to HELIX
response = requests.post(
    "http://localhost:8000/api/v1/analyze",
    json={
        "ocr_text": ocr_text,
        "patient_id": "P123"
    }
)

# Show results
result = response.json()
print(f"Summary: {result['summary_short']}")
print(f"Diseases: {[d['normalized'] for d in result['entities']['diseases']]}")
```

---

## 📊 Option 4: Use Sample Data

Run the examples script:

```bash
cd C:\Healix-2\helix_medical_nlp\examples
python quick_start.py
```

This runs 4 complete examples showing:
- Basic analysis
- Analysis with patient history
- Risk detection
- Entity extraction

---

## ✅ Verify Installation

Check if everything is installed:

```bash
python -c "import fastapi; import pydantic; import transformers; print('✅ All dependencies installed!')"
```

If you get errors, install dependencies:

```bash
pip install -r requirements.txt
```

---

## 🎯 What You Can Do

### 1. Test with Text
```bash
curl -X POST http://localhost:8000/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{"ocr_text": "Patient with diabetes takes metformin", "patient_id": "P001"}'
```

### 2. Process Your Medical Document
- Scan a medical document as PNG/JPG
- Extract text using Tesseract or AWS Textract
- Send to HELIX API
- Get structured analysis

### 3. Batch Process Multiple Documents
```python
from pathlib import Path
import requests

for image_file in Path("medical_scans/").glob("*.png"):
    # Extract text
    ocr_text = extract_ocr(image_file)
    # Analyze
    response = requests.post(
        "http://localhost:8000/api/v1/analyze",
        json={"ocr_text": ocr_text, "patient_id": image_file.stem}
    )
    # Save result
    with open(f"results/{image_file.stem}.json", "w") as f:
        json.dump(response.json(), f)
```

---

## 📚 Next: Read Documentation

After running tests, read:

1. **QUICKSTART.md** - 5-minute guide
2. **README.md** - Complete documentation
3. **OCR_INTEGRATION_GUIDE.md** - Integrate your OCR system
4. **USER_GUIDE.md** - Usage examples

---

## 🆘 Troubleshooting

**Problem**: "Module not found"
```bash
pip install -r requirements.txt
```

**Problem**: Port 8000 in use
```bash
python -m uvicorn app.main:app --port 8080
```

**Problem**: Models downloading (first run is slow)
- Wait for models to download (~3GB)
- Check internet connection
- Ensure 10GB disk space available

---

## ✨ You're Ready!

Choose an option above and run it on your machine to test the HELIX Medical NLP system!
