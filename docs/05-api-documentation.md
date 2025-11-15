# API Documentation - Multimodal Integration

## Overview

This document describes the API changes for multimodal integration. All new fields are **additive** - existing fields remain unchanged.

---

## Database Model Changes

### Video Model (models.py)

**NEW FIELDS:**

```python
class Video(Base):
    # ... existing fields ...

    # NEW: Visual analysis fields (Week 1)
    visual_analysis = Column(JSON, default=list)  # Frame-by-frame data
    visual_insights = Column(JSON, default=dict)  # Wrestling-specific insights

    # NEW: Vocal analysis fields (Week 2)
    vocal_analysis = Column(JSON, default=list)   # Audio segment data
    vocal_insights = Column(JSON, default=dict)   # Wrestling-specific insights
```

**Field Descriptions:**

| Field | Type | Description | Example Data |
|-------|------|-------------|--------------|
| `visual_analysis` | JSONB Array | Frame-by-frame visual analysis data | `[{"timestamp": 0.0, "facial_emotion": "confident", ...}, ...]` |
| `visual_insights` | JSONB Object | Aggregated visual scores and insights | `{"conviction_score": 85.5, "intensity_score": 78.2, ...}` |
| `vocal_analysis` | JSONB Array | Audio segment vocal analysis data | `[{"start_time": 0.0, "pitch": 220.5, ...}, ...]` |
| `vocal_insights` | JSONB Object | Aggregated vocal scores and insights | `{"vocal_conviction_score": 82.0, ...}` |

### Analysis Model (models.py)

**NEW FIELDS:**

```python
class Analysis(Base):
    # ... existing fields ...

    # NEW: Comprehensive multimodal analysis (Week 3)
    comprehensive_data = Column(JSON, default=dict)  # Complete ComprehensiveAnalysis

    # NEW: Multimodal scores (0-100 scale)
    congruence_score = Column(DECIMAL(5, 2), default=0.00)      # Face+Voice+Words alignment
    authenticity_score = Column(DECIMAL(5, 2), default=0.00)    # Believability
    intensity_score = Column(DECIMAL(5, 2), default=0.00)       # Energy level
    impact_score = Column(DECIMAL(5, 2), default=0.00)          # Predicted audience reaction

    # NEW: Jake Morrison grades (A to F)
    character_grade = Column(String(3))      # Character work grade
    delivery_grade = Column(String(3))       # Delivery grade
    psychology_grade = Column(String(3))     # Psychology grade
```

**Field Descriptions:**

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `comprehensive_data` | JSONB Object | N/A | Complete multimodal analysis including money moments, breakdowns |
| `congruence_score` | DECIMAL(5,2) | 0-100 | How well facial expression, vocal tone, and words align |
| `authenticity_score` | DECIMAL(5,2) | 0-100 | How genuine and believable the performance feels |
| `intensity_score` | DECIMAL(5,2) | 0-100 | Overall energy and commitment level |
| `impact_score` | DECIMAL(5,2) | 0-100 | Predicted strength of audience reaction |
| `character_grade` | VARCHAR(3) | A to F | Jake's grade for character work (A, A-, B+, B, B-, C+, C, C-, D, F) |
| `delivery_grade` | VARCHAR(3) | A to F | Jake's grade for delivery execution |
| `psychology_grade` | VARCHAR(3) | A to F | Jake's grade for psychological storytelling |

---

## API Response Schemas (schemas.py)

### VisualInsights

**Purpose:** Aggregated visual analysis scores

```python
class VisualInsights(BaseModel):
    conviction_score: float  # 0-100
    intensity_score: float  # 0-100
    eye_contact_score: float  # 0-100
    body_language_score: float  # 0-100
    peak_moments: List[Dict[str, Any]]  # Timestamps of strongest visual moments
    weaknesses: List[Dict[str, Any]]  # Visual breakdown moments
    recommendations: List[str]  # Visual improvement suggestions
```

