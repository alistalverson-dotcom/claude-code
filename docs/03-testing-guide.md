# Testing Guide - Multimodal Integration

## Overview

This guide provides comprehensive testing procedures for validating the multimodal integration. Tests should be run after deployment to ensure all components work correctly.

---

## Prerequisites

Before testing:

- ✅ Database migration applied successfully
- ✅ Backend code updated (models.py, schemas.py, tasks.py)
- ✅ Dependencies installed
- ✅ All services running (backend, celery_worker, postgres, redis)
- ✅ Test video file available (30-90 seconds recommended)

---

## Test 1: Automated Integration Test

### Purpose
Validates complete end-to-end multimodal processing pipeline.

### Setup

1. **Create test video directory:**
   ```bash
   mkdir -p test_videos
   ```

2. **Place test video:**
   - Copy a wrestling promo video to `test_videos/sample_promo.mp4`
   - Recommended: 30-90 seconds duration
   - Must have clear audio and visual content
   - Should show facial expressions and body language

3. **Run test script:**
   ```bash
   python tests/test_multimodal_integration.py
   ```

### Expected Output

```
🧪 MULTIMODAL INTEGRATION TEST
============================================================

1️⃣ Uploading test video...
✅ Video uploaded: 660e8400-e29b-41d4-a716-446655440001

2️⃣ Monitoring processing pipeline...
   Expected: Metadata → Audio → Transcribe → Visual → Vocal → Comprehensive → Jake
   Status: processing
✅ Processing completed in 98s

3️⃣ Verifying multimodal data...
✅ Visual insights present
   - Conviction: 85.5/100
   - Intensity: 78.2/100
   - Eye Contact: 92.0/100
✅ Vocal insights present
   - Vocal Conviction: 82.0/100
   - Vocal Intensity: 88.5/100
   - Confidence: 85.0/100
✅ Comprehensive scores present
   - Congruence: 84.2/100
   - Authenticity: 86.5/100
   - Intensity: 88.8/100
   - Impact: 87.0/100
✅ Grades assigned
   - Character: B+
   - Delivery: A-
   - Psychology: A
✅ Moment-by-moment feedback: 12 moments

4️⃣ Verifying Jake Morrison's enhanced feedback...
✅ Jake's feedback references multimodal data: face, voice, visual, eye, tone, congruence

============================================================
🎉 MULTIMODAL INTEGRATION TEST PASSED!
============================================================
```

### If Test Fails

Check logs for errors:

```bash
# Celery worker logs
docker-compose logs -f celery_worker | grep -i "error\|warning"

# Backend logs
docker-compose logs -f backend | grep -i "error\|warning"

# Check video status
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT id, status, created_at FROM videos ORDER BY created_at DESC LIMIT 5;"
```

---

## Test 2: Database Validation

### Purpose
Verify database schema changes and data storage.

### Test A: Verify New Columns Exist

```bash
# Check videos table
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ videos"
```

**Expected columns:**
- `visual_analysis` (jsonb)
- `visual_insights` (jsonb)
- `vocal_analysis` (jsonb)
- `vocal_insights` (jsonb)

```bash
# Check analyses table
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ analyses"
```

**Expected columns:**
- `comprehensive_data` (jsonb)
- `congruence_score` (numeric)
- `authenticity_score` (numeric)
- `intensity_score` (numeric)
- `impact_score` (numeric)
- `character_grade` (character varying)
- `delivery_grade` (character varying)
- `psychology_grade` (character varying)

### Test B: Verify Indexes Created

```bash
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT indexname FROM pg_indexes WHERE tablename IN ('videos', 'analyses')
   AND (indexname LIKE '%visual%' OR indexname LIKE '%vocal%'
        OR indexname LIKE '%comprehensive%' OR indexname LIKE '%scores%');"
```

**Expected indexes:**
- `idx_videos_visual_analysis`
- `idx_videos_vocal_analysis`
- `idx_analyses_comprehensive_data`
- `idx_analyses_scores`
- `idx_analyses_grades`

### Test C: Verify Data Stored

```bash
# Check visual/vocal data exists
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     id,
     visual_analysis IS NOT NULL AND jsonb_array_length(visual_analysis) > 0 as has_visual,
     vocal_analysis IS NOT NULL AND jsonb_array_length(vocal_analysis) > 0 as has_vocal
   FROM videos
   WHERE status = 'completed'
   LIMIT 5;"
```

