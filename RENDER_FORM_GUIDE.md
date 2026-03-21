# Render Deployment Form - Exact Values to Fill In

## Screenshot 1: Root Directory, Build Command, Start Command

### 1. Root Directory
**Field:** Root Directory (Optional)
**What to fill in:** Leave EMPTY or enter: `.`
**Why:** Your app is at repo root, no subdirectory

---

### 2. Build Command
**Field:** Build Command
**Replace:** `$ pip install -r requirements.txt`
**With:** `pip install -r requirements.txt`
**Exact value:**
```
pip install -r requirements.txt
```
✅ Keep as is (already correct in placeholder)

---

### 3. Start Command
**Field:** Start Command
**Replace:** `$ gunicorn your_application.wsgi`
**With:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
**Exact value:**
```
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

---

## Screenshot 2: Environment Variables

### Add These 5 Environment Variables:

**Variable 1:**
```
NAME:  USE_SCISPACY
VALUE: false
```

**Variable 2:**
```
NAME:  SUMMARIZATION_MODEL
VALUE: default
```

**Variable 3:**
```
NAME:  LOG_LEVEL
VALUE: INFO
```

**Variable 4:**
```
NAME:  DEVICE
VALUE: cpu
```

**Variable 5:**
```
NAME:  DEBUG
VALUE: False
```

**How to add them:**
1. Click "+ Add Environment Variable" button
2. Enter NAME in left field
3. Enter VALUE in right field
4. Repeat for all 5 variables

---

## Screenshot 3: Health Check, Pre-Deploy, Auto-Deploy

### 1. Health Check Path
**Field:** Health Check Path
**Current value:** `/healthz`
**Change to:** `/api/v1/health`
**Exact value:**
```
/api/v1/health
```

---

### 2. Pre-Deploy Command
**Field:** Pre-Deploy Command (Optional)
**What to fill in:** Leave EMPTY
**Why:** No database migrations needed

---

### 3. Auto-Deploy
**Field:** Auto-Deploy
**Current value:** On Commit
**Keep as:** On Commit ✅
**Why:** Auto-deploys when you push to GitHub

---

## Complete Checklist

```
FORM FIELDS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Name:                  helix-medical-nlp
Environment:           Python 3
Region:                (choose your region)
Branch:                main
Root Directory:        (leave empty)

Build Command:         ✅ pip install -r requirements.txt
Start Command:         ✅ uvicorn app.main:app --host 0.0.0.0 --port $PORT

Health Check Path:     ✅ /api/v1/health
Pre-Deploy Command:    (leave empty)
Auto-Deploy:           ✅ On Commit

ENVIRONMENT VARIABLES (Add 5):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ USE_SCISPACY        = false
✅ SUMMARIZATION_MODEL = default
✅ LOG_LEVEL           = INFO
✅ DEVICE              = cpu
✅ DEBUG               = False

INSTANCE TYPE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Free tier           (start with this)
```

---

## What Each Setting Does

### Build Command
- Installs all 15 dependencies from requirements.txt
- This runs once before starting your app

### Start Command
- Starts FastAPI server on Render's port
- `$PORT` is automatically set by Render
- Makes app accessible on the internet

### Health Check Path
- Render pings `/api/v1/health` every 30 seconds
- If it fails 3 times, service restarts
- Our endpoint returns: `{"status": "healthy", "timestamp": "..."}`

### Environment Variables
- `USE_SCISPACY=false` → Use pattern-based extraction (no model download)
- `SUMMARIZATION_MODEL=default` → Use rule-based summarizer
- `LOG_LEVEL=INFO` → Standard logging
- `DEVICE=cpu` → Use CPU (Render doesn't have GPU)
- `DEBUG=False` → Production mode

### Auto-Deploy
- When you push to GitHub, Render automatically rebuilds and deploys
- Takes 2-5 minutes per deployment

---

## After Filling in the Form

1. **Click "Create Web Service"**
2. **Wait 2-5 minutes** for deployment
3. **Check status page** - will show "Live" when ready
4. **Copy your service URL** from the dashboard
5. **Test it:**
   ```
   curl https://YOUR_SERVICE_URL/api/v1/health
   ```
6. **View interactive API:**
   ```
   https://YOUR_SERVICE_URL/docs
   ```

---

## Testing After Deployment

### Health Check
```bash
curl https://your-service-url/api/v1/health
```
**Expected response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-03-22T15:30:00Z",
  "version": "1.0.0"
}
```

### Try the API
```bash
curl -X POST https://your-service-url/api/v1/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "patient_id": "P001",
    "ocr_text": "Patient has fever and cough. Taking aspirin 500mg"
  }'
```

### View API Documentation
Visit: `https://your-service-url/docs`
(Interactive Swagger UI)

---

## Troubleshooting

### If deployment fails:
1. Check Build Logs in Render dashboard
2. Make sure "Build Command" is exactly: `pip install -r requirements.txt`
3. Make sure "Start Command" is exactly: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### If health check fails:
1. Make sure Health Check Path is: `/api/v1/health`
2. Wait 5 minutes for app to fully start
3. Check application logs in Render dashboard

### If app restarts repeatedly:
1. Check "Health Check" section in Render dashboard
2. May need to increase timeout
3. Our health endpoint should respond in <100ms

---

## Summary: Copy-Paste Values

**Root Directory:** (empty)
**Build:** `pip install -r requirements.txt`
**Start:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
**Health:** `/api/v1/health`
**Env Vars:**
```
USE_SCISPACY=false
SUMMARIZATION_MODEL=default
LOG_LEVEL=INFO
DEVICE=cpu
DEBUG=False
```

That's it! Click Create and wait 2-5 minutes. ✅