**Example:**
```json
{
  "conviction_score": 85.5,
  "intensity_score": 78.2,
  "eye_contact_score": 92.0,
  "body_language_score": 80.3,
  "peak_moments": [
    {
      "timestamp": 12.5,
      "emotion": "anger",
      "intensity": 95.2,
      "description": "Peak intensity - powerful facial expression"
    }
  ],
  "weaknesses": [
    {
      "timestamp": 45.2,
      "issue": "eye_contact_drop",
      "description": "Eyes wandered off camera"
    }
  ],
  "recommendations": [
    "Maintain eye contact during key statements",
    "Use more varied facial expressions"
  ]
}
```

### VocalInsights

**Purpose:** Aggregated vocal analysis scores

```python
class VocalInsights(BaseModel):
    vocal_conviction_score: float  # 0-100
    vocal_intensity_score: float  # 0-100
    speaking_confidence_score: float  # 0-100
    pacing_score: float  # 0-100
    vocal_variety_score: float  # 0-100
    best_moments: List[Dict[str, Any]]  # Timestamps of strongest vocal moments
    weaknesses: List[str]  # Vocal issues
    recommendations: List[str]  # Vocal improvement suggestions
```

**Example:**
```json
{
  "vocal_conviction_score": 82.0,
  "vocal_intensity_score": 88.5,
  "speaking_confidence_score": 85.0,
  "pacing_score": 75.5,
  "vocal_variety_score": 70.0,
  "best_moments": [
    {
      "timestamp": 12.5,
      "pitch_mean": 220.5,
      "volume_mean": 0.85,
      "description": "Strong vocal projection with emotional range"
    }
  ],
  "weaknesses": [
    "Monotone delivery during middle section",
    "Volume drops at end of sentences"
  ],
  "recommendations": [
    "Increase pitch variation during key points",
    "Maintain volume through full statements"
  ]
}
```

### MomentFeedback

**Purpose:** Timestamp-specific multimodal feedback

```python
class MomentFeedback(BaseModel):
    timestamp: float  # Seconds into video
    duration: float  # Duration of moment in seconds
    category: str  # "money_moment", "breakdown", "neutral"
    visual_signal: str  # What the face showed
    vocal_signal: str  # What the voice conveyed
    linguistic_signal: str  # What the words said
    alignment: str  # "aligned", "contradictory", "partial"
    jake_observation: str  # Jake's specific feedback for this moment
```

**Example:**
```json
{
  "timestamp": 12.5,
  "duration": 3.2,
  "category": "money_moment",
  "visual_signal": "intense anger, clenched jaw, piercing eye contact",
  "vocal_signal": "raised volume, aggressive tone, pitch elevation",
  "linguistic_signal": "\"You don't deserve to be in the same ring as me!\"",
  "alignment": "aligned",
  "jake_observation": "MONEY MOMENT at 12.5s - Everything aligned perfectly. Your face, voice, and words all screamed pure rage. This is what conviction looks like."
}
```

### AnalysisResponse (UPDATED)

**NEW FIELDS ADDED:**

```python
class AnalysisResponse(BaseModel):
    # ... existing fields ...

    # NEW: Multimodal scores
    congruence_score: Optional[Decimal]
    authenticity_score: Optional[Decimal]
    intensity_score: Optional[Decimal]
    impact_score: Optional[Decimal]

    # NEW: Grades
    character_grade: Optional[str]
    delivery_grade: Optional[str]
    psychology_grade: Optional[str]

    # NEW: Comprehensive data
    comprehensive_data: Dict[str, Any] = {}
    moment_by_moment: List[MomentFeedback] = []
```

