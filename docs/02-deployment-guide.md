# Deployment Guide - Multimodal Integration

## Overview

This guide provides complete step-by-step instructions for deploying the multimodal integration to a production or staging environment.

**Estimated Time:** 2-3 hours
**Difficulty:** Intermediate
**Prerequisites:** Docker, PostgreSQL, Redis, existing Promo Analyzer backend

---

## Pre-Deployment Checklist

Before starting deployment:

- [ ] Have database admin access
- [ ] Have Docker access (docker-compose commands)
- [ ] Have git commit/push access
- [ ] Have production/staging environment access
- [ ] Maintenance window scheduled (optional but recommended)
- [ ] Team notified of deployment
- [ ] Backup strategy prepared

---

## Step 1: Backup Everything (5 minutes)

### A. Backup Database

```bash
# Create backup directory
mkdir -p backups
cd backups

# Backup database
docker-compose exec postgres pg_dump -U promo_admin promo_analyzer > \
  backup_$(date +%Y%m%d_%H%M%S).sql

# Verify backup file exists and has content
ls -lh backup_*.sql
head -20 backup_*.sql
```

**Expected:** Backup file should be several MB and contain SQL statements.

### B. Backup Code

```bash
# Commit all current changes
git add .
git commit -m "Pre-multimodal-integration backup - $(date +%Y-%m-%d)"

# Push to remote
git push origin main

# Create backup branch
git checkout -b backup-pre-multimodal-$(date +%Y%m%d)
git push origin backup-pre-multimodal-$(date +%Y%m%d)

# Return to main
git checkout main
```

### C. Backup Configuration Files

```bash
# Backup specific files
cp backend/models.py backend/models.py.backup
cp backend/schemas.py backend/schemas.py.backup
cp backend/tasks.py backend/tasks.py.backup
cp backend/requirements.txt backend/requirements.txt.backup
```

### D. Document Current State

```bash
# Record current service status
docker-compose ps > backups/service_status_before.txt

# Record current database schema
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\dt" > \
  backups/db_schema_before.txt

# Record current video/analysis counts
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT 'videos' as table, count(*) FROM videos
   UNION ALL
   SELECT 'analyses', count(*) FROM analyses;" > \
  backups/record_counts_before.txt
```

---

## Step 2: Create Feature Branch (2 minutes)

```bash
# Create and checkout feature branch
git checkout -b feature/multimodal-integration

# Verify you're on the branch
git branch
# Should show: * feature/multimodal-integration
```

---

## Step 3: Verify Environment (5 minutes)

### A. Check Services Running

```bash
docker-compose ps
```

**Expected:** All services should show "Up" status:
- backend
- celery_worker
- postgres
- redis

If any service is down:
```bash
docker-compose up -d <service_name>
```

### B. Check Disk Space

```bash
df -h
```

**Required:** At least 2GB free space for dependencies and processing.

If low on space:
```bash
# Clean Docker images
docker system prune -a

# Clean old backups
rm -f backups/backup_old_*.sql
```

### C. Test Database Connection

```bash
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "SELECT version();"
```

**Expected:** PostgreSQL version information.

### D. Test Backend Health

```bash
curl http://localhost:8000/health
```

**Expected:** `{"status": "healthy"}` or similar.

---

## Step 4: Apply Database Migration (10 minutes)

### A. Review Migration Script

```bash
# Review what changes will be made
cat migrations/001_add_multimodal_fields.sql
```

**Verify:**
- Adds 4 columns to `videos` table
- Adds 8 columns to `analyses` table
- Creates 5 indexes
- Adds grade validation constraint

### B. Copy Migration to Container

```bash
docker cp migrations/001_add_multimodal_fields.sql \
  promo_analyzer_postgres:/tmp/migration.sql
```

### C. Apply Migration

```bash
# Run migration
docker-compose exec postgres psql -U promo_admin -d promo_analyzer \
  -f /tmp/migration.sql
```

**Expected output:**
```
BEGIN
ALTER TABLE
ALTER TABLE
ALTER TABLE
CREATE INDEX
CREATE INDEX
...
COMMIT
```

**Look for:** `COMMIT` at the end (indicates success).

### D. Verify Migration Success

```bash
# Check videos table has new columns
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ videos"
```

**Expected columns:**
- `visual_analysis`
- `visual_insights`
- `vocal_analysis`
- `vocal_insights`

