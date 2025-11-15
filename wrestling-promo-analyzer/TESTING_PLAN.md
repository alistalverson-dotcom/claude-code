# Wrestling Promo Analyzer - Testing & Validation Plan

**Sprint:** Testing & Validation
**Duration:** 3-5 days
**Date Started:** 2025-11-15
**Status:** In Progress

## Objectives

1. ✅ Validate complete multimodal pipeline functionality
2. ✅ Test enhanced visual analysis accuracy
3. ✅ Verify frontend components render correctly
4. ✅ Identify and fix integration issues
5. ✅ Measure performance and costs
6. ✅ Ensure production readiness

---

## Testing Scope

### Backend Testing
- [ ] Enhanced visual analysis module
- [ ] Frame extraction pipeline
- [ ] Multimodal Claude integration
- [ ] Database schema and migrations
- [ ] Celery task queue
- [ ] Error handling and edge cases

### Frontend Testing
- [ ] Visual analysis components
- [ ] Type safety and TypeScript
- [ ] Responsive design
- [ ] Data rendering accuracy
- [ ] Loading states and skeletons
- [ ] Error states

### Integration Testing
- [ ] End-to-end video processing
- [ ] API data flow
- [ ] Real video analysis
- [ ] Multiple video scenarios

### Performance Testing
- [ ] Processing time benchmarks
- [ ] Memory usage profiling
- [ ] API cost analysis
- [ ] Database query performance

---

## Test Cases

### 1. Enhanced Visual Analysis Module

#### Test: Emotion Classification
**Input:** Frame with facial landmarks
**Expected:**
- Valid emotion scores (0-1 range)
- Dominant emotion identified
- Emotional consistency calculated

#### Test: Eye Contact Detection
**Input:** Frame with face and iris landmarks
**Expected:**
- Eye contact score (0-1 range)
- Gaze direction classified
- Quality rating assigned

#### Test: Gesture Recognition
**Input:** Frame with hand landmarks
**Expected:**
- Gesture type identified
- Count incremented
- Effectiveness scored

#### Test: Posture Analysis
**Input:** Frame with pose landmarks
**Expected:**
- Posture type classified
- Power pose detected
- Openness score calculated

#### Test: Camera Framing
**Input:** Frame with face bounding box
**Expected:**
- Shot type classified
- Rule of thirds evaluated
- Headroom assessed
- Composition scored

#### Test: Aggregation
**Input:** Multiple frame analyses
**Expected:**
- Normalized emotion breakdown
- Average eye contact score
- Power pose ratio
- Top gestures list
- Dominant shot type

---

### 2. Multimodal Pipeline Integration

#### Test: Frame Extraction Task
**Input:** Video file (MP4, 30 seconds)
**Expected:**
- Frames extracted at 3-second intervals (~10 frames)
- Scene change scores calculated
- Motion levels computed
- Key frames selected
- Frames saved to database

#### Test: Enhanced Analysis in Pipeline
**Input:** Extracted frames
**Expected:**
- Enhanced analysis runs on all frames
- Results stored in frame records
- Enhanced summary generated
- Data passed to Claude prompt

#### Test: Multimodal Prompt Building
**Input:** Enhanced visual summary
**Expected:**
- Visual context included in prompt
- Emotion breakdown formatted
- Gestures listed
- Metrics displayed

#### Test: Visual Analysis Saving
**Input:** Claude response with visual data
**Expected:**
- VisualAnalysis record created
- Scores saved correctly
- JSONB fields populated
- Relationship to Analysis established

---

### 3. Database Schema Validation

#### Test: Frame Model
- [ ] All fields save correctly
- [ ] Foreign key to Video works
- [ ] JSONB fields store complex data
- [ ] Indexes perform well

#### Test: VisualAnalysis Model
- [ ] All fields save correctly
- [ ] Foreign key to Analysis works
- [ ] JSONB fields store complex data
- [ ] One-to-one relationship enforced

#### Test: Migrations
- [ ] Migration 004 runs successfully
- [ ] Tables created with correct schema
- [ ] Indexes created
- [ ] No data loss on upgrade

---

### 4. Frontend Component Testing

#### Test: EmotionBreakdownChart
**Input:** `{"confident": 0.6, "intense": 0.3, "neutral": 0.1}`
**Expected:**
- 3 emotion bars displayed
- Sorted by percentage (descending)
- Correct icons shown
- Percentages calculated correctly

#### Test: GestureAnalysisCard
**Input:** `[{"gesture": "pointing", "count": 5, "effectiveness": 0.85}]`
**Expected:**
- Gesture displayed with icon
- Count shown correctly
- Effectiveness color-coded
- Proper formatting

#### Test: VisualPerformanceMetrics
**Input:** `{facialExpression: 87, bodyLanguage: 90}`
**Expected:**
- 2 metric cards displayed
- Scores shown as X/100
- Color-coded by score range
- Icons displayed

