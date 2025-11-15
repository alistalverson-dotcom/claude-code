# Quick Start Guide - Promo Analyzer Multimodal Integration

## 🎯 What Is This Repository?

This repository contains **integration documentation** for adding multimodal analysis capabilities to the Wrestling Promo Analyzer application.

**Your Base System:**
- Full-stack web app (React + FastAPI)
- Video upload and transcript analysis
- Jake Morrison AI judge (transcript-only)
- 4-task processing pipeline

**This Integration Adds:**
- Visual analysis (facial expressions, body language)
- Vocal analysis (tone, pitch, emotional markers)
- Comprehensive synthesis (congruence detection)
- Enhanced Jake Morrison (multimodal observations)
- 7-task processing pipeline

---

## 📁 Repository Structure

```
claude-code/
├── QUICK_START.md              ← You are here
├── README.md                   ← Executive summary
├── INTEGRATION_OVERVIEW.md     ← How integration fits into base system
│
├── docs/                       ← Complete documentation
│   ├── 01-implementation-checklist.md
│   ├── 02-deployment-guide.md
│   ├── 03-testing-guide.md
│   ├── 04-troubleshooting.md
│   └── 05-api-documentation.md
│
├── migrations/                 ← Database changes
│   ├── 001_add_multimodal_fields.sql
│   └── 001_rollback.sql
│
├── backend/                    ← Backend resources
│   └── requirements-additions.txt
│
└── tests/                      ← Testing
    └── test_multimodal_integration.py
```

---

## 🚀 Getting Started

### Step 1: Read Integration Overview (5 minutes)

```bash
cat INTEGRATION_OVERVIEW.md
```

**This explains:**
- How multimodal integration extends your base system
- What changes and what stays the same
- Before/after comparison
- Impact on processing time, cost, and data

### Step 2: Review Implementation Checklist (10 minutes)

```bash
cat docs/01-implementation-checklist.md
```

**This provides:**
- 6 phases with detailed tasks
- Expected time: 2-3 hours total
- Step-by-step instructions
- Verification procedures

### Step 3: Check Prerequisites (5 minutes)

**Your base system must be running:**

```bash
# Check Docker services
docker-compose ps
# Should show: backend, celery_worker, postgres, redis all "Up"

# Check backend health
curl http://localhost:8000/health
# Should return: {"status": "healthy"}

# Check frontend
# Open http://localhost:3000 in browser
# Should load upload page

# Process a test video through existing system
# Verify 4-task pipeline works:
#   1. Extract Metadata
#   2. Extract Audio
#   3. Transcribe
#   4. Jake Analysis
```

**If base system isn't running**, you need to deploy it first using your existing build documentation.

### Step 4: Required Files (10 minutes)

**You need these files from Weeks 1-3 deliverables:**

1. `visual_analysis.py` (Week 1 - Visual Analysis Engine)
2. `vocal_analysis.py` (Week 2 - Vocal Analysis Engine)
3. `multimodal_integration_engine.py` (Week 3 - Multimodal Integration)

**Copy them to your backend directory:**

```bash
# Example:
cp /path/to/week1/visual_analysis.py backend/
cp /path/to/week2/vocal_analysis.py backend/
cp /path/to/week3/multimodal_integration_engine.py backend/

# Verify they exist
ls -lh backend/visual_analysis.py
ls -lh backend/vocal_analysis.py
ls -lh backend/multimodal_integration_engine.py
```

### Step 5: Backup Everything (5 minutes)

```bash
# Backup database
docker-compose exec postgres pg_dump -U promo_admin promo_analyzer > \
  backup_$(date +%Y%m%d_%H%M%S).sql

# Backup code
git add .
git commit -m "Pre-multimodal-integration backup"
git push origin main

# Backup specific files
cp backend/models.py backend/models.py.backup
cp backend/schemas.py backend/schemas.py.backup
cp backend/tasks.py backend/tasks.py.backup
```

### Step 6: Apply Database Migration (10 minutes)

```bash
# Copy migration to container
docker cp migrations/001_add_multimodal_fields.sql \
  promo_analyzer_postgres:/tmp/migration.sql

# Apply migration
docker-compose exec postgres psql -U promo_admin -d promo_analyzer \
  -f /tmp/migration.sql

# Verify new columns exist
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ videos"
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ analyses"
```

**Expected new columns:**
- `videos`: visual_analysis, visual_insights, vocal_analysis, vocal_insights
- `analyses`: comprehensive_data, congruence_score, authenticity_score, intensity_score, impact_score, character_grade, delivery_grade, psychology_grade

### Step 7: Install Dependencies (15 minutes)