**Complete Example Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "video_id": "660e8400-e29b-41d4-a716-446655440001",
  "judge_name": "Jake Morrison",

  "overall_score": 85.5,
  "psychology_score": 88.0,
  "character_score": 82.0,
  "delivery_score": 87.5,
  "structure_score": 80.0,
  "crowd_connection_score": 90.0,
  "originality_score": 75.0,

  "congruence_score": 84.2,
  "authenticity_score": 86.5,
  "intensity_score": 88.8,
  "impact_score": 87.0,

  "character_grade": "B+",
  "delivery_grade": "A-",
  "psychology_grade": "A",

  "detailed_feedback": "Listen kid, I saw real commitment at 12.5s when your face, voice, and words all screamed rage...",

  "strengths": [
    "Exceptional eye contact throughout (92/100)",
    "Strong vocal conviction during key moments",
    "Perfect alignment at 12.5s, 34.2s, 58.7s"
  ],

  "weaknesses": [
    "Monotone delivery 45-55s where words said one thing but voice was flat",
    "Eye contact dropped at 23.4s during critical statement",
    "Volume inconsistency hurt believability"
  ],

  "recommendations": [
    "Work on maintaining vocal intensity through full statements",
    "Practice pitch variation for emotional range",
    "Keep eye contact locked during power statements"
  ],

  "comprehensive_data": {
    "money_moments": [...],
    "breakdown_moments": [...],
    "peak_intensity_moments": [...],
    "jake_priorities": [...]
  },

  "moment_by_moment": [
    {
      "timestamp": 12.5,
      "duration": 3.2,
      "category": "money_moment",
      "visual_signal": "intense anger, clenched jaw",
      "vocal_signal": "raised volume, aggressive tone",
      "linguistic_signal": "\"You don't deserve to be in the same ring as me!\"",
      "alignment": "aligned",
      "jake_observation": "MONEY MOMENT - Everything aligned perfectly..."
    },
    ...
  ],

  "created_at": "2025-11-15T10:30:00Z",
  "processing_time": 98000
}
```

### VideoDetailResponse (UPDATED)

**NEW FIELDS ADDED:**

```python
class VideoDetailResponse(BaseModel):
    # ... existing fields ...

    # NEW: Visual insights
    visual_insights: Optional[VisualInsights] = None

    # NEW: Vocal insights
    vocal_insights: Optional[VocalInsights] = None

    # Analyses now include comprehensive data
    analyses: List[AnalysisResponse] = []
