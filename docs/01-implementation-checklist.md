# Implementation Checklist

## 🎯 Overview

This checklist provides a phase-by-phase guide for integrating multimodal analysis capabilities into the Promo Analyzer system. Follow each phase in order.

**Estimated Total Time:** 2-3 hours for experienced backend developer

---

## Phase 1: Preparation (5 minutes)

### Tasks:
- [ ] **Backup database**
  ```bash
  docker-compose exec postgres pg_dump -U promo_admin promo_analyzer > backup_$(date +%Y%m%d_%H%M%S).sql
  ```

- [ ] **Create feature branch**
  ```bash
  git checkout -b feature/multimodal-integration
  ```

- [ ] **Verify all services running**
  ```bash
  docker-compose ps
  # All services should show "Up" status
  ```

- [ ] **Check disk space**
  ```bash
  df -h
  # Need ~2GB free for dependencies and processing
  ```

- [ ] **Backup current code**
  ```bash
  cp backend/models.py backend/models.py.backup
  cp backend/schemas.py backend/schemas.py.backup
  cp backend/tasks.py backend/tasks.py.backup
  ```

### Verification:
- Database backup file exists
- Feature branch created
- All Docker services running
- Sufficient disk space available
- Code backups created

---

## Phase 2: Database Migration (10 minutes)

### Tasks:
- [ ] **Review migration script**
  - Open `migrations/001_add_multimodal_fields.sql`
  - Understand what columns are being added
  - Review constraints and indexes

- [ ] **Copy migration to Docker container**
  ```bash
  docker cp migrations/001_add_multimodal_fields.sql \
    promo_analyzer_postgres:/tmp/migration.sql
  ```

- [ ] **Apply migration**
  ```bash
  docker-compose exec postgres psql -U promo_admin -d promo_analyzer \
    -f /tmp/migration.sql
  ```

- [ ] **Verify new columns exist**
  ```bash
  # Check videos table
  docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ videos"

  # Check analyses table
  docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c "\d+ analyses"
  ```

- [ ] **Test rollback procedure** (optional, in test environment)
  ```bash
  docker cp migrations/001_rollback.sql promo_analyzer_postgres:/tmp/rollback.sql
  docker-compose exec postgres psql -U promo_admin -d promo_analyzer -f /tmp/rollback.sql
  # Then re-apply migration
  ```

### Verification:
- Migration executes without errors
- `videos` table has: `visual_analysis`, `visual_insights`, `vocal_analysis`, `vocal_insights`
- `analyses` table has: `comprehensive_data`, `congruence_score`, `authenticity_score`, `intensity_score`, `impact_score`, `character_grade`, `delivery_grade`, `psychology_grade`
- Indexes created successfully
- Constraints applied correctly

---

## Phase 3: Code Integration (45 minutes)

### Part A: Update Models (10 minutes)

- [ ] **Open `backend/models.py`**

- [ ] **Add new fields to `Video` model:**
  ```python
  # NEW: Visual analysis fields (Week 1)
  visual_analysis = Column(JSON, default=list)
  visual_insights = Column(JSON, default=dict)

  # NEW: Vocal analysis fields (Week 2)
  vocal_analysis = Column(JSON, default=list)
  vocal_insights = Column(JSON, default=dict)
  ```

- [ ] **Add new fields to `Analysis` model:**
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

- [ ] **Save and verify syntax**
  ```bash
  python -m py_compile backend/models.py
  ```

### Part B: Update Schemas (15 minutes)

- [ ] **Open `backend/schemas.py`**

- [ ] **Add new Pydantic models:**
  - [ ] `VisualInsights`
  - [ ] `VocalInsights`
  - [ ] `ComprehensiveScores`
  - [ ] `MomentFeedback`

- [ ] **Update `AnalysisResponse` to include:**
  - [ ] `congruence_score`
  - [ ] `authenticity_score`
  - [ ] `intensity_score`
  - [ ] `impact_score`
  - [ ] `character_grade`
  - [ ] `delivery_grade`
  - [ ] `psychology_grade`
  - [ ] `comprehensive_data`
  - [ ] `moment_by_moment`

- [ ] **Update `VideoDetailResponse` to include:**
  - [ ] `visual_insights`
  - [ ] `vocal_insights`

- [ ] **Add `build_video_detail_response` helper function**

- [ ] **Save and verify syntax**
  ```bash
  python -m py_compile backend/schemas.py
  ```

### Part C: Update Tasks (20 minutes)