```bash
# Add dependencies to requirements.txt
cat backend/requirements-additions.txt >> backend/requirements.txt

# Install in container
docker-compose exec backend pip install -r requirements.txt

# OR rebuild container (cleaner)
docker-compose build backend
docker-compose up -d

# Verify installation
docker-compose exec backend pip list | grep -E "mediapipe|librosa|fer|opencv"
```

### Step 8: Update Backend Code (30 minutes)

**Follow detailed instructions in:**
```bash
cat docs/01-implementation-checklist.md
# See "Phase 3: Code Integration"
```

**Summary:**
1. Update `backend/models.py` - Add new ORM fields
2. Update `backend/schemas.py` - Add new Pydantic models
3. Update `backend/tasks.py` - Add 3 new tasks, enhance 1 existing

**Or reference the complete code examples in:**
```bash
cat docs/05-api-documentation.md
# Contains complete model and schema definitions
```

### Step 9: Restart Services (5 minutes)

```bash
# Restart backend and Celery worker
docker-compose restart backend celery_worker

# Wait for startup
sleep 30

# Verify no errors
docker-compose logs backend | tail -50
docker-compose logs celery_worker | tail -50

# Verify tasks registered
docker-compose exec celery_worker celery -A tasks inspect registered
# Should show: analyze_visual, analyze_vocal, analyze_comprehensive
```

### Step 10: Test Integration (30 minutes)

```bash
# Create test videos directory
mkdir -p test_videos

# Place a test video (30-90 seconds recommended)
# File: test_videos/sample_promo.mp4

# Run automated test
python tests/test_multimodal_integration.py
```

**Expected output:**
```
🧪 MULTIMODAL INTEGRATION TEST
============================================================

1️⃣ Uploading test video...
✅ Video uploaded: 660e8400-...

2️⃣ Monitoring processing pipeline...
✅ Processing completed in 98s

3️⃣ Verifying multimodal data...
✅ Visual insights present
   - Conviction: 85.5/100
   - Intensity: 78.2/100
✅ Vocal insights present
   - Vocal Conviction: 82.0/100
✅ Comprehensive scores present
   - Congruence: 84.2/100
✅ Grades assigned
   - Character: B+

4️⃣ Verifying Jake Morrison's enhanced feedback...
✅ Jake's feedback references multimodal data

============================================================
🎉 MULTIMODAL INTEGRATION TEST PASSED!
============================================================
```

---

## 🎯 What Success Looks Like

### API Response Before Integration

```json
{
  "video_id": "...",
  "status": "completed",
  "analyses": [{
    "overall_score": 78.5,
    "summary": "Good use of psychology. Your pacing was strong...",
    "strengths": ["Word choice showed character consistency"],
    "weaknesses": ["Volume could be stronger"]
  }]
}
```

### API Response After Integration

```json
{
  "video_id": "...",
  "status": "completed",
  "visual_insights": {
    "conviction_score": 85.5,
    "intensity_score": 78.2,
    "eye_contact_score": 92.0
  },
  "vocal_insights": {
    "vocal_conviction_score": 82.0,
    "vocal_intensity_score": 88.5
  },
  "analyses": [{
    "overall_score": 78.5,
    "congruence_score": 84.2,
    "authenticity_score": 86.5,
    "character_grade": "B+",
    "delivery_grade": "A-",
    "summary": "I SAW real intensity at 0:15 when your eyes locked and jaw clenched...",
    "moment_by_moment": [
      {
        "timestamp": 12.5,
        "category": "money_moment",
        "alignment": "aligned",
        "visual_signal": "intense anger, clenched jaw",
        "vocal_signal": "raised volume, aggressive tone",
        "jake_observation": "MONEY MOMENT - everything aligned perfectly..."
      }
    ]
  }]
}
```

### Jake Morrison Before vs After

**Before (Transcript-Only):**
> "Good use of psychology building to the championship match. Your pacing was strong in the opening when you established stakes. Volume could be stronger in the middle section."

**After (Multimodal):**
> "I SAW real intensity at 0:15 when your eyes locked on camera and jaw clenched - your FACE told me you meant business. But then I HEARD your voice go flat at 0:45 while your WORDS said you were confident. That's a breakdown moment. At 1:30, EVERYTHING aligned - angry face, aggressive tone, powerful words - that's a MONEY MOMENT."

---

## 📊 Quick Reference

### Processing Pipeline Comparison

**Before:**
```
Upload → Metadata → Audio → Transcribe → Jake Analysis
                                          (transcript only)
Time: ~75 seconds
```

**After:**
```
Upload → Metadata → Audio → Transcribe → Visual → Vocal → Comprehensive → Jake Analysis
                                                                          (multimodal)
Time: ~98 seconds (+23s)
```

### Database Changes

