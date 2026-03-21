# ARCHITECTURE.md - System Design and Technical Details

## System Overview

HELIX Medical NLP is a multi-stage pipeline that transforms raw OCR text into structured, actionable medical intelligence.

```
┌─────────────────┐
│  OCR Document   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  Text Cleaning          │  - Remove control chars
│  (OCRTextCleaner)       │  - Normalize whitespace
│                         │  - Standardize abbreviations
└────────┬────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Entity Extraction       │  - scispaCy NER
│  (MedicalEntityExtractor)│  - Pattern matching
│                          │  - Confidence scoring
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Term Normalization      │  - UMLS-style mapping
│  (MedicalTermNormalizer) │  - Synonym resolution
│                          │  - Definition lookup
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Context Integration     │  - Load patient history
│  (ContextMerger)         │  - Deduplicate entities
│                          │  - Identify contradictions
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Summarization           │  - FLAN-T5 inference
│  (MedicalSummarizer)     │  - Hierarchical chunking
│                          │  - Multiple summary types
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Risk Detection          │  - Critical condition flags
│  (RiskDetector)          │  - Drug interaction checks
│                          │  - Symptom cluster analysis
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Confidence Scoring      │  - Entity extraction quality
│  (ConfidenceScorer)      │  - Summarization quality
│                          │  - Overall system confidence
└────────┬─────────────────┘
         │
         ▼
┌──────────────────────────┐
│  Response Generation     │  - JSON formatting
│  (MedicalNLPPipeline)    │  - Doctor notes
│                          │  - Alerts/warnings
└──────────────────────────┘
```

## Component Details

### 1. Text Cleaning (OCRTextCleaner)

**Purpose**: Prepare OCR output for NLP processing

**Operations**:
- **Control Character Removal**: Strip Unicode control characters
- **Whitespace Normalization**: Collapse multiple spaces, fix line breaks
- **Duplicate Line Removal**: Remove repetitive lines from OCR
- **Header/Footer Removal**: Eliminate page numbers, headers
- **Abbreviation Expansion**: Convert medical abbreviations to full forms
  - `BP` → `blood pressure`
  - `DM` → `diabetes mellitus`
  - `SOB` → `shortness of breath`

**Input**: Raw OCR text (may contain artifacts)
**Output**: Clean, normalized text

**Key Methods**:
```python
cleaner = OCRTextCleaner()
cleaned_text = cleaner.clean(raw_ocr_text)
```

### 2. Entity Extraction (MedicalEntityExtractor)

**Purpose**: Identify and extract medical concepts

**Architecture**:
1. **Primary NER** (Optional): scispaCy biomedical model
   - Trained on biomedical literature
   - Recognizes diseases, drugs, procedures, etc.
   - ~85% confidence

2. **Secondary Extraction**: Pattern-based regex matching
   - 100+ disease patterns
   - 50+ symptom patterns
   - 40+ medication patterns
   - 30+ procedure patterns
   - 20+ test patterns
   - Measurement patterns
   - ~75% confidence

**Entity Types**:
- DISEASE: Medical conditions and diagnoses
- SYMPTOM: Signs and symptoms
- MEDICATION: Drugs and treatments
- TEST: Diagnostic tests and procedures
- PROCEDURE: Medical procedures
- MEASUREMENT: Lab values and vital signs
- ANATOMY: Anatomical structures

**Conflict Resolution**:
- Overlapping entities: Keep highest confidence
- Deduplication: Remove duplicates after scoring

**Input**: Cleaned text
**Output**: List of MedicalEntity objects with positions, confidence, explanations

### 3. Term Normalization (MedicalTermNormalizer)

**Purpose**: Map variant terms to standard medical terminology

**Normalization Database**:
- **100+ disease** normalizations
- **50+ symptom** normalizations
- **70+ medication** normalizations
- **30+ test** normalizations
- **20+ procedure** normalizations

**Example Mappings**:
```
"dm" → "Diabetes Mellitus"
"high BP" → "Hypertension"
"heart attack" → "Myocardial Infarction"
"pneumonia" → "Pneumonia"
```

**Features**:
- Direct term matching
- Alias/synonym matching
- Partial matching for flexibility
- Definition lookup
- Synonym retrieval

**Input**: Extracted entities with original text
**Output**: Normalized medical terms with definitions

### 4. Context Integration (ContextMerger)

**Purpose**: Integrate current findings with patient history

**Operations**:
1. **History Loading**: Retrieve previous medical records
2. **Chronological Sorting**: Organize by date
3. **Time Window Filtering**: Focus on relevant history (default: 365 days)
4. **Entity Deduplication**: Remove repeated findings
5. **Contradiction Detection**: Flag conflicting information
6. **Timeline Building**: Generate patient history narrative
7. **Trend Analysis**: Identify patterns in medical history

**Contradiction Rules**:
- Same disease: Usually continuation
- Different medication: Possible change (note it)
- Conflicting test values: Flag for review
- Disease resolution: Positive change