- [ ] **Copy dependency files to backend/**
  - [ ] `visual_analysis.py` (from Week 1)
  - [ ] `vocal_analysis.py` (from Week 2)
  - [ ] `multimodal_integration_engine.py` (from Week 3)

- [ ] **Verify dependency files exist**
  ```bash
  ls -lh backend/visual_analysis.py
  ls -lh backend/vocal_analysis.py
  ls -lh backend/multimodal_integration_engine.py
  ```

- [ ] **Replace `backend/tasks.py`** with complete version
  - Backup already created in Phase 1
  - Copy new tasks.py from `backend/tasks.py.new`

- [ ] **Review new tasks in tasks.py:**
  - [ ] Task 4: `analyze_visual` (NEW)
  - [ ] Task 5: `analyze_vocal` (NEW)
  - [ ] Task 6: `analyze_comprehensive` (NEW)
  - [ ] Task 7: `analyze_with_jake` (ENHANCED)
  - [ ] Updated: `process_video_complete` (7-task pipeline)

- [ ] **Verify imports at top of tasks.py**
  ```python
  from visual_analysis import VisualAnalysisEngine
  from vocal_analysis import VocalAnalysisEngine
  from multimodal_integration_engine import (
      MultiModalIntegrationEngine,
      ComprehensiveAnalysis
  )
  ```

### Part D: Update Dependencies (5 minutes)

- [ ] **Update `backend/requirements.txt`** with new dependencies:
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

- [ ] **Install dependencies**
  ```bash
  docker-compose exec backend pip install -r requirements.txt
  # OR rebuild container:
  docker-compose build backend
  ```

### Verification:
- All Python files compile without syntax errors
- All dependency files present
- Dependencies installed successfully
- No import errors when importing tasks

---

## Phase 4: Service Restart (5 minutes)

### Tasks:
- [ ] **Restart Celery worker**
  ```bash
  docker-compose restart celery_worker
  ```

- [ ] **Restart backend**
  ```bash
  docker-compose restart backend
  ```

- [ ] **Wait for services to be ready** (30 seconds)

- [ ] **Verify no errors in backend logs**
  ```bash
  docker-compose logs backend | tail -50
  # Look for import errors or startup failures
  ```

- [ ] **Verify no errors in Celery logs**
  ```bash
  docker-compose logs celery_worker | tail -50
  # Should see "Tasks registered" message
  ```

- [ ] **Check registered Celery tasks**
  ```bash
  docker-compose exec celery_worker celery -A tasks inspect registered
  # Should show: analyze_visual, analyze_vocal, analyze_comprehensive
  ```

- [ ] **Test health endpoint**
  ```bash
  curl http://localhost:8000/health
  # Should return healthy status
  ```

### Verification:
- Services restarted successfully
- No import errors in logs
- All new tasks registered in Celery
- Health endpoint responding

---

## Phase 5: Testing (30 minutes)

### Part A: Prepare Test Video (5 minutes)

- [ ] **Create test videos directory**
  ```bash
  mkdir -p test_videos
  ```

- [ ] **Place a test video** in `test_videos/sample_promo.mp4`
  - Use a short promo (30-90 seconds recommended for testing)
  - Ensure it has clear audio and visual content

### Part B: Run Integration Test (20 minutes)

- [ ] **Run automated test script**
  ```bash
  python tests/test_multimodal_integration.py
  ```

- [ ] **Monitor test progress**
  - Upload should succeed
  - Processing should show all 7 tasks
  - Should complete in ~2-3 minutes for short video

- [ ] **If test fails, check:**
  ```bash
  # Celery worker logs
  docker-compose logs -f celery_worker

  # Backend logs
  docker-compose logs -f backend

  # Database for error state
  docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
    "SELECT id, status FROM videos ORDER BY created_at DESC LIMIT 5;"
  ```

### Part C: Manual Verification (5 minutes)

- [ ] **Check database for new data**
  ```bash
  docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
    "SELECT
       visual_analysis IS NOT NULL as has_visual,
       vocal_analysis IS NOT NULL as has_vocal,
       visual_insights IS NOT NULL as has_visual_insights,
       vocal_insights IS NOT NULL as has_vocal_insights
     FROM videos
     WHERE status = 'completed'
     LIMIT 1;"
  ```

- [ ] **Check comprehensive analysis data**
  ```bash
  docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
    "SELECT
       congruence_score,
       authenticity_score,
       intensity_score,
       impact_score,
       character_grade,
       delivery_grade,
       psychology_grade
     FROM analyses
     ORDER BY created_at DESC
     LIMIT 1;"
  ```

- [ ] **Retrieve full analysis via API**
  ```bash
  # Get video ID from test output, then:
  curl http://localhost:8000/api/v1/videos/{VIDEO_ID} | jq '.'
  ```

### Verification:
- Test script passes all checks
- Database contains visual_analysis and vocal_analysis data
- Database contains comprehensive_data with scores
- API returns all new fields
- Jake's feedback references multimodal observations

---

## Phase 6: Validation (15 minutes)

### Tasks:
- [ ] **Review comprehensive analysis output**
  - Check that congruence_score is calculated (0-100)
  - Check that authenticity_score is calculated (0-100)
  - Check that grades are assigned (A-F) or NULL
  - Verify moment_by_moment feedback exists

- [ ] **Review Jake's enhanced feedback**
  - Should reference visual observations ("I saw...")
  - Should reference vocal observations ("I heard...")
  - Should identify specific timestamps
  - Should call out money moments (alignment)
  - Should call out breakdown moments (contradictions)

- [ ] **Check performance metrics**
  ```bash
  # Check processing time from analyses table
  docker-compose exec postgres psql -U promo_admin -d promo_analyzer -c \
    "SELECT
       video_id,
       processing_time,
       overall_score
     FROM analyses
     ORDER BY created_at DESC
     LIMIT 5;"
  ```
  - Should be under 180 seconds (3 minutes) for short videos

- [ ] **Confirm no regressions**
  - Old videos still viewable
  - Existing analyses still accessible
  - No broken endpoints
  - No database errors

- [ ] **Document any issues**
  - Create GitHub issues for bugs
  - Note performance bottlenecks
  - Record edge cases discovered

### Verification:
- All scores within expected ranges (0-100)
- Grades make sense (A-F or NULL)
- Jake's feedback is comprehensive and multimodal
- Processing time acceptable
- No regressions in existing functionality

---

## Post-Integration Checklist

After all phases complete, verify:

- [ ] Database migration applied successfully
- [ ] All new fields present in database
- [ ] Models updated with new columns
- [ ] Schemas updated with new response models
- [ ] Tasks.py includes all 7 tasks
- [ ] Dependencies installed
- [ ] Services restarted and healthy
- [ ] Test video processes successfully
- [ ] All 7 tasks execute in sequence
- [ ] Visual analysis data stored in database
- [ ] Vocal analysis data stored in database
- [ ] Comprehensive scores calculated
- [ ] Grades assigned (when appropriate)
- [ ] API returns all new fields
- [ ] Jake's feedback is multimodal
- [ ] Processing time under 3 minutes
- [ ] No errors in logs
- [ ] No regressions in existing features

---

## Rollback Procedure

If critical issues arise, execute rollback:

```bash
# 1. Stop services
docker-compose down

# 2. Restore database from backup
docker-compose up -d postgres
cat backup_TIMESTAMP.sql | docker-compose exec -T postgres \
  psql -U promo_admin -d promo_analyzer

# 3. Restore code
git checkout HEAD~1  # or specific commit
cp backend/models.py.backup backend/models.py
cp backend/schemas.py.backup backend/schemas.py
cp backend/tasks.py.backup backend/tasks.py

# 4. Restart services
docker-compose up -d

# 5. Verify system works
curl http://localhost:8000/health
```

---

## Success Criteria

Integration is **100% successful** when:

1. ✅ All 7 tasks execute without errors
2. ✅ Database contains visual_analysis, vocal_analysis, comprehensive_data
3. ✅ API returns congruence_score, authenticity_score, intensity_score, impact_score
4. ✅ API returns character_grade, delivery_grade, psychology_grade
5. ✅ Jake's feedback references visual and vocal observations
6. ✅ Moment-by-moment feedback includes alignment/contradiction detection
7. ✅ Processing time remains under 3 minutes for 5-minute videos
8. ✅ No regressions in existing functionality
9. ✅ Automated test script passes
10. ✅ Manual validation confirms data quality

---

## Next Steps After Integration

Once checklist is complete:

1. **Update Frontend** - Display new scores and grades in UI
2. **Enhance Jake Prompt** - Refine multimodal observation templates
3. **User Testing** - Test with real wrestling promos
4. **Performance Optimization** - Profile and optimize bottlenecks
5. **Documentation** - Update user guides and API docs

---

**Estimated Total Time:** 2-3 hours
**Last Updated:** 2025-11-15