```bash
# Check analyses table has new columns
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ analyses"
```

**Expected columns:**
- `comprehensive_data`
- `congruence_score`
- `authenticity_score`
- `intensity_score`
- `impact_score`
- `character_grade`
- `delivery_grade`
- `psychology_grade`

### E. Verify Indexes Created

```bash
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT indexname FROM pg_indexes WHERE tablename IN ('videos', 'analyses')
   AND (indexname LIKE '%visual%' OR indexname LIKE '%vocal%'
        OR indexname LIKE '%comprehensive%');"
```

**Expected indexes:**
- `idx_videos_visual_analysis`
- `idx_videos_vocal_analysis`
- `idx_analyses_comprehensive_data`
- `idx_analyses_scores`
- `idx_analyses_grades`

---

## Step 5: Install Dependencies (15 minutes)

### A. Update requirements.txt

```bash
# Add new dependencies to backend/requirements.txt
cat backend/requirements-additions.txt >> backend/requirements.txt
```

**Or manually add these lines to `backend/requirements.txt`:**

```txt
# Week 1 - Visual Analysis
opencv-python==4.8.1.78
mediapipe==0.10.8
fer==22.5.1
pillow==10.1.0

# Week 2 - Vocal Analysis
librosa==0.10.1
soundfile==0.12.1
praat-parselmouth==0.4.3
scipy==1.11.4
numpy==1.24.3

# Week 3 - Multimodal Integration
scikit-learn==1.3.2
```

### B. Install in Docker Container (Option 1 - Faster)

```bash
# Install dependencies in running container
docker-compose exec backend pip install -r requirements.txt

# This takes ~5-10 minutes
# Watch for successful installations
```

**Look for:**
```
Successfully installed opencv-python-4.8.1.78
Successfully installed mediapipe-0.10.8
Successfully installed fer-22.5.1
...
```

### C. Rebuild Container (Option 2 - Cleaner)

```bash
# Rebuild backend container with new dependencies
docker-compose build backend

# This takes ~10-15 minutes
# Restart services
docker-compose up -d
```

### D. Verify Dependencies Installed

```bash
docker-compose exec backend pip list | grep -E "mediapipe|librosa|fer|opencv|parselmouth|scikit-learn"
```

**Expected output:**
```
fer                  22.5.1
librosa              0.10.1
mediapipe            0.10.8
opencv-python        4.8.1.78
pillow               10.1.0
praat-parselmouth    0.4.3
scikit-learn         1.3.2
scipy                1.11.4
soundfile            0.12.1
```

---

## Step 6: Copy Integration Files (5 minutes)

### A. Ensure Dependency Files Present

These files should be copied from Week 1-3 deliverables into `backend/`:

```bash
# Verify files exist
ls -lh backend/visual_analysis.py
ls -lh backend/vocal_analysis.py
ls -lh backend/multimodal_integration_engine.py
```

**If files are missing:**
- Copy from Week 1, 2, 3 deliverable packages
- Ensure they're in the `backend/` directory
- Commit them to git

### B. Copy to Container (if needed)

```bash
# If files are outside container, copy them
docker cp backend/visual_analysis.py promo_analyzer_backend:/app/
docker cp backend/vocal_analysis.py promo_analyzer_backend:/app/
docker cp backend/multimodal_integration_engine.py promo_analyzer_backend:/app/
```

### C. Verify Files Accessible

```bash
docker-compose exec backend ls -lh /app/visual_analysis.py
docker-compose exec backend ls -lh /app/vocal_analysis.py
docker-compose exec backend ls -lh /app/multimodal_integration_engine.py
```

---

## Step 7: Update Backend Code (30 minutes)

### A. Update models.py

**Edit `backend/models.py`** and add new fields:

**To `Video` model:**
```python
# NEW: Visual analysis fields (Week 1)
visual_analysis = Column(JSON, default=list)  # Frame-by-frame data
visual_insights = Column(JSON, default=dict)  # Wrestling-specific insights

# NEW: Vocal analysis fields (Week 2)
vocal_analysis = Column(JSON, default=list)   # Audio segment data
vocal_insights = Column(JSON, default=dict)   # Wrestling-specific insights
```