**Expected:** `has_visual` and `has_vocal` should be `true` for newly processed videos.

```bash
# Check comprehensive scores exist
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     video_id,
     congruence_score,
     authenticity_score,
     intensity_score,
     impact_score,
     character_grade,
     delivery_grade,
     psychology_grade
   FROM analyses
   ORDER BY created_at DESC
   LIMIT 5;"
```

**Expected:** Scores should be between 0-100, grades should be A-F or NULL.

---

## Test 3: API Endpoint Validation

### Purpose
Verify API returns all new fields correctly.

### Test A: Video Detail Endpoint

```bash
VIDEO_ID="<your_test_video_id>"
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.' > response.json
```

**Verify response includes:**

1. **Visual insights:**
   ```bash
   cat response.json | jq '.visual_insights'
   ```
   Should show:
   ```json
   {
     "conviction_score": 85.5,
     "intensity_score": 78.2,
     "eye_contact_score": 92.0,
     "body_language_score": 80.3,
     ...
   }
   ```

2. **Vocal insights:**
   ```bash
   cat response.json | jq '.vocal_insights'
   ```
   Should show:
   ```json
   {
     "vocal_conviction_score": 82.0,
     "vocal_intensity_score": 88.5,
     "speaking_confidence_score": 85.0,
     ...
   }
   ```

3. **Comprehensive scores:**
   ```bash
   cat response.json | jq '.analyses[0] | {congruence_score, authenticity_score, intensity_score, impact_score}'
   ```
   Should show:
   ```json
   {
     "congruence_score": 84.2,
     "authenticity_score": 86.5,
     "intensity_score": 88.8,
     "impact_score": 87.0
   }
   ```

4. **Grades:**
   ```bash
   cat response.json | jq '.analyses[0] | {character_grade, delivery_grade, psychology_grade}'
   ```
   Should show:
   ```json
   {
     "character_grade": "B+",
     "delivery_grade": "A-",
     "psychology_grade": "A"
   }
   ```

5. **Moment-by-moment feedback:**
   ```bash
   cat response.json | jq '.analyses[0].moment_by_moment | length'
   ```
   Should show a number > 0 (e.g., 12)

   ```bash
   cat response.json | jq '.analyses[0].moment_by_moment[0]'
   ```
   Should show moment structure:
   ```json
   {
     "timestamp": 12.5,
     "duration": 3.2,
     "category": "money_moment",
     "visual_signal": "intense anger, clenched jaw",
     "vocal_signal": "raised volume, aggressive tone",
     "linguistic_signal": "\"You don't deserve...\"",
     "alignment": "aligned",
     "jake_observation": "MONEY MOMENT at 12.5s..."
   }
   ```

---

## Test 4: Celery Task Validation

### Purpose
Verify all tasks are registered and execute correctly.

### Test A: Check Task Registration

```bash
docker-compose exec celery_worker celery -A tasks inspect registered
```

**Expected tasks:**
- `tasks.extract_metadata`
- `tasks.extract_audio`
- `tasks.transcribe_audio`
- `tasks.analyze_visual` **[NEW]**
- `tasks.analyze_vocal` **[NEW]**
- `tasks.analyze_comprehensive` **[NEW]**
- `tasks.analyze_with_jake`
- `tasks.process_video_complete`
- `tasks.health_check`

### Test B: Monitor Task Execution

Start a video upload, then watch Celery logs:

```bash
docker-compose logs -f celery_worker | grep -E "TASK|Starting|complete"
```