#### Test: ProductionQualityCard
**Input:** `{lighting: 0.85, framing: 0.90, background: 0.80}`
**Expected:**
- 3 quality metrics displayed
- Percentages calculated
- Qualitative labels shown
- Colors match quality

#### Test: TimestampedFeedbackList with Visual Elements
**Input:** `[{timestamp: "00:15", comment: "Great eye contact", type: "positive", visual_element: "eye_contact"}]`
**Expected:**
- Visual element badge shown
- Correct icon displayed
- Label formatted properly

#### Test: VideoDetailPage Integration
**Input:** Analysis with visual data
**Expected:**
- Visual Performance section renders
- All components displayed
- Conditional rendering works
- No TypeScript errors

---

### 5. End-to-End Integration Tests

#### Test Scenario 1: High-Quality Video
**Input:** Professional wrestling promo (720p+, good lighting, clear audio)
**Expected:**
- Processing completes successfully
- High visual scores (80+)
- Multiple emotions detected
- Gestures recognized
- Good production quality scores

#### Test Scenario 2: Low-Quality Video
**Input:** Amateur promo (low resolution, poor lighting, echo)
**Expected:**
- Processing completes successfully
- Lower visual scores (40-60)
- Fewer emotions detected
- Lower production quality scores
- Appropriate feedback given

#### Test Scenario 3: No Face Visible
**Input:** Video where wrestler is not on camera
**Expected:**
- Processing completes successfully
- Graceful handling of missing face data
- Lower facial expression scores
- Appropriate error handling

#### Test Scenario 4: Text-Only Fallback
**Input:** Frame extraction fails
**Expected:**
- Pipeline continues with text-only
- No visual analysis section in frontend
- Standard 6 category scores only
- User sees appropriate message

---

### 6. Performance Benchmarks

#### Target Metrics

**Processing Time:**
- 30-second video: < 2 minutes total
  - Metadata extraction: < 5 seconds
  - Frame extraction: < 15 seconds
  - Audio extraction: < 10 seconds
  - Transcription: < 30 seconds
  - Multimodal analysis: < 60 seconds

**API Costs:**
- Text-only analysis: $0.01-0.02 per video
- Multimodal analysis: $0.03-0.05 per video

**Memory Usage:**
- Peak memory: < 2GB per video
- Frame storage: < 10MB per video

**Database Performance:**
- Video detail query: < 100ms
- Analysis list query: < 200ms

---

## Test Environment Setup

### Backend
```bash
# Install test dependencies
cd wrestling-promo-analyzer/backend
pip install pytest pytest-cov pytest-asyncio

# Run database migrations
python manage.py migrate

# Start services
docker-compose up -d redis postgres
celery -A tasks worker --loglevel=info
```

### Frontend
```bash
# Install dependencies
cd wrestling-promo-analyzer/frontend
npm install

# Run dev server
npm run dev

# Run type checking
npm run type-check
```

---

## Test Data Requirements

### Sample Videos
1. **High-quality promo:** Professional wrestler, good production
2. **Low-quality promo:** Amateur, webcam quality
3. **Edge case 1:** No face visible
4. **Edge case 2:** Multiple people in frame
5. **Edge case 3:** Very short video (< 10 seconds)
6. **Edge case 4:** Long video (> 5 minutes)

### Mock Data
- Sample emotion breakdowns
- Sample gesture arrays
- Sample production quality objects
- Sample analysis responses

---

## Success Criteria

### Must Pass
- ✅ All core functionality works end-to-end
- ✅ No critical bugs that prevent usage
- ✅ Database schema correctly implemented
- ✅ Frontend components render without errors
- ✅ Visual analysis integrates with Claude

### Should Pass
- ✅ Processing time within target metrics
- ✅ API costs within budget
- ✅ Graceful error handling for edge cases
- ✅ Good user experience on mobile

### Nice to Have
- ✅ Performance optimizations identified
- ✅ UI/UX improvements noted
- ✅ Future enhancement ideas documented

---

## Bug Tracking

### Critical Bugs
*None identified yet*

### Major Bugs
*None identified yet*

### Minor Bugs
*None identified yet*

### Enhancements
*To be documented during testing*

---

## Testing Progress

- [ ] **Day 1: Backend Testing** (In Progress)
  - [x] Testing plan created
  - [ ] Enhanced visual analysis unit tests
  - [ ] Pipeline integration tests
  - [ ] Database schema validation

- [ ] **Day 2: Frontend Testing**
  - [ ] Component unit tests
  - [ ] Type safety validation
  - [ ] Responsive design testing
  - [ ] Mock data integration

- [ ] **Day 3: Integration & Performance**
  - [ ] End-to-end tests with real videos
  - [ ] Performance benchmarking
  - [ ] Cost analysis
  - [ ] Bug fixes and refinements

---

## Notes

- Testing will be done iteratively
- Bugs will be fixed as discovered
- Performance optimizations will be noted for future sprints
- User feedback mechanisms to be considered

---

**Last Updated:** 2025-11-15
**Next Review:** End of Day 1