**To `Analysis` model:**
```python
# NEW: Comprehensive multimodal analysis (Week 3)
comprehensive_data = Column(JSON, default=dict)

# NEW: Multimodal scores (0-100 scale)
congruence_score = Column(DECIMAL(5, 2), default=0.00)
authenticity_score = Column(DECIMAL(5, 2), default=0.00)
intensity_score = Column(DECIMAL(5, 2), default=0.00)
impact_score = Column(DECIMAL(5, 2), default=0.00)

# NEW: Jake Morrison grades (A to F)
character_grade = Column(String(3))
delivery_grade = Column(String(3))
psychology_grade = Column(String(3))
```

**Verify syntax:**
```bash
python -m py_compile backend/models.py
```

**Expected:** No output = success

### B. Update schemas.py

**Edit `backend/schemas.py`** and add new Pydantic models.

See `docs/05-api-documentation.md` for complete schemas:
- `VisualInsights`
- `VocalInsights`
- `ComprehensiveScores`
- `MomentFeedback`
- Updated `AnalysisResponse`
- Updated `VideoDetailResponse`
- `build_video_detail_response()` helper

**Verify syntax:**
```bash
python -m py_compile backend/schemas.py
```

**Expected:** No output = success

### C. Update tasks.py

**IMPORTANT:** This file has major changes. Recommended to:

1. **Backup original:**
   ```bash
   cp backend/tasks.py backend/tasks.py.original
   ```

2. **Review complete new version** in the provided documentation

3. **Copy complete new tasks.py** or manually add:
   - Import statements for visual_analysis, vocal_analysis, multimodal_integration_engine
   - Task 4: `analyze_visual()`
   - Task 5: `analyze_vocal()`
   - Task 6: `analyze_comprehensive()`
   - Updated Task 7: `analyze_with_jake()` (enhanced with comprehensive data)
   - Updated: `process_video_complete()` (7-task pipeline)

**Verify syntax:**
```bash
python -m py_compile backend/tasks.py
```

**Expected:** No output = success

### D. Test Imports

```bash
# Test all imports work
docker-compose exec backend python -c "
from visual_analysis import VisualAnalysisEngine
from vocal_analysis import VocalAnalysisEngine
from multimodal_integration_engine import MultiModalIntegrationEngine, ComprehensiveAnalysis
print('✅ All imports successful')
"
```

**Expected:** `✅ All imports successful`

---

## Step 8: Restart Services (5 minutes)

### A. Restart Celery Worker

```bash
docker-compose restart celery_worker
```

### B. Restart Backend

```bash
docker-compose restart backend
```

### C. Wait for Services to Start

```bash
# Wait 30 seconds for services to fully start
sleep 30

# Check service status
docker-compose ps
```

**Expected:** All services "Up" status

### D. Verify No Errors in Logs

```bash
# Check backend logs
docker-compose logs backend | tail -50
```

**Look for:**
- ✅ "Application startup complete"
- ✅ No import errors
- ✅ No database errors

```bash
# Check Celery logs
docker-compose logs celery_worker | tail -50
```

**Look for:**
- ✅ "celery@<hostname> ready"
- ✅ Tasks registered message
- ✅ No import errors

### E. Verify Tasks Registered

```bash
docker-compose exec celery_worker celery -A tasks inspect registered
```

**Expected tasks:**
- `tasks.analyze_visual` **[NEW]**
- `tasks.analyze_vocal` **[NEW]**
- `tasks.analyze_comprehensive` **[NEW]**
- `tasks.analyze_with_jake`
- `tasks.process_video_complete`
- `tasks.extract_metadata`
- `tasks.extract_audio`
- `tasks.transcribe_audio`
- `tasks.health_check`

---

## Step 9: Test Integration (30 minutes)

### A. Run Automated Test

```bash
# Ensure test video exists
ls -lh test_videos/sample_promo.mp4

# Run test script
python tests/test_multimodal_integration.py
```

**Expected:** All checks pass with ✅

### B. Manual Test - Upload Video

```bash
# Upload test video
curl -X POST -F "file=@test_videos/sample_promo.mp4" \
  http://localhost:8000/api/v1/videos/upload
```

**Expected:**
```json
{
  "video_id": "660e8400-...",
  "filename": "sample_promo.mp4",
  "status": "pending",
  "message": "Video uploaded successfully"
}
```

### C. Monitor Processing