**Expected sequence:**
```
[TASK 1/7] Extracting metadata for video...
Metadata extracted: 1920x1080, 90s, h264

[TASK 2/7] Extracting audio for video...
Audio extracted to: /path/to/audio.wav

[TASK 3/7] Transcribing audio for video...
Transcription complete: 245 words

[TASK 4/7] 🎥 Starting VISUAL ANALYSIS for video...
✅ Visual analysis complete: 180 frames analyzed
   - Conviction: 85.5/100
   - Intensity: 78.2/100
   - Eye Contact: 92.0/100

[TASK 5/7] 🎤 Starting VOCAL ANALYSIS for video...
✅ Vocal analysis complete: 45 segments analyzed
   - Vocal Conviction: 82.0/100
   - Vocal Intensity: 88.5/100
   - Confidence: 85.0/100

[TASK 6/7] 🧠 Starting COMPREHENSIVE INTEGRATION for video...
✅ Comprehensive analysis complete!
   - Congruence: 84.2/100
   - Authenticity: 86.5/100
   - Intensity: 88.8/100
   - Impact: 87.0/100
   - Grades: Character=B+, Delivery=A-, Psychology=A

[TASK 7/7] 🎭 Jake Morrison analyzing video...
✅ Jake Morrison analysis complete! Processing time: 18234ms
   - Overall Score: 85.5
```

---

## Test 5: Performance Validation

### Purpose
Ensure processing completes within acceptable timeframes.

### Test Processing Time

Process a test video and measure time for each task:

```bash
# Upload video and capture start time
START_TIME=$(date +%s)
VIDEO_ID=$(curl -X POST -F "file=@test_videos/sample_promo.mp4" \
  http://localhost:8000/api/v1/videos/upload | jq -r '.video_id')

# Wait for completion
while true; do
  STATUS=$(curl -s http://localhost:8000/api/v1/videos/$VIDEO_ID | jq -r '.status')
  if [ "$STATUS" = "completed" ] || [ "$STATUS" = "failed" ]; then
    break
  fi
  sleep 5
done

END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))
echo "Total processing time: ${DURATION}s"
```

**Expected timings for 60-second promo:**

| Task | Expected Duration | Acceptable Range |
|------|-------------------|------------------|
| 1. Extract Metadata | ~5s | 3-10s |
| 2. Extract Audio | ~10s | 5-15s |
| 3. Transcribe | ~30s | 20-45s |
| 4. Visual Analysis | ~15s | 10-25s |
| 5. Vocal Analysis | ~10s | 5-15s |
| 6. Comprehensive | ~8s | 5-15s |
| 7. Jake Analysis | ~20s | 15-30s |
| **TOTAL** | **~98s** | **80-150s** |

**Performance Criteria:**
- ✅ **PASS:** Total time < 3 minutes (180s)
- ⚠️ **WARNING:** Total time 3-5 minutes
- ❌ **FAIL:** Total time > 5 minutes

---

## Test 6: Jake Morrison Feedback Quality

### Purpose
Verify Jake's feedback uses multimodal observations.

### Manual Review Checklist

Get Jake's feedback:

```bash
VIDEO_ID="<your_test_video_id>"
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | \
  jq -r '.analyses[0].detailed_feedback' > jake_feedback.txt

cat jake_feedback.txt
```

**Verify feedback includes:**

- [ ] **Visual observations** (e.g., "I saw you", "your face showed", "eye contact", "facial expression")
- [ ] **Vocal observations** (e.g., "I heard", "your voice", "tone", "volume", "pitch")
- [ ] **Specific timestamps** (e.g., "at 12.5s", "around the 30-second mark")
- [ ] **Money moments** (e.g., "Everything aligned at...", "perfect congruence when...")
- [ ] **Breakdown moments** (e.g., "Your words said X but your face showed Y", "contradiction at...")
- [ ] **Multimodal language** (e.g., "congruence", "alignment", "authentic", "believable")

**Example quality feedback:**

```
Listen kid, I SAW real commitment at 12.5s when your FACE, VOICE, and WORDS all
screamed pure rage - that's a MONEY MOMENT. Your eyes were locked, jaw clenched,
volume spiked, and the words "You don't deserve to be in the same ring as me"
hit with perfect congruence. THAT'S what authenticity looks like.

But then around 45s, your words said you were confident but your VOICE went flat
and your EYES wandered off camera. I HEARD the conviction drop and SAW the
intensity fade. That's a breakdown moment - face, voice, and words weren't aligned.

Work on maintaining that vocal intensity through full statements and keep your
eyes locked when making power claims. You've got the raw material - now make it
consistent.
```

---

## Test 7: Backward Compatibility

### Purpose
Ensure integration doesn't break existing functionality.

### Test A: Existing Videos Still Accessible

```bash
# List all videos
curl http://localhost:8000/api/v1/videos | jq '.videos | length'

# Get details for old video (processed before integration)
OLD_VIDEO_ID="<video_id_from_before_integration>"
curl http://localhost:8000/api/v1/videos/$OLD_VIDEO_ID | jq '.'
```