**New tables:** None
**Modified tables:** `videos` (+ 4 fields), `analyses` (+ 8 fields)
**New indexes:** 5
**Breaking changes:** None

### Dependencies Added

**Visual Analysis:**
- opencv-python 4.8.1.78
- mediapipe 0.10.8
- fer 22.5.1
- pillow 10.1.0

**Vocal Analysis:**
- librosa 0.10.1
- soundfile 0.12.1
- praat-parselmouth 0.4.3
- scipy 1.11.4
- numpy 1.24.3

**Integration:**
- scikit-learn 1.3.2

### Cost Impact

- **Before:** ~$0.40 per video (Claude API)
- **After:** ~$0.40 per video (same - visual/vocal are free)

---

## 🔥 Common Issues & Solutions

### Issue: Import errors

**Error:** `ModuleNotFoundError: No module named 'visual_analysis'`

**Solution:**
```bash
# Verify files exist
ls -lh backend/visual_analysis.py
ls -lh backend/vocal_analysis.py
ls -lh backend/multimodal_integration_engine.py

# If missing, copy from Week 1-3 deliverables
# Then restart Celery worker
docker-compose restart celery_worker
```

### Issue: Database errors

**Error:** `column "visual_analysis" does not exist`

**Solution:**
```bash
# Apply migration
docker cp migrations/001_add_multimodal_fields.sql \
  promo_analyzer_postgres:/tmp/migration.sql

docker-compose exec postgres psql -U promo_admin -d promo_analyzer \
  -f /tmp/migration.sql

# Restart services
docker-compose restart backend celery_worker
```

### Issue: Tasks not registered

**Error:** `Received unregistered task 'tasks.analyze_visual'`

**Solution:**
```bash
# Restart Celery worker
docker-compose restart celery_worker

# Verify tasks registered
docker-compose exec celery_worker celery -A tasks inspect registered
```

**For more troubleshooting:** See `docs/04-troubleshooting.md`

---

## 📞 Support & Documentation

### Primary Documentation

1. **INTEGRATION_OVERVIEW.md** - How integration fits into base system
2. **docs/01-implementation-checklist.md** - Step-by-step guide (PRIMARY)
3. **docs/02-deployment-guide.md** - Production deployment
4. **docs/03-testing-guide.md** - Validation procedures
5. **docs/04-troubleshooting.md** - Common issues & solutions
6. **docs/05-api-documentation.md** - API schemas & response formats

### Quick Commands

```bash
# View all documentation
ls docs/

# Read specific guide
cat docs/01-implementation-checklist.md

# Check logs
docker-compose logs -f celery_worker

# Test database connection
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\dt"

# Verify API working
curl http://localhost:8000/health
```

---

## ✅ Final Checklist

Before considering integration complete:

- [ ] Base system deployed and working
- [ ] Week 1-3 files copied to backend/
- [ ] Database backup created
- [ ] Code backup created
- [ ] Database migration applied
- [ ] Dependencies installed
- [ ] Backend code updated (models, schemas, tasks)
- [ ] Services restarted
- [ ] All 7 tasks registered in Celery
- [ ] Test video processed successfully
- [ ] Test script passes all checks
- [ ] Visual insights in API response
- [ ] Vocal insights in API response
- [ ] Comprehensive scores in API response
- [ ] Jake's feedback references multimodal observations
- [ ] No errors in logs
- [ ] Old videos still accessible

---

## 🎬 Next Steps After Integration

1. **Frontend Updates (Optional)**
   - Add visual insights display
   - Add vocal insights display
   - Add comprehensive scores display
   - Add moment timeline visualization

2. **User Testing**
   - Process 20-30 test videos
   - Compare feedback quality: transcript-only vs multimodal
   - Gather user feedback
   - Measure engagement metrics

3. **Optimization**
   - Tune visual analysis parameters
   - Tune vocal analysis parameters
   - Refine Jake's prompt templates
   - Optimize processing performance

4. **Production Deployment**
   - Follow `docs/02-deployment-guide.md`
   - Enable HTTPS
   - Set up monitoring
   - Configure backups

---

## 🎯 Key Takeaways

1. **Non-Breaking:** Integration maintains backward compatibility
2. **Minimal Impact:** +23 seconds processing time, same cost
3. **High Value:** Transforms Jake from transcript analyst to performance coach
4. **Production-Ready:** Complete documentation, testing, rollback plan
5. **Well-Documented:** 5 comprehensive guides + troubleshooting + API reference

**Integration Time:** 2-3 hours
**Risk Level:** Low (rollback available)
**Value Added:** High (multimodal analysis)

---

**Ready to enhance Jake Morrison with multimodal superpowers! 🚀**

**Start here:** `docs/01-implementation-checklist.md`