```

---

## API Endpoints

### GET /api/v1/videos/{video_id}

**Purpose:** Retrieve complete video details with all analysis

**Response Changes:**
- Added `visual_insights` object
- Added `vocal_insights` object
- `analyses` array now includes:
  - `congruence_score`, `authenticity_score`, `intensity_score`, `impact_score`
  - `character_grade`, `delivery_grade`, `psychology_grade`
  - `comprehensive_data` object
  - `moment_by_moment` array

**Example Request:**
```bash
curl http://localhost:8000/api/v1/videos/660e8400-e29b-41d4-a716-446655440001
```

**Example Response (New Fields Only):**
```json
{
  "id": "660e8400-e29b-41d4-a716-446655440001",
  "original_filename": "my_promo.mp4",
  "status": "completed",
  ...

  "visual_insights": {
    "conviction_score": 85.5,
    "intensity_score": 78.2,
    "eye_contact_score": 92.0,
    "body_language_score": 80.3,
    ...
  },

  "vocal_insights": {
    "vocal_conviction_score": 82.0,
    "vocal_intensity_score": 88.5,
    "speaking_confidence_score": 85.0,
    ...
  },

  "analyses": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "judge_name": "Jake Morrison",
      "congruence_score": 84.2,
      "authenticity_score": 86.5,
      "intensity_score": 88.8,
      "impact_score": 87.0,
      "character_grade": "B+",
      "delivery_grade": "A-",
      "psychology_grade": "A",
      "moment_by_moment": [...],
      ...
    }
  ]
}
```

---

## Processing Status

Videos now go through 7 processing stages:

| Status Value | Description | Duration |
|-------------|-------------|----------|
| `pending` | Upload complete, waiting to process | - |
| `processing` | Video is being processed | ~98s total |
| `completed` | All analysis complete | - |
| `failed` | Processing encountered error | - |

**Task Breakdown:**
1. `extract_metadata` - Extract video properties (~5s)
2. `extract_audio` - Extract audio track (~10s)
3. `transcribe_audio` - Whisper transcription (~30s)
4. `analyze_visual` - Visual analysis (~15s) **[NEW]**
5. `analyze_vocal` - Vocal analysis (~10s) **[NEW]**
6. `analyze_comprehensive` - Multimodal integration (~8s) **[NEW]**
7. `analyze_with_jake` - Jake Morrison feedback (~20s) **[ENHANCED]**

---

## Score Interpretation Guide

### Congruence Score (0-100)

How well facial expression, vocal tone, and linguistic content align:

- **90-100:** Perfect alignment - "Money" performance
- **80-89:** Strong alignment - Minor inconsistencies
- **70-79:** Good alignment - Some contradictions
- **60-69:** Moderate alignment - Noticeable gaps
- **< 60:** Poor alignment - Face/voice/words contradict

### Authenticity Score (0-100)

How genuine and believable the performance feels:

- **90-100:** Exceptionally authentic - Pure believability
- **80-89:** Very authentic - Highly believable
- **70-79:** Authentic - Generally believable
- **60-69:** Somewhat authentic - Some artificial moments
- **< 60:** Inauthentic - Feels forced or fake

### Intensity Score (0-100)

Overall energy and commitment level:

- **90-100:** Extreme intensity - Maximum commitment
- **80-89:** High intensity - Strong energy
- **70-79:** Good intensity - Solid energy
- **60-69:** Moderate intensity - Adequate energy
- **< 60:** Low intensity - Lacking energy

### Impact Score (0-100)

Predicted strength of audience reaction:

- **90-100:** Huge impact - Crowd will explode
- **80-89:** Strong impact - Crowd will respond well
- **70-79:** Good impact - Solid crowd reaction
- **60-69:** Moderate impact - Decent response
- **< 60:** Low impact - Weak crowd reaction

### Grade Scale (A to F)

Jake Morrison's traditional wrestling grades:

- **A:** Excellent - Professional level
- **A-:** Very good - Near professional
- **B+:** Good - Above average
- **B:** Solid - Average
- **B-:** Below average - Needs work
- **C+/C/C-:** Poor - Significant issues
- **D:** Very poor - Major problems
- **F:** Failing - Fundamentally broken
- **NULL:** Not graded (brief promos, insufficient data)

---

## Migration Compatibility

### Backward Compatibility

- ✅ **Existing videos** will have new fields set to defaults:
  - `visual_analysis`: `[]` (empty array)
  - `visual_insights`: `{}` (empty object)
  - `vocal_analysis`: `[]` (empty array)
  - `vocal_insights`: `{}` (empty object)

- ✅ **Existing analyses** will have new fields set to defaults:
  - `comprehensive_data`: `{}` (empty object)
  - `congruence_score`: `0.00`
  - `authenticity_score`: `0.00`
  - `intensity_score`: `0.00`
  - `impact_score`: `0.00`
  - `character_grade`: `NULL`
  - `delivery_grade`: `NULL`
  - `psychology_grade`: `NULL`

- ✅ **API responses** include all fields (old + new)
- ✅ **Frontend** can check for null/empty values to determine if multimodal data exists

### Frontend Integration Tips

**Check if multimodal data exists:**

```javascript
// Check if video has visual analysis
if (video.visual_insights && Object.keys(video.visual_insights).length > 0) {
  // Display visual scores
  console.log("Conviction:", video.visual_insights.conviction_score);
}

// Check if analysis has comprehensive scores
if (analysis.congruence_score > 0) {
  // Display multimodal scores
  console.log("Congruence:", analysis.congruence_score);
}

// Check if grades exist
if (analysis.character_grade) {
  // Display grades
  console.log("Character Grade:", analysis.character_grade);
}

// Check if moment-by-moment feedback exists
if (analysis.moment_by_moment && analysis.moment_by_moment.length > 0) {
  // Display timeline visualization
  renderTimeline(analysis.moment_by_moment);
}
```

---

## Testing API Changes

### Test New Fields Exist

```bash
# Upload video
curl -X POST -F "file=@test_promo.mp4" \
  http://localhost:8000/api/v1/videos/upload

# Wait for processing (~2 minutes)

# Get video details
VIDEO_ID="<video_id_from_upload>"
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.visual_insights'

# Should show visual scores
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.vocal_insights'

# Should show vocal scores
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.analyses[0].congruence_score'

# Should show congruence score (0-100)
curl http://localhost:8000/api/v1/videos/$VIDEO_ID | jq '.analyses[0].character_grade'

# Should show grade (A-F) or null
```

---

**Last Updated:** 2025-11-15
**Version:** 1.0 - Multimodal Integration