**Output**:
- Merged text with both current and historical context
- Integration summary (e.g., "New acute event vs stable baseline")
- Deduplicated entity list

### 5. Summarization (MedicalSummarizer)

**Purpose**: Generate doctor-friendly clinical summaries

**Models**:
- **Primary**: google/flan-t5-base (248M parameters)
- **Fallback**: Rule-based extractive summarization

**Summary Types**:
1. **Short Summary** (80 tokens)
   - 1-2 sentences
   - Key findings only
   - Use case: EMR display

2. **Long Summary** (150-200 tokens)
   - Full clinical context
   - Patient demographics
   - Relevant history
   - Assessment and plan
   - Use case: Detailed review

3. **Key Findings** (100 tokens)
   - Abnormal results only
   - Critical findings highlighted
   - Use case: Alert summary

**Hierarchical Summarization** (for long documents):
```
Long Document (>2000 chars)
    ↓
Split into 500-char chunks
    ↓
Summarize each chunk (~100 tokens)
    ↓
Combine summaries
    ↓
Final summarization (~150 tokens)
```

**Input**: Cleaned text (optionally merged with history)
**Output**: Multiple summary types as strings

### 6. Risk Detection (RiskDetector)

**Purpose**: Identify medical risks and generate clinical alerts

**Risk Categories**:

#### A. Critical Conditions
- Stroke, MI, sepsis, cardiac arrest, respiratory failure
- **Severity**: CRITICAL
- **Action**: Immediate intervention

#### B. Critical Symptoms
- Chest pain, difficulty breathing, loss of consciousness
- **Severity**: CRITICAL
- **Action**: Emergency evaluation

#### C. Medication Interactions
- Knowledge base of 15+ known interactions
- Examples:
  - Warfarin + Aspirin → Bleeding risk
  - Metformin + Contrast dye → Lactic acidosis
  - ACE inhibitor + Potassium → Hyperkalemia
- **Severity**: HIGH
- **Action**: Pharmacist consultation

#### D. Symptom Clusters
- Multiple symptoms suggesting specific conditions:
  - ACS: chest pain + SOB + nausea + diaphoresis
  - Sepsis: fever + tachycardia + hypotension + altered mental status
  - DKA: nausea + vomiting + abdominal pain + dyspnea
- **Severity**: HIGH or CRITICAL
- **Action**: Further evaluation

#### E. Abnormal Values
- Lab values outside normal ranges
- Example: Glucose >200, Hemoglobin <10
- **Severity**: MEDIUM
- **Action**: Verify and monitor

#### F. Emergency Indicators
- Keywords: "emergency", "acute", "severe", "urgent"
- **Severity**: CRITICAL
- **Action**: Treat as emergency

**Output**: RiskFlag objects with:
- Flag type
- Severity level
- Description
- Clinical explanation
- Involved entities
- Recommended action

### 7. Confidence Scoring (ConfidenceScorer)

**Purpose**: Quantify uncertainty and system reliability

**Metrics**:

#### A. Entity Extraction Confidence (0-1)
```
score = (avg_entity_confidence × 0.7) + (text_length_factor × 0.3)
- Based on model confidence scores
- Adjusted for text length
- Range: 0.2 to 0.95
```

#### B. Summarization Confidence (0-1)
```
score = (compression_ratio_quality × 0.6) + (keyword_presence × 0.4)
- Optimal compression: 25-30% of original
- Presence of medical keywords
- Range: 0.2 to 0.95
```

#### C. Context Understanding (0-1)
```
score = (history_coverage × 0.5) + (integration_quality × 0.5)
- How much history was available
- Quality of integration summary
- Range: 0.3 to 0.95
```

#### D. Overall Confidence (0-1)
```
overall = (entity × 0.4) + (summarization × 0.4) + (context × 0.2)
- Weighted average of components
```

**Interpretations**:
- `0.85+`: High confidence, reliable
- `0.70-0.84`: Moderate confidence, review recommended
- `0.50-0.69`: Low confidence, manual review required
- `<0.50`: Very low, not suitable for autonomous decisions

### 8. Response Generation (MedicalNLPPipeline)

**Purpose**: Orchestrate all components and produce final output

**Pipeline Execution**:
```python
def process(request: AnalysisRequest) -> AnalysisResponse:
    1. Clean text
    2. Extract entities
    3. Merge with history
    4. Summarize
    5. Detect risks
    6. Calculate confidence
    7. Generate doctor notes
    8. Build response JSON
```

**Final Response Fields**:
```json
{
  "patient_id": "...",
  "entities": {
    "diseases": [...],
    "symptoms": [...],
    "medications": [...],
    "tests": [...],
    "procedures": [...],
    "measurements": [...],
    "anatomy": [...]
  },
  "normalized_terms": {...},
  "summary_short": "...",
  "summary_long": "...",
  "history_integration": "...",
  "risk_flags": [...],
  "confidence": {...},
  "notes_for_doctor": [...],
  "warnings": [...],
  "processing_time_ms": 250,
  "model_versions": {...}
}
```