**Expected:**
- API returns successfully
- Old fields still present
- New fields are null/empty:
  - `visual_insights`: `null` or `{}`
  - `vocal_insights`: `null` or `{}`
  - `congruence_score`: `0.00`
  - `character_grade`: `null`

### Test B: Re-process Old Video

Upload an old video to test that new pipeline processes it:

```bash
# Upload previously analyzed video again
curl -X POST -F "file=@old_promo.mp4" \
  http://localhost:8000/api/v1/videos/upload
```

**Expected:**
- New upload processes with all 7 tasks
- Receives visual, vocal, and comprehensive analysis
- Gets new multimodal scores and grades

---

## Test 8: Error Handling

### Purpose
Verify system handles errors gracefully.

### Test A: Invalid Video Format

```bash
# Try uploading a text file as video
echo "not a video" > fake.mp4
curl -X POST -F "file=@fake.mp4" http://localhost:8000/api/v1/videos/upload
```

**Expected:**
- Upload rejected OR processing fails gracefully
- Video status set to "failed"
- Error logged but system continues running

### Test B: Missing Dependencies

Temporarily break a dependency and test:

```bash
# Rename visual_analysis.py to simulate missing dependency
docker-compose exec backend mv /app/visual_analysis.py /app/visual_analysis.py.bak

# Try processing video
# Upload should work but Task 4 should fail

# Restore file
docker-compose exec backend mv /app/visual_analysis.py.bak /app/visual_analysis.py
docker-compose restart celery_worker
```

**Expected:**
- Task 4 (analyze_visual) fails with import error
- Pipeline stops at failed task
- Video status set to "failed"
- Error logged with clear message

---

## Test Checklist Summary

After running all tests, verify:

- [ ] Automated integration test passes
- [ ] All database columns exist
- [ ] All indexes created
- [ ] Data stored in database (visual, vocal, comprehensive)
- [ ] API returns all new fields
- [ ] All 7 Celery tasks registered
- [ ] Tasks execute in correct sequence
- [ ] Processing time < 3 minutes
- [ ] Jake's feedback is multimodal
- [ ] Backward compatibility maintained
- [ ] Old videos still accessible
- [ ] Error handling works
- [ ] No regressions in existing features

---

## Troubleshooting Failed Tests

### Test Fails: "Visual insights not found"

**Possible causes:**
1. visual_analysis.py not present in backend/
2. MediaPipe failed to initialize
3. Task 4 (analyze_visual) failed silently

**Solution:**
```bash
# Check if file exists
docker-compose exec backend ls -lh /app/visual_analysis.py

# Check Celery logs for Task 4
docker-compose logs celery_worker | grep -i "visual"

# Test import manually
docker-compose exec backend python -c "from visual_analysis import VisualAnalysisEngine; print('✅ Import works')"
```

### Test Fails: "Vocal insights not found"

**Possible causes:**
1. vocal_analysis.py not present in backend/
2. Librosa failed to initialize
3. Audio extraction failed in Task 2

**Solution:**
```bash
# Check if file exists
docker-compose exec backend ls -lh /app/vocal_analysis.py

# Check if audio was extracted
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT id, audio_path FROM videos ORDER BY created_at DESC LIMIT 5;"

# Test import manually
docker-compose exec backend python -c "from vocal_analysis import VocalAnalysisEngine; print('✅ Import works')"
```

### Test Fails: "Comprehensive data empty"

**Possible causes:**
1. multimodal_integration_engine.py not present
2. Tasks 4 or 5 failed before Task 6
3. Data not passed correctly between tasks

**Solution:**
```bash
# Check if file exists
docker-compose exec backend ls -lh /app/multimodal_integration_engine.py

# Check database for visual/vocal data
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     visual_analysis IS NOT NULL as has_visual,
     vocal_analysis IS NOT NULL as has_vocal
   FROM videos
   WHERE id = '<VIDEO_ID>';"

# Test import manually
docker-compose exec backend python -c "from multimodal_integration_engine import MultiModalIntegrationEngine; print('✅ Import works')"
```

---

**Last Updated:** 2025-11-15
**Version:** 1.0 - Multimodal Integration