```bash
VIDEO_ID="<video_id_from_upload>"

# Watch processing in real-time
docker-compose logs -f celery_worker
```

**Expected sequence:**
1. `[TASK 1/7] Extracting metadata`
2. `[TASK 2/7] Extracting audio`
3. `[TASK 3/7] Transcribing audio`
4. `[TASK 4/7] 🎥 Starting VISUAL ANALYSIS` **[NEW]**
5. `[TASK 5/7] 🎤 Starting VOCAL ANALYSIS` **[NEW]**
6. `[TASK 6/7] 🧠 Starting COMPREHENSIVE INTEGRATION` **[NEW]**
7. `[TASK 7/7] 🎭 Jake Morrison analyzing`

### D. Verify Results

```bash
# Wait for processing to complete (~2 minutes)

# Get video details
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.'

# Check visual insights exist
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.visual_insights'

# Check vocal insights exist
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.vocal_insights'

# Check comprehensive scores exist
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | \
  jq '.analyses[0] | {congruence_score, authenticity_score, intensity_score, impact_score}'

# Check grades exist
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | \
  jq '.analyses[0] | {character_grade, delivery_grade, psychology_grade}'
```

**Expected:** All fields populated with data (not null/empty).

---

## Step 10: Validation (15 minutes)

### A. Database Validation

```bash
# Check visual/vocal data stored
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     id,
     visual_analysis IS NOT NULL AND jsonb_array_length(visual_analysis) > 0 as has_visual,
     vocal_analysis IS NOT NULL AND jsonb_array_length(vocal_analysis) > 0 as has_vocal
   FROM videos
   WHERE status = 'completed'
   LIMIT 5;"
```

**Expected:** `has_visual` and `has_vocal` = `true`

```bash
# Check comprehensive scores stored
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     video_id,
     congruence_score,
     authenticity_score,
     character_grade,
     delivery_grade
   FROM analyses
   ORDER BY created_at DESC
   LIMIT 5;"
```

**Expected:** Scores between 0-100, grades A-F or NULL

### B. Performance Validation

```bash
# Check processing times
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     video_id,
     processing_time,
     created_at
   FROM analyses
   ORDER BY created_at DESC
   LIMIT 5;"
```

**Expected:** `processing_time` < 180000 (3 minutes in milliseconds)

### C. Jake Feedback Validation

```bash
# Get Jake's feedback
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | \
  jq -r '.analyses[0].detailed_feedback'
```

**Verify feedback includes:**
- Visual observations ("I saw...", "your face...")
- Vocal observations ("I heard...", "your voice...")
- Specific timestamps ("at 12.5s...")
- Money moments ("Everything aligned...")
- Breakdown moments ("Your words said X but...")

### D. No Regressions Check

```bash
# Test old video still accessible
OLD_VIDEO_ID="<video_id_from_before_integration>"
curl http://localhost:8000/api/v1/videos/$OLD_VIDEO_ID | jq '.status'

# Should return 200 OK with video details
```

---

## Step 11: Commit and Push (5 minutes)

### A. Commit Changes

```bash
# Add all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add multimodal integration (visual, vocal, comprehensive analysis)

- Add visual_analysis and visual_insights fields to Video model
- Add vocal_analysis and vocal_insights fields to Video model
- Add comprehensive_data and multimodal scores to Analysis model
- Add character_grade, delivery_grade, psychology_grade to Analysis model
- Implement analyze_visual task (Week 1 integration)
- Implement analyze_vocal task (Week 2 integration)
- Implement analyze_comprehensive task (Week 3 integration)
- Enhance analyze_with_jake task with multimodal data
- Update schemas for new API response fields
- Add database migration for new fields
- Update dependencies (opencv, mediapipe, librosa, etc.)

Processing pipeline now: 7 tasks (~98s total)
1. Extract metadata (~5s)
2. Extract audio (~10s)
3. Transcribe (~30s)
4. Analyze visual (~15s) [NEW]
5. Analyze vocal (~10s) [NEW]
6. Analyze comprehensive (~8s) [NEW]
7. Jake analysis (~20s) [ENHANCED]

Closes #[ISSUE_NUMBER]"
```

### B. Push to Remote

```bash
# Push feature branch
git push origin feature/multimodal-integration
```

### C. Create Pull Request (if using PR workflow)

