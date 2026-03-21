#!/usr/bin/env python3
import sys, os
os.environ['USE_SCISPACY'] = 'false'
os.environ['SUMMARIZATION_MODEL'] = 'default'
sys.path.insert(0, '.')

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

print("Testing API...")
print("=" * 60)

# Test 1: Root
resp = client.get("/")
assert resp.status_code == 200
print("[OK] GET / - Root")

# Test 2: Health
resp = client.get("/api/v1/health")
assert resp.status_code == 200
print("[OK] GET /api/v1/health - Health")

# Test 3: Extract
resp = client.post("/api/v1/extract", json={"text": "Cough and fever. Paracetamol 500mg."})
assert resp.status_code == 200
print("[OK] POST /api/v1/extract - Extract")

# Test 4: Summarize
resp = client.post("/api/v1/summarize", json={"text": "Patient with fever and cough"})
assert resp.status_code == 200
print("[OK] POST /api/v1/summarize - Summarize")

# Test 5: Analyze
resp = client.post("/api/v1/analyze", json={
    "ocr_text": "Patient John, 45M. Cough with fever. Amoxycillin 500mg.",
    "patient_id": "TEST-001",
    "age": 45,
    "sex": "M"
})
assert resp.status_code == 200
data = resp.json()
print(f"[OK] POST /api/v1/analyze - Analyze ({data['processing_time_ms']:.0f}ms)")

# Test 6: Models
resp = client.get("/api/v1/models")
assert resp.status_code == 200
print("[OK] GET /api/v1/models - Models")

print("=" * 60)
print("SUCCESS: All endpoints working!")
