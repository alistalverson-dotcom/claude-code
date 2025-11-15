# 🧪 Testing Guide - Wrestling Promo Analyzer

Complete end-to-end testing documentation for Sprint 2A validation.

---

## 📋 Table of Contents

- [Quick Test](#quick-test)
- [Manual Testing Checklist](#manual-testing-checklist)
- [Automated API Tests](#automated-api-tests)
- [Test Video Library](#test-video-library)
- [Performance Testing](#performance-testing)
- [Quality Evaluation](#quality-evaluation)
- [Cost Tracking](#cost-tracking)

---

## ⚡ Quick Test

**5-Minute Smoke Test** - Verify basic functionality:

```bash
# 1. Start all services
docker-compose up -d

# 2. Check all services are healthy
docker-compose ps

# 3. Check backend health
curl http://localhost:8000/health

# 4. Open frontend
open http://localhost:3000

# 5. Upload a test video (via UI)
# - Use a 1-2 minute video
# - Add title: "Quick Test"
# - Wait for processing to complete
# - Verify results display correctly

# 6. Check logs for errors
docker-compose logs backend | grep ERROR
docker-compose logs celery_worker | grep ERROR
```

**Expected Results**:
- ✅ All services show "Up" status
- ✅ Health check returns "healthy"
- ✅ Video uploads without errors
- ✅ Processing completes in < 3 minutes
- ✅ Analysis displays with score and feedback
- ✅ No ERROR logs (warnings are OK)

---

## 📝 Manual Testing Checklist

### Test 1: Video Upload
- [ ] **Test 1.1**: Upload MP4 video (1 minute)
  - Expected: Upload succeeds, shows progress bar
  - Actual: ___________________

- [ ] **Test 1.2**: Upload MOV video (5 minutes)
  - Expected: Upload succeeds, redirects to detail page
  - Actual: ___________________

- [ ] **Test 1.3**: Upload AVI video (10 minutes)
  - Expected: Upload succeeds, starts processing
  - Actual: ___________________

- [ ] **Test 1.4**: Try to upload unsupported format (.wmv)
  - Expected: Shows error "Invalid file type"
  - Actual: ___________________

- [ ] **Test 1.5**: Try to upload file > 500MB
  - Expected: Shows error "File too large"
  - Actual: ___________________

- [ ] **Test 1.6**: Upload with optional metadata
  - Promo title: "Championship Challenge"
  - Character type: Heel
  - Promo type: Challenge
  - Context: "Challenging for world title"
  - Expected: Metadata saved, visible in results
  - Actual: ___________________

### Test 2: Processing Pipeline
- [ ] **Test 2.1**: Verify metadata extraction
  - Upload video, check video detail page
  - Expected: Duration, resolution, codec displayed
  - Actual: ___________________

- [ ] **Test 2.2**: Verify transcription
  - Wait for processing to complete
  - Expected: Full transcript with timestamps
  - Actual: ___________________

- [ ] **Test 2.3**: Verify Jake Morrison analysis
  - Check analysis section
  - Expected: Score, grade, categories, feedback
  - Actual: ___________________

- [ ] **Test 2.4**: Check processing time
  - Note: Start time, end time
  - Expected: < 2 minutes for 5-minute video
  - Actual: ___________________

### Test 3: Frontend UI
- [ ] **Test 3.1**: Upload page loads correctly
  - Expected: Drag-drop zone, metadata form
  - Actual: ___________________

- [ ] **Test 3.2**: Videos list page shows all videos
  - Expected: List of uploaded videos with status
  - Actual: ___________________

- [ ] **Test 3.3**: Status filtering works
  - Filter by "completed"
  - Expected: Only completed videos shown
  - Actual: ___________________

- [ ] **Test 3.4**: Video detail page during processing
  - Expected: Shows "Processing" with animated status
  - Actual: ___________________

- [ ] **Test 3.5**: Video detail page when completed
  - Expected: Full analysis displayed beautifully
  - Actual: ___________________

- [ ] **Test 3.6**: Transcript view toggle
  - Switch between "Full Text" and "Segments"
  - Expected: Both views work correctly
  - Actual: ___________________

### Test 4: Error Handling
- [ ] **Test 4.1**: Invalid video file (corrupt)
  - Expected: Error message, status = "failed"
  - Actual: ___________________

- [ ] **Test 4.2**: Network interruption during upload
  - Disconnect internet mid-upload
  - Expected: Upload fails with retry option
  - Actual: ___________________

- [ ] **Test 4.3**: Missing Anthropic API key
  - Temporarily remove API key, upload video
  - Expected: Processing fails, clear error message
  - Actual: ___________________

- [ ] **Test 4.4**: Database connection loss
  - Stop postgres, try to upload
  - Expected: Connection error displayed
  - Actual: ___________________

### Test 5: Edge Cases
- [ ] **Test 5.1**: Video with no audio
  - Expected: Transcription empty, analysis handles gracefully
  - Actual: ___________________

- [ ] **Test 5.2**: Video with background music
  - Expected: Transcription may have noise, still works
  - Actual: ___________________

- [ ] **Test 5.3**: Very quiet audio
  - Expected: Whisper transcribes, may be less accurate
  - Actual: ___________________

- [ ] **Test 5.4**: Multiple speakers
  - Expected: All speech transcribed, no speaker labels
  - Actual: ___________________

- [ ] **Test 5.5**: Non-English audio
  - Expected: Whisper detects language, transcribes
  - Actual: ___________________

---

## 🤖 Automated API Tests

Create `backend/test_api.py`:

```python
"""
API Integration Tests
Run: pytest test_api.py -v
"""

import pytest
import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"

def test_health_check():
    """Test health endpoint"""
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"

def test_list_videos_empty():
    """Test listing videos when database is empty"""
    response = requests.get(f"{BASE_URL}/api/v1/videos")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_upload_video():
    """Test video upload endpoint"""
    # Create a tiny test video file (won't actually process)
    test_file = Path("test_video.mp4")
    test_file.write_bytes(b"fake video content")

    try:
        with open(test_file, "rb") as f:
            files = {"file": ("test.mp4", f, "video/mp4")}
            data = {
                "promo_title": "Test Promo",
                "character_type": "heel",
            }
            response = requests.post(
                f"{BASE_URL}/api/v1/videos/upload",
                files=files,
                data=data
            )

        # May fail due to invalid video, but should return proper error
        assert response.status_code in [201, 400, 500]

    finally:
        test_file.unlink()

def test_get_nonexistent_video():
    """Test getting video that doesn't exist"""
    fake_uuid = "00000000-0000-0000-0000-000000000000"
    response = requests.get(f"{BASE_URL}/api/v1/videos/{fake_uuid}")
    assert response.status_code == 404

def test_list_judges():
    """Test listing judges"""
    response = requests.get(f"{BASE_URL}/api/v1/judges")
    assert response.status_code == 200
    judges = response.json()
    assert len(judges) >= 1
    assert judges[0]["name"] == "Jake Morrison"

def test_get_jake_morrison():
    """Test getting Jake Morrison judge"""
    response = requests.get(f"{BASE_URL}/api/v1/judges/jake-morrison")
    assert response.status_code == 200
    judge = response.json()
    assert judge["slug"] == "jake-morrison"
    assert judge["is_active"] == True

def test_invalid_file_type():
    """Test uploading invalid file type"""
    test_file = Path("test.txt")
    test_file.write_text("not a video")

    try:
        with open(test_file, "rb") as f:
            files = {"file": ("test.txt", f, "text/plain")}
            response = requests.post(
                f"{BASE_URL}/api/v1/videos/upload",
                files=files
            )

        assert response.status_code == 400
        assert "Invalid file type" in response.json()["detail"]

    finally:
        test_file.unlink()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

**Run Tests**:
```bash
# Install pytest
docker-compose exec backend pip install pytest

# Run tests
docker-compose exec backend pytest test_api.py -v
```

---

## 📹 Test Video Library

### Recommended Test Videos

**Create a test videos folder**: `test_videos/`

1. **short_1min.mp4** (1 minute)
   - Tests: Quick processing, minimum length
   - Expected processing: ~30 seconds

2. **medium_5min.mp4** (5 minutes)
   - Tests: Standard processing, typical promo
   - Expected processing: ~90 seconds

3. **long_10min.mp4** (10 minutes)
   - Tests: Longer processing, cost calculation
   - Expected processing: ~3 minutes

4. **quiet_audio.mp4**
   - Tests: Whisper handling of low volume
   - Expected: May have transcription gaps

5. **accented_speaker.mp4**
   - Tests: Whisper handling of accents
   - Expected: Should still transcribe

6. **multiple_speakers.mp4**
   - Tests: Multiple people talking
   - Expected: All speech transcribed

7. **background_music.mp4**
   - Tests: Audio with music
   - Expected: Transcription with some noise

### Finding Test Videos

**Sources**:
- YouTube wrestling promos (download with yt-dlp)
- Record your own test promos
- Use stock footage with voiceover
- Create synthetic test videos with TTS

**Download from YouTube**:
```bash
# Install yt-dlp
pip install yt-dlp

# Download a 1-minute section
yt-dlp --download-sections "*0:00-1:00" -f "best[ext=mp4]" -o "short_1min.mp4" <URL>
```

---

## 🎯 Performance Testing

### Processing Time Benchmarks

**Test each video length 3 times, record average**:

| Video Length | Trial 1 | Trial 2 | Trial 3 | Average | Target |
|--------------|---------|---------|---------|---------|--------|
| 1 minute     |         |         |         |         | < 30s  |
| 5 minutes    |         |         |         |         | < 90s  |
| 10 minutes   |         |         |         |         | < 180s |

### Component Breakdown

For a 5-minute video, measure each step:

| Step                  | Time    | % of Total |
|-----------------------|---------|------------|
| 1. Metadata Extract   |         |            |
| 2. Audio Extract      |         |            |
| 3. Transcription      |         |            |
| 4. Jake Analysis      |         |            |
| **Total**             |         | 100%       |

**How to Measure**:
```bash
# Check Celery logs for task timing
docker-compose logs celery_worker | grep "Task.*succeeded"
```

---

## ✅ Quality Evaluation

### Jake Morrison Feedback Quality

**Evaluate each analysis on 1-5 scale**:

| Criteria                           | Video 1 | Video 2 | Video 3 | Avg |
|------------------------------------|---------|---------|---------|-----|
| Overall score seems accurate       |         |         |         |     |
| Category scores make sense         |         |         |         |     |
| Summary is helpful                 |         |         |         |     |
| Strengths are specific             |         |         |         |     |
| Weaknesses are constructive        |         |         |         |     |
| Timestamped feedback is accurate   |         |         |         |     |
| Recommendations are actionable     |         |         |         |     |
| **Overall Quality**                |         |         |         |     |

**Rating Scale**:
- 5 = Excellent, professional quality
- 4 = Good, useful feedback
- 3 = Acceptable, some value
- 2 = Poor, needs improvement
- 1 = Unusable, incorrect

### Transcription Accuracy

**Spot check 5 random segments per video**:

| Segment      | Expected Text           | Actual Text             | Accurate? |
|--------------|-------------------------|-------------------------|-----------|
| 0:15-0:20    | "I am the champion"     |                         |           |
| 1:30-1:35    | "You don't stand..."    |                         |           |
| 2:45-2:50    | ...                     |                         |           |

**Accuracy Rate**: ___ / 5 = ____%

---

## 💰 Cost Tracking

### Claude API Costs

**Track for each video**:

| Video | Duration | Input Tokens | Output Tokens | Total Tokens | Est. Cost |
|-------|----------|--------------|---------------|--------------|-----------|
| 1     |          |              |               |              |           |
| 2     |          |              |               |              |           |
| 3     |          |              |               |              |           |
| **Avg** |        |              |               |              |           |

**Cost Calculation**:
- Claude Sonnet 4: $3 per million input tokens, $15 per million output tokens
- Formula: (input_tokens * 0.000003) + (output_tokens * 0.000015)

**Where to Find**:
- Check Celery logs for token counts
- Or check Analysis model: `token_count` field
- Or Anthropic dashboard: https://console.anthropic.com/

### Cost Projections

**Based on averages**:
- Cost per 1-min video: $___
- Cost per 5-min video: $___
- Cost per 10-min video: $___

**Monthly projections**:
- 10 videos/day × 30 days = 300 videos/month
- Estimated cost: $___

---

## 🐛 Bug Tracking

**Document any issues found**:

| # | Severity | Component | Description | Steps to Reproduce | Status |
|---|----------|-----------|-------------|-------------------|--------|
| 1 | High     | Celery    | Task fails with...  | 1. Upload... 2. ... | Open |
| 2 | Medium   | Frontend  | Loading spinner...  | 1. ... | Fixed |

**Severity Levels**:
- **Critical**: App doesn't work, data loss
- **High**: Major feature broken
- **Medium**: Minor feature broken, has workaround
- **Low**: Cosmetic, minor annoyance

---

## 📊 Test Results Template

**Copy and fill out after testing**:

```markdown
# Test Results - [Date]

## Summary
- Videos tested: X
- Success rate: X%
- Average processing time: Xs
- Average cost: $X
- Critical bugs: X
- Overall quality rating: X/5

## Performance
- 1-min video avg: Xs (target: 30s)
- 5-min video avg: Xs (target: 90s)
- 10-min video avg: Xs (target: 180s)

## Quality
- Jake Morrison feedback: X/5
- Transcription accuracy: X%
- User experience: X/5

## Bugs Found
1. [Severity] Description
2. ...

## Recommendations
- Priority 1: ...
- Priority 2: ...
- Priority 3: ...

## Next Steps
- [ ] Fix critical bugs
- [ ] Improve Jake prompt
- [ ] Optimize performance
```

---

## 🚀 Ready to Test!

1. Start services: `docker-compose up -d`
2. Prepare test videos
3. Follow manual testing checklist
4. Run automated tests
5. Document results
6. Analyze and improve

**Good luck testing!** 🎬