- Go to GitHub/GitLab
- Create PR from `feature/multimodal-integration` to `main`
- Add description of changes
- Request review from team
- Wait for approval

**OR** merge directly if authorized:

```bash
git checkout main
git merge feature/multimodal-integration
git push origin main
```

---

## Step 12: Production Deployment (if applicable)

### If deploying to production (separate from staging):

```bash
# SSH into production server
ssh user@production-server

# Pull latest code
cd /path/to/promo-analyzer
git pull origin main

# Run same steps 1-10 on production
# ... (follow all steps above)

# Monitor production logs carefully
docker-compose logs -f
```

### Gradual Rollout Strategy (Optional)

1. **Deploy to staging first** - Test thoroughly
2. **Deploy to production** - During low-traffic period
3. **Monitor closely** - Watch logs for 1 hour
4. **Process test video** - Verify works in production
5. **Enable for all users** - If no issues

---

## Post-Deployment Checklist

After deployment is complete:

- [ ] Database migration applied successfully
- [ ] All new columns exist in database
- [ ] All indexes created
- [ ] Dependencies installed
- [ ] All three integration files present (visual, vocal, multimodal)
- [ ] Backend code updated (models, schemas, tasks)
- [ ] Services restarted
- [ ] All 7 tasks registered in Celery
- [ ] Test video processed successfully
- [ ] All tasks executed in correct order
- [ ] Visual analysis data in database
- [ ] Vocal analysis data in database
- [ ] Comprehensive scores calculated
- [ ] Grades assigned (when appropriate)
- [ ] API returns all new fields
- [ ] Jake's feedback is multimodal
- [ ] Processing time acceptable (<3 min)
- [ ] No errors in logs
- [ ] No regressions in existing functionality
- [ ] Old videos still accessible
- [ ] Code committed and pushed
- [ ] Team notified of successful deployment

---

## Rollback Procedure (if needed)

If critical issues arise:

### Immediate Rollback

```bash
# 1. Stop services
docker-compose down

# 2. Restore database
docker-compose up -d postgres
cat backups/backup_TIMESTAMP.sql | docker-compose exec -T postgres \
  psql -U promo_admin -d promo_analyzer

# 3. Restore code
git checkout HEAD~1  # or specific commit hash
cp backend/models.py.backup backend/models.py
cp backend/schemas.py.backup backend/schemas.py
cp backend/tasks.py.backup backend/tasks.py

# 4. Restart services
docker-compose up -d

# 5. Verify system works
curl http://localhost:8000/health
docker-compose logs -f
```

### Database-Only Rollback

If only database needs rollback:

```bash
docker cp migrations/001_rollback.sql promo_analyzer_postgres:/tmp/rollback.sql
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -f /tmp/rollback.sql
```

---

## Monitoring After Deployment

### First 24 Hours

Monitor these metrics:

```bash
# Check error rates
docker-compose logs backend | grep -i "error" | wc -l
docker-compose logs celery_worker | grep -i "error" | wc -l

# Check processing success rate
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     status,
     COUNT(*) as count
   FROM videos
   WHERE created_at > NOW() - INTERVAL '24 hours'
   GROUP BY status;"

# Check average processing time
docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
  "SELECT
     AVG(processing_time) / 1000 as avg_seconds,
     MAX(processing_time) / 1000 as max_seconds,
     COUNT(*) as total_processed
   FROM analyses
   WHERE created_at > NOW() - INTERVAL '24 hours';"
```

### Alert Conditions

Set up alerts for:
- ❌ Processing failure rate > 5%
- ❌ Average processing time > 180 seconds
- ❌ Error logs > 10 per hour
- ❌ Disk space < 1GB

---

## Next Steps After Deployment

1. **Update Frontend** - Add UI for new scores and grades
2. **User Documentation** - Update user guides with new features
3. **Team Training** - Train team on interpreting multimodal scores
4. **Performance Monitoring** - Track processing times and optimize
5. **User Feedback** - Gather feedback on Jake's enhanced analysis

---

## Support and Troubleshooting

For issues after deployment, see:
- [Troubleshooting Guide](04-troubleshooting.md)
- [Testing Guide](03-testing-guide.md)
- [API Documentation](05-api-documentation.md)

---

**Deployment Guide Complete**
**Last Updated:** 2025-11-15
**Version:** 1.0 - Multimodal Integration