## API Layer (FastAPI)

**Endpoints**:
- `POST /api/v1/analyze` - Full pipeline
- `POST /api/v1/summarize` - Summarization only
- `POST /api/v1/extract` - Entity extraction only
- `GET /api/v1/health` - Health check
- `GET /api/v1/models` - Model information

**Request/Response Validation**: Pydantic schemas ensure data quality

**Error Handling**: Try-except blocks with detailed logging

**CORS**: Enabled for cross-origin requests (configure for production)

## Model Architecture

### Entity Extraction Models

**scispaCy (Primary)**:
- Base: spaCy 3.x
- Training: PubMed + PMC biomedical literature
- Models:
  - `en_core_sci_sm` (33MB): Fast, resource-light
  - `en_core_sci_md` (115MB): Balanced (default)
  - `en_core_sci_lg` (354MB): Highest accuracy
- Performance: 85-90% F1 on biomedical NER

**Pattern Matching (Secondary)**:
- 300+ regex patterns
- Medical terminology database
- Fallback when scispaCy unavailable

### Summarization Models

**FLAN-T5 Family**:
- Base model: T5-based instruction-following
- Fine-tuned for 200+ NLP tasks
- Architecture: Encoder-Decoder transformer
- Quantization: Optional INT8 for memory efficiency

**Variants**:
- `flan-t5-small`: 80M params (~500MB)
- `flan-t5-base`: 248M params (~1.4GB) - **DEFAULT**
- `flan-t5-large`: 783M params (~3.7GB)

**Inference**:
- Batch size: 1-32 (adjustable)
- Device: CPU (default) or CUDA GPU
- Max input: 1024 tokens
- Generation: Beam search (beam_size=4)

## Data Models (Pydantic)

**MedicalEntity**:
- text: Original extracted text
- entity_type: disease, symptom, medication, etc.
- normalized: Standardized term
- confidence: 0-1 score
- start_pos, end_pos: Character positions
- explanation: Why it was extracted
- synonyms: Alternative names
- cui: UMLS Concept ID (optional)

**AnalysisRequest**:
- ocr_text: Raw OCR document
- patient_id: Patient identifier
- age, sex: Demographics
- source_type: Document type
- known_conditions: Pre-existing conditions
- previous_records: Historical records list

**AnalysisResponse**:
- All extracted information
- Summaries and integrations
- Risk flags and alerts
- Confidence scores
- Doctor notes and warnings
- Processing metrics

## Performance Considerations

### Memory Usage
- Model loading: ~1.5GB (FLAN-T5 base)
- Text buffer: ~10MB (typical document)
- Pipeline cache: ~500MB (sliding window)
- **Total**: ~2GB typical, ~3GB peak

### Latency
- Text cleaning: 5-10ms
- Entity extraction: 30-50ms
- Summarization: 150-300ms
- **Total**: 200-400ms for typical documents

### Optimization Strategies
1. **Model Quantization**: INT8 for 25% smaller models
2. **Batch Processing**: Group requests when possible
3. **Caching**: Cache model outputs for identical inputs
4. **Lazy Loading**: Load models on first use only
5. **GPU Acceleration**: CUDA support for 3-5x speedup

## Security & Privacy

**Data Handling**:
- No data persistence (stateless)
- Models run locally (no cloud calls)
- Optional HIPAA compliance configuration
- Audit logging available

**Input Validation**:
- Text length limits
- Character validation
- SQL injection prevention
- Command injection prevention

**Output Filtering**:
- Confidence thresholding
- Hallucination prevention
- Uncertainty expression

## Future Extensibility

### Pluggable Components
```python
# Easy to swap models
class MedicalSummarizer:
    def __init__(self, model_name="custom-model"):
        self.model = load_model(model_name)
```

### Custom Entity Types
```python
# Add new entity types
ENTITY_TYPES = {
    "DISEASE": "disease",
    "CUSTOM_TYPE": "custom",  # New!
}
```

### Integration Points
- OCR systems (Tesseract, AWS, Google, Azure)
- EHR systems (HL7 FHIR, proprietary APIs)
- Knowledge bases (UMLS, DrugBank, UpToDate)
- Feedback loops (user corrections, ground truth)

## Testing Strategy

**Unit Tests**:
- Component testing (each module)
- Edge case coverage
- Error handling

**Integration Tests**:
- End-to-end pipeline
- With sample data
- Performance benchmarking

**Performance Tests**:
- Latency measurement
- Memory profiling
- Batch processing

**Validation Tests**:
- Against medical ground truth
- Comparison with expert annotations
- Confidence calibration

---

**Version**: 1.0.0
**Last Updated**: March 2024
**Complexity**: Production-Grade Multi-Stage NLP Pipeline
