# Troubleshooting Guide - Multimodal Integration

## Overview

This guide provides solutions to common issues encountered during and after multimodal integration deployment.

---

## Table of Contents

1. [Import Errors](#import-errors)
2. [Database Errors](#database-errors)
3. [Task Registration Issues](#task-registration-issues)
4. [Processing Failures](#processing-failures)
5. [Performance Issues](#performance-issues)
6. [Data Quality Issues](#data-quality-issues)
7. [API Response Issues](#api-response-issues)
8. [Dependency Issues](#dependency-issues)

---

## Import Errors

### Error: `ModuleNotFoundError: No module named 'visual_analysis'`

**Symptoms:**
```
[ERROR] Task 4 failed: ModuleNotFoundError: No module named 'visual_analysis'
```

**Cause:** visual_analysis.py file not present in backend directory

**Solution:**

```bash
# Check if file exists
docker-compose exec backend ls -lh /app/visual_analysis.py

# If missing, copy from Week 1 deliverable
cp /path/to/week1/visual_analysis.py backend/

# Copy to container
docker cp backend/visual_analysis.py promo_analyzer_backend:/app/

# Restart Celery worker
docker-compose restart celery_worker

# Verify import works
docker-compose exec backend python -c "from visual_analysis import VisualAnalysisEngine; print('✅ Import successful')"
```

---

### Error: `ModuleNotFoundError: No module named 'vocal_analysis'`

**Symptoms:**
```
[ERROR] Task 5 failed: ModuleNotFoundError: No module named 'vocal_analysis'
```

**Cause:** vocal_analysis.py file not present in backend directory

**Solution:**

```bash
# Check if file exists
docker-compose exec backend ls -lh /app/vocal_analysis.py

# If missing, copy from Week 2 deliverable
cp /path/to/week2/vocal_analysis.py backend/

# Copy to container
docker cp backend/vocal_analysis.py promo_analyzer_backend:/app/

# Restart Celery worker
docker-compose restart celery_worker

# Verify import works
docker-compose exec backend python -c "from vocal_analysis import VocalAnalysisEngine; print('✅ Import successful')"
```

---

### Error: `ModuleNotFoundError: No module named 'multimodal_integration_engine'`

**Symptoms:**
```
[ERROR] Task 6 failed: ModuleNotFoundError: No module named 'multimodal_integration_engine'
```

**Cause:** multimodal_integration_engine.py file not present in backend directory

**Solution:**

```bash
# Check if file exists
docker-compose exec backend ls -lh /app/multimodal_integration_engine.py

# If missing, copy from Week 3 deliverable
cp /path/to/week3/multimodal_integration_engine.py backend/

# Copy to container
docker cp backend/multimodal_integration_engine.py promo_analyzer_backend:/app/

# Restart Celery worker
docker-compose restart celery_worker

# Verify import works
docker-compose exec backend python -c "from multimodal_integration_engine import MultiModalIntegrationEngine; print('✅ Import successful')"
```

---

### Error: `ImportError: cannot import name 'ComprehensiveAnalysis'`

**Symptoms:**
```
[ERROR] ImportError: cannot import name 'ComprehensiveAnalysis' from 'multimodal_integration_engine'
```

**Cause:** multimodal_integration_engine.py missing ComprehensiveAnalysis class

**Solution:**

Ensure multimodal_integration_engine.py contains:

```python
class ComprehensiveAnalysis:
    def __init__(self, ...):
        # Implementation

    def to_dict(self):
        # Implementation
```

If missing, update file from Week 3 deliverable.

---

## Database Errors

### Error: `column "visual_analysis" does not exist`

**Symptoms:**
```
[ERROR] sqlalchemy.exc.ProgrammingError: column "visual_analysis" of relation "videos" does not exist
```

**Cause:** Database migration not applied

**Solution:**

```bash
# Apply migration
docker cp migrations/001_add_multimodal_fields.sql \
  promo_analyzer_postgres:/tmp/migration.sql

docker-compose exec postgres psql -U promo_admin -d promo_analyzer \
  -f /tmp/migration.sql

# Verify columns exist
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ videos"

# Restart services
docker-compose restart backend celery_worker
```

---

### Error: `column "congruence_score" does not exist`

**Symptoms:**
```
[ERROR] sqlalchemy.exc.ProgrammingError: column "congruence_score" of relation "analyses" does not exist
```

**Cause:** Database migration not applied to analyses table

**Solution:**

Same as above - apply migration script. The migration adds columns to both `videos` and `analyses` tables.

---

### Error: `new row for relation "analyses" violates check constraint "check_valid_grades"`

**Symptoms:**
```
[ERROR] psycopg2.errors.CheckViolation: new row for relation "analyses" violates check constraint "check_valid_grades"
DETAIL: Failing row contains (..., character_grade=G, ...)
```

**Cause:** Code attempting to assign invalid grade (not A-F scale)

**Solution:**

Fix code to only assign valid grades:
- Valid: 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', NULL
- Invalid: 'G', 'E', 'A+', etc.

Check `multimodal_integration_engine.py` grade assignment logic.

---

## Task Registration Issues

### Error: Celery task not found: `tasks.analyze_visual`

**Symptoms:**
```
[ERROR] Received unregistered task of type 'tasks.analyze_visual'
```

**Cause:** Task not registered in Celery worker

**Solution:**

```bash
# Restart Celery worker
docker-compose restart celery_worker

# Wait for startup
sleep 10

# Verify tasks registered
docker-compose exec celery_worker celery -A tasks inspect registered

# Should show:
# - tasks.analyze_visual
# - tasks.analyze_vocal
# - tasks.analyze_comprehensive
```

If tasks still not registered:

```bash
# Check tasks.py for syntax errors
docker-compose exec backend python -m py_compile /app/tasks.py

# Check Celery logs for import errors
docker-compose logs celery_worker | grep -i "error\|import"
```

---

### Error: Task never starts (stuck in pending)

**Symptoms:**
- Video status stays "processing"
- Celery logs show no activity
- Task chain appears broken

**Cause:** Celery worker not running or task routing issue

**Solution:**

```bash
# Check Celery worker running
docker-compose ps celery_worker
# Should show "Up"

# If down, start it
docker-compose up -d celery_worker

# Check Redis connection
docker-compose exec backend python -c "import redis; r = redis.Redis(host='redis'); r.ping(); print('✅ Redis OK')"

# Check task queue
docker-compose exec celery_worker celery -A tasks inspect active

# Check task reserved
docker-compose exec celery_worker celery -A tasks inspect reserved
```

---

## Processing Failures

### Error: Task 4 (Visual Analysis) fails with MediaPipe error

**Symptoms:**
```
[ERROR] MediaPipe failed to initialize
[ERROR] FaceDetector initialization failed
```

**Cause:** MediaPipe dependencies not installed or GPU access issue

**Solution:**

```bash
# Install/reinstall MediaPipe
docker-compose exec backend pip install --force-reinstall mediapipe==0.10.8

# Check OpenCV installation
docker-compose exec backend python -c "import cv2; print(cv2.__version__)"

# If OpenCV missing
docker-compose exec backend pip install opencv-python==4.8.1.78

# Test MediaPipe
docker-compose exec backend python -c "
import mediapipe as mp
face_detection = mp.solutions.face_detection.FaceDetection()
print('✅ MediaPipe working')
"

# Restart Celery worker
docker-compose restart celery_worker
```

---

### Error: Task 5 (Vocal Analysis) fails with Librosa error

**Symptoms:**
```
[ERROR] librosa.load() failed
[ERROR] soundfile.SoundFileError: Error opening file
```

**Cause:** Audio file corrupted or Librosa dependencies missing

**Solution:**

```bash
# Install/reinstall Librosa
docker-compose exec backend pip install --force-reinstall librosa==0.10.1 soundfile==0.12.1

# Test Librosa
docker-compose exec backend python -c "
import librosa
import soundfile
print('✅ Librosa working')
"

# Check audio file exists
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT id, audio_path FROM videos WHERE status = 'processing' LIMIT 5;"

# Verify audio file readable
docker-compose exec backend ls -lh /path/to/audio.wav

# Restart Celery worker
docker-compose restart celery_worker
```

---

### Error: Task 6 (Comprehensive) fails with empty data

**Symptoms:**
```
[ERROR] Cannot analyze: visual_data is empty
[ERROR] Cannot analyze: vocal_data is empty
```

**Cause:** Tasks 4 and 5 failed to save data to database

**Solution:**

```bash
# Check if visual/vocal data was saved
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     id,
     visual_analysis IS NOT NULL AND jsonb_array_length(visual_analysis) > 0 as has_visual,
     vocal_analysis IS NOT NULL AND jsonb_array_length(vocal_analysis) > 0 as has_vocal
   FROM videos
   WHERE status = 'processing'
   LIMIT 5;"

# If has_visual or has_vocal is false, check logs for Task 4/5 failures
docker-compose logs celery_worker | grep -A 20 "TASK 4\|TASK 5"

# Re-process video from scratch
# (delete and re-upload)
```

---

### Error: Task 7 (Jake Analysis) timeout

**Symptoms:**
```
[ERROR] Task tasks.analyze_with_jake[...] exceeded time limit (1800s)
```

**Cause:** Claude API slow or network issue

**Solution:**

```bash
# Check Claude API key configured
docker-compose exec backend python -c "
from config import settings
assert settings.ANTHROPIC_API_KEY, 'API key missing'
print('✅ API key configured')
"

# Test Claude API connectivity
docker-compose exec backend python -c "
from anthropic import Anthropic
client = Anthropic()
response = client.messages.create(
    model='claude-3-sonnet-20240229',
    max_tokens=100,
    messages=[{'role': 'user', 'content': 'test'}]
)
print('✅ Claude API working')
"

# Increase timeout in tasks.py if needed
# Change task_time_limit from 1800 to 3600

# Check network connectivity
docker-compose exec backend ping -c 3 api.anthropic.com
```

---

## Performance Issues

### Issue: Processing takes > 5 minutes

**Symptoms:**
- Total processing time exceeds 300 seconds
- Users complaining of slow analysis

**Diagnosis:**

```bash
# Check processing times per task
docker-compose logs celery_worker | grep "complete" | tail -20

# Check database processing times
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     video_id,
     processing_time / 1000 as seconds,
     created_at
   FROM analyses
   ORDER BY processing_time DESC
   LIMIT 10;"
```

**Solutions:**

1. **If Transcription slow (>60s):**
   ```bash
   # Use smaller Whisper model
   # In config.py: WHISPER_MODEL = "tiny" instead of "base"
   ```

2. **If Visual Analysis slow (>30s):**
   ```bash
   # Reduce frame sampling rate
   # In analyze_visual task: sample_rate=1.0 instead of 2.0
   ```

3. **If Vocal Analysis slow (>20s):**
   ```bash
   # Increase segment duration
   # In analyze_vocal task: segment_duration=3.0 instead of 2.0
   ```

4. **If Claude API slow (>40s):**
   ```bash
   # Check API rate limits
   # Consider caching responses for testing
   # Use shorter prompts
   ```

---

### Issue: High CPU usage

**Symptoms:**
- CPU at 100%
- System becoming unresponsive

**Solution:**

```bash
# Check which process using CPU
docker stats

# Limit Celery worker concurrency
# In docker-compose.yml:
# celery_worker:
#   command: celery -A tasks worker --concurrency=2

# Or set in tasks.py:
# celery_app.conf.worker_concurrency = 2

# Restart services
docker-compose restart celery_worker
```

---

### Issue: High memory usage

**Symptoms:**
- Memory at 90%+
- OOM (Out of Memory) errors

**Solution:**

```bash
# Check memory usage
docker stats

# Limit memory per container
# In docker-compose.yml:
# celery_worker:
#   mem_limit: 2g

# Reduce batch sizes in analysis
# Process shorter video segments

# Restart services
docker-compose restart celery_worker
```

---

## Data Quality Issues

### Issue: Visual insights scores always 0

**Symptoms:**
```json
{
  "visual_insights": {
    "conviction_score": 0,
    "intensity_score": 0,
    ...
  }
}
```

**Cause:** Visual analysis not detecting faces or returning empty results

**Diagnosis:**

```bash
# Check visual_analysis data
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.visual_analysis | length'

# If 0, no frames were analyzed
```

**Solution:**

1. **Check video has visible faces:**
   - View video to ensure faces are visible
   - Check video resolution (should be > 480p)

2. **Test visual analysis manually:**
   ```bash
   docker-compose exec backend python -c "
   from visual_analysis import VisualAnalysisEngine
   engine = VisualAnalysisEngine()
   results = engine.analyze_video('/path/to/video.mp4', sample_rate=1.0)
   print(f'Frames analyzed: {len(results[0])}')
   "
   ```

3. **Check MediaPipe configuration:**
   - Ensure min_detection_confidence is not too high
   - Lower threshold if needed

---

### Issue: Vocal insights scores always 0

**Symptoms:**
```json
{
  "vocal_insights": {
    "vocal_conviction_score": 0,
    "vocal_intensity_score": 0,
    ...
  }
}
```

**Cause:** Vocal analysis not processing audio or returning empty results

**Diagnosis:**

```bash
# Check vocal_analysis data
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.vocal_analysis | length'

# If 0, no segments were analyzed
```

**Solution:**

1. **Check audio was extracted:**
   ```bash
   docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
     "SELECT id, audio_path FROM videos WHERE id = '$VIDEO_ID';"
   ```

2. **Verify audio file exists:**
   ```bash
   docker-compose exec backend ls -lh /path/to/audio.wav
   ```

3. **Test vocal analysis manually:**
   ```bash
   docker-compose exec backend python -c "
   from vocal_analysis import VocalAnalysisEngine
   engine = VocalAnalysisEngine()
   results = engine.analyze_audio('/path/to/audio.wav', segment_duration=2.0)
   print(f'Segments analyzed: {len(results[0])}')
   "
   ```

---

### Issue: Comprehensive scores all the same

**Symptoms:**
All congruence, authenticity, intensity, impact scores are identical (e.g., all 75.0)

**Cause:** Multimodal integration using default/fallback scoring

**Solution:**

Check multimodal_integration_engine.py implementation:
- Ensure it's calculating scores from actual data
- Not returning hardcoded defaults
- Properly weighting visual, vocal, linguistic signals

---

### Issue: Grades always NULL

**Symptoms:**
```json
{
  "character_grade": null,
  "delivery_grade": null,
  "psychology_grade": null
}
```

**Cause:** Grade assignment logic not triggered or returning None

**Diagnosis:**

```bash
# Check comprehensive_data for grade fields
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | \
  jq '.analyses[0].comprehensive_data | {character_grade, delivery_grade, psychology_grade}'
```

**Solution:**

1. Grades may be intentionally NULL for:
   - Very short videos (< 15 seconds)
   - Insufficient data
   - Low quality video/audio

2. If scores are good but grades NULL:
   - Check `multimodal_integration_engine.py` grade assignment logic
   - Ensure it maps scores to grades correctly
   - Verify ComprehensiveAnalysis.character_grade is set

---

## API Response Issues

### Issue: API returns 500 error after integration

**Symptoms:**
```
HTTP 500 Internal Server Error
```

**Diagnosis:**

```bash
# Check backend logs
docker-compose logs backend | tail -50

# Look for:
# - Database connection errors
# - Serialization errors
# - Missing field errors
```

**Common causes:**

1. **Pydantic validation error:**
   - schemas.py field types don't match database
   - Solution: Fix schema definitions

2. **Database field mismatch:**
   - models.py doesn't match actual schema
   - Solution: Check `\d+ videos` and `\d+ analyses`

3. **JSON serialization error:**
   - DECIMAL fields not serializing
   - Solution: Add Config class with `json_encoders`

---

### Issue: New fields missing from API response

**Symptoms:**
API doesn't return visual_insights, vocal_insights, or comprehensive scores

**Cause:** schemas.py not updated or build_video_detail_response() not using new fields

**Solution:**

1. **Verify schemas.py updated:**
   ```bash
   grep -n "visual_insights" backend/schemas.py
   grep -n "congruence_score" backend/schemas.py
   ```

2. **Check helper function:**
   ```bash
   grep -A 30 "def build_video_detail_response" backend/schemas.py
   ```

   Should include:
   ```python
   visual_insights = VisualInsights(**video.visual_insights) if video.visual_insights else None
   vocal_insights = VocalInsights(**video.vocal_insights) if video.vocal_insights else None
   ```

3. **Restart backend:**
   ```bash
   docker-compose restart backend
   ```

---

## Dependency Issues

### Error: `Could not find a version that satisfies the requirement mediapipe==0.10.8`

**Cause:** Python version incompatibility or platform not supported

**Solution:**

```bash
# Check Python version (should be 3.8-3.11)
docker-compose exec backend python --version

# Try different MediaPipe version
docker-compose exec backend pip install mediapipe==0.10.7

# Or latest version
docker-compose exec backend pip install mediapipe
```

---

### Error: `ERROR: Failed building wheel for librosa`

**Cause:** Missing build dependencies

**Solution:**

```bash
# Install build dependencies in Dockerfile
# Add to Dockerfile:
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libsndfile1 \
    ffmpeg

# Rebuild container
docker-compose build backend
docker-compose up -d
```

---

## General Debugging Commands

### View all logs

```bash
# All services
docker-compose logs -f

# Backend only
docker-compose logs -f backend

# Celery only
docker-compose logs -f celery_worker

# Last 100 lines
docker-compose logs --tail=100 celery_worker
```

### Check database state

```bash
# Connect to database
docker-compose exec postgres psql -U promo_admin -d promo_analyzer

# List tables
\dt

# Describe tables
\d+ videos
\d+ analyses

# Query recent videos
SELECT id, status, created_at FROM videos ORDER BY created_at DESC LIMIT 10;

# Query recent analyses
SELECT video_id, congruence_score, authenticity_score FROM analyses ORDER BY created_at DESC LIMIT 10;
```

### Check container health

```bash
# Service status
docker-compose ps

# Resource usage
docker stats

# Restart all services
docker-compose restart

# Rebuild and restart
docker-compose up -d --build
```

### Test individual components

```bash
# Test visual analysis
docker-compose exec backend python -c "
from visual_analysis import VisualAnalysisEngine
print('✅ Visual analysis module OK')
"

# Test vocal analysis
docker-compose exec backend python -c "
from vocal_analysis import VocalAnalysisEngine
print('✅ Vocal analysis module OK')
"

# Test multimodal integration
docker-compose exec backend python -c "
from multimodal_integration_engine import MultiModalIntegrationEngine
print('✅ Multimodal integration module OK')
"

# Test Claude API
docker-compose exec backend python -c "
from anthropic import Anthropic
from config import settings
client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)
print('✅ Claude API connection OK')
"
```

---

## Getting Help

If issue persists after troubleshooting:

1. **Collect diagnostic info:**
   ```bash
   # Save logs
   docker-compose logs > debug_logs.txt

   # Save database schema
   docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ videos" > schema_videos.txt
   docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ analyses" > schema_analyses.txt

   # Save sample data
   docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
     "SELECT * FROM videos WHERE status = 'failed' LIMIT 1;" > failed_video.txt
   ```

2. **Check documentation:**
   - [Implementation Checklist](01-implementation-checklist.md)
   - [Deployment Guide](02-deployment-guide.md)
   - [Testing Guide](03-testing-guide.md)
   - [API Documentation](05-api-documentation.md)

3. **Contact support:**
   - Include diagnostic logs
   - Describe exact error message
   - List steps taken so far
   - Specify environment (staging/production)

---

**Last Updated:** 2025-11-15
**Version:** 1.0 - Multimodal Integration
