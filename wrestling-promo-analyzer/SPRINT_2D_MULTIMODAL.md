# Sprint 2D: Multimodal Integration

**Goal**: Enhance Jake Morrison's analysis with visual intelligence by analyzing facial expressions, body language, and visual storytelling elements alongside the audio transcript.

**Duration**: 3-4 weeks
**Complexity**: High (involves computer vision and multimodal AI)

---

## Overview

Currently, Jake Morrison analyzes only the transcript (what was said). With multimodal integration, he'll also analyze:
- **Facial expressions**: Confidence, emotion, authenticity
- **Body language**: Gestures, posture, movement
- **Visual presence**: Camera work, framing, visual storytelling
- **Crowd reactions**: If visible in frame
- **Visual-audio synchronization**: Does body language match words?

---

## Technical Architecture

### Current Pipeline
```
Video Upload → Metadata → Audio Extraction → Whisper Transcription → Claude Analysis (text only)
```

### Enhanced Pipeline
```
Video Upload → Metadata → Audio Extraction → Whisper Transcription
                      ↓
               Frame Extraction (key frames)
                      ↓
            Visual Feature Detection
                      ↓
         Multimodal Claude Analysis (text + images)
```

---

## Implementation Plan

### **Week 1: Foundation & Frame Extraction**

#### Day 1-2: Frame Extraction Infrastructure
- [ ] Create frame extraction utility using FFmpeg
- [ ] Implement intelligent key frame selection (scene changes, speaker changes)
- [ ] Add frame storage and management
- [ ] Create database schema for frames

**Deliverables:**
- `utils/frame_extraction.py` - Frame extraction utilities
- `models.py` updates - Frame model
- Migration script for frame tables

#### Day 3-4: Visual Feature Detection
- [ ] Implement face detection using OpenCV/MediaPipe
- [ ] Extract facial landmarks and expressions
- [ ] Detect body pose and gestures
- [ ] Store visual features in database

**Deliverables:**
- `utils/visual_analysis.py` - Visual feature extraction
- Face detection and tracking
- Pose estimation integration

#### Day 5: Testing & Optimization
- [ ] Test frame extraction on various video formats
- [ ] Optimize frame selection algorithm
- [ ] Performance testing and memory optimization
- [ ] Error handling for edge cases

**Deliverables:**
- Unit tests for frame extraction
- Performance benchmarks
- Documentation

---

### **Week 2: Multimodal Claude Integration**

#### Day 6-7: Claude Vision API Integration
- [ ] Integrate Claude's vision capabilities
- [ ] Create multimodal prompt templates
- [ ] Implement frame-to-Claude pipeline
- [ ] Handle image encoding and API limits

**Deliverables:**
- `utils/multimodal_claude.py` - Vision API integration
- Multimodal prompt engineering
- Image preprocessing pipeline

#### Day 8-9: Enhanced Analysis Task
- [ ] Update `analyze_with_jake` task for multimodal input
- [ ] Combine transcript + visual features
- [ ] Generate enhanced timestamped feedback
- [ ] Visual-audio correlation analysis

**Deliverables:**
- Updated Celery task with vision support
- Enhanced analysis schema
- Visual feedback generation

#### Day 10: Cost Optimization
- [ ] Optimize number of frames sent to API
- [ ] Implement frame compression
- [ ] Smart frame selection based on importance
- [ ] Update cost tracking for vision API

**Deliverables:**
- Frame selection optimization
- Cost estimation updates
- Budget controls

---

### **Week 3: Enhanced Analysis Features**

#### Day 11-12: Facial Expression Analysis
- [ ] Emotion detection from frames
- [ ] Confidence level analysis
- [ ] Authenticity scoring
- [ ] Eye contact and engagement metrics

**Deliverables:**
- Emotion classification
- Confidence scoring
- Enhanced feedback with visual insights

#### Day 13-14: Body Language Analysis
- [ ] Gesture recognition and classification
- [ ] Posture analysis (open vs. closed)
- [ ] Movement dynamics
- [ ] Power poses and presence detection

**Deliverables:**
- Body language scoring
- Gesture catalog
- Movement analysis

#### Day 15: Visual Storytelling Elements
- [ ] Camera framing analysis
- [ ] Visual composition scoring
- [ ] Lighting and production quality
- [ ] Visual-narrative alignment

**Deliverables:**
- Production quality metrics
- Visual storytelling feedback
- Enhanced recommendations

---

### **Week 4: Frontend Integration & Polish**

#### Day 16-17: Frontend Enhancements
- [ ] Display visual analysis in results
- [ ] Frame gallery with annotations
- [ ] Visual feedback timeline
- [ ] Side-by-side video + visual insights

**Deliverables:**
- Visual analysis display components
- Frame viewer with annotations
- Enhanced video player with visual markers

#### Day 18-19: Enhanced Reporting
- [ ] Visual highlights extraction
- [ ] Screenshot generation for key moments
- [ ] Enhanced PDF reports with images
- [ ] Visual performance charts

**Deliverables:**
- Report generation with visuals
- Highlight reel creation
- Performance dashboards

#### Day 20-21: Testing & Documentation
- [ ] End-to-end multimodal testing
- [ ] Performance optimization
- [ ] Cost analysis and optimization
- [ ] Complete documentation

**Deliverables:**
- Multimodal test suite
- Performance benchmarks
- User documentation
- API documentation updates

---

## Technical Implementation Details

### 1. Frame Extraction Strategy

**Approach**: Extract key frames at strategic intervals
```python
# Extract frames at:
# - Scene changes (visual transitions)
# - Every N seconds (e.g., every 3 seconds)
# - Moments of high motion
# - Speaker changes (if detectable)

# Target: 10-20 frames per minute of video
# For 5-minute promo: 50-100 frames
# Sent to Claude: 5-10 most important frames
```

**Frame Selection Criteria**:
- Scene change detection (histogram difference)
- Motion level (optical flow)
- Face prominence (face detection confidence)
- Even temporal distribution

### 2. Visual Feature Extraction

**Tools**:
- **OpenCV**: Face detection, scene change detection
- **MediaPipe**: Face landmarks, pose estimation, hand tracking
- **scikit-image**: Image quality metrics

**Features to Extract**:
```python
{
    "facial_features": {
        "faces_detected": 1,
        "primary_face_confidence": 0.95,
        "facial_landmarks": [...],
        "emotion_estimates": {"neutral": 0.6, "confident": 0.4},
        "eye_contact_score": 0.8
    },
    "body_language": {
        "pose_detected": true,
        "posture_type": "open",
        "gesture_detected": "pointing",
        "movement_level": "moderate"
    },
    "production": {
        "lighting_quality": 0.85,
        "framing": "medium_shot",
        "background_quality": "clean"
    }
}
```

### 3. Multimodal Prompt Structure

```python
# System prompt for Jake Morrison (enhanced)
system_prompt = """
You are Jake Morrison, veteran wrestling coach and promo analyst.
You analyze both what wrestlers SAY and HOW they present themselves visually.

Analyze:
1. Verbal content (transcript)
2. Facial expressions and emotion
3. Body language and gestures
4. Visual presence and charisma
5. Synchronization between words and actions
"""

# User prompt with frames
user_prompt = """
TRANSCRIPT:
{transcript}

VISUAL ANALYSIS:
I'm providing {num_frames} key frames from this promo at these timestamps:
{frame_timestamps}

[Image 1: 00:05]
[Image 2: 00:15]
...

Analyze:
1. Do facial expressions match the words?
2. Is body language confident and open?
3. Are gestures purposeful and impactful?
4. Does visual presence enhance or detract from message?
5. Specific moments where visual and verbal align or conflict
"""
```

### 4. Enhanced Database Schema

```sql
-- Frames table
CREATE TABLE frames (
    id UUID PRIMARY KEY,
    video_id UUID REFERENCES videos(id) ON DELETE CASCADE,
    frame_number INTEGER NOT NULL,
    timestamp_seconds DECIMAL(10, 2) NOT NULL,
    file_path VARCHAR(500) NOT NULL,

    -- Visual features
    faces_detected INTEGER DEFAULT 0,
    primary_face_confidence DECIMAL(5, 2),
    scene_change_score DECIMAL(5, 2),
    motion_level DECIMAL(5, 2),

    -- Metadata
    width INTEGER,
    height INTEGER,
    file_size_bytes BIGINT,

    created_at TIMESTAMP DEFAULT NOW()
);

-- Visual analysis results
CREATE TABLE visual_analyses (
    id UUID PRIMARY KEY,
    analysis_id UUID REFERENCES analyses(id) ON DELETE CASCADE,

    -- Overall visual scores
    facial_expression_score DECIMAL(5, 2),
    body_language_score DECIMAL(5, 2),
    visual_presence_score DECIMAL(5, 2),
    production_quality_score DECIMAL(5, 2),

    -- Detailed insights
    emotion_breakdown JSONB,  -- {"confident": 0.6, "intense": 0.3, "neutral": 0.1}
    gesture_analysis JSONB,   -- [{"timestamp": "00:15", "gesture": "pointing", "effectiveness": 0.8}]
    visual_feedback JSONB,    -- Enhanced timestamped feedback with visual elements

    created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Cost Management

**Claude Vision Pricing** (as of Jan 2025):
- Input tokens: $3.00 / 1M tokens (same as text)
- Images count as tokens based on size
- Typical image: ~1000-2000 tokens

**Cost Estimation**:
```python
# Per video analysis:
# - Transcript: ~500-2000 tokens (input)
# - 5-10 images: ~5000-20000 tokens (input)
# - Response: ~1500-2000 tokens (output)
#
# Total: ~7000-24000 tokens
# Cost: $0.10 - $0.40 per video
#
# vs. Text-only: $0.05 - $0.15 per video
# Premium for multimodal: +$0.05 - $0.25
```

**Optimization Strategies**:
1. Compress images before sending
2. Send only most important frames
3. Lower resolution for distant shots
4. Cache visual features to avoid reprocessing

---

## API Changes

### New Endpoints

```http
# Get frames for a video
GET /api/v1/videos/{video_id}/frames
Response: [
    {
        "frame_id": "...",
        "timestamp": 5.5,
        "thumbnail_url": "/api/v1/frames/...jpg",
        "visual_features": {...}
    }
]

# Get visual analysis
GET /api/v1/analyses/{analysis_id}/visual
Response: {
    "facial_expression_score": 85,
    "body_language_score": 90,
    "visual_presence_score": 88,
    "emotion_breakdown": {...},
    "visual_feedback": [...]
}

# Get frame image
GET /api/v1/frames/{frame_id}
Response: <JPEG image>
```

### Enhanced Analysis Response

```json
{
    "analysis_id": "...",
    "overall_score": 87,

    "category_scores": {
        "psychology": 88,
        "character_work": 85,
        "delivery": 92,
        "story_structure": 84,
        "crowd_connection": 86,
        "originality": 80,

        // NEW: Visual categories
        "facial_expressions": 88,
        "body_language": 90,
        "visual_presence": 87
    },

    "visual_analysis": {
        "emotion_breakdown": {
            "confident": 0.6,
            "intense": 0.3,
            "focused": 0.1
        },
        "top_gestures": [
            {"gesture": "pointing", "count": 5, "effectiveness": 0.85},
            {"gesture": "open_hands", "count": 3, "effectiveness": 0.90}
        ],
        "production_quality": {
            "lighting": 0.85,
            "framing": 0.90,
            "background": 0.80
        }
    },

    "timestamped_feedback": [
        {
            "timestamp": "00:15",
            "type": "positive",
            "comment": "Great point here with strong eye contact",
            "visual_element": "eye_contact",
            "frame_url": "/api/v1/frames/..."
        }
    ]
}
```

---

## Frontend Components

### 1. Visual Analysis Dashboard
```tsx
<VisualAnalysisDashboard
    emotionBreakdown={emotionData}
    gestureAnalysis={gestureData}
    productionQuality={qualityData}
/>
```

### 2. Frame Timeline
```tsx
<FrameTimeline
    frames={frames}
    currentTime={videoTime}
    onFrameClick={seekToTimestamp}
    annotations={visualFeedback}
/>
```

### 3. Enhanced Video Player
```tsx
<EnhancedVideoPlayer
    videoUrl={videoUrl}
    frames={frames}
    visualMarkers={visualFeedback}
    onTimeUpdate={updateVisualContext}
/>
```

---

## Testing Strategy

### Unit Tests
- Frame extraction accuracy
- Visual feature detection precision
- Multimodal API integration
- Cost calculation for images

### Integration Tests
- End-to-end multimodal pipeline
- Frame storage and retrieval
- Visual analysis generation
- Frontend display of visual data

### Performance Tests
- Frame extraction speed
- Memory usage with images
- API latency with vision
- Database query performance

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| High API costs | High | Frame selection optimization, compression, budget limits |
| Slow processing | Medium | Parallel frame processing, GPU acceleration |
| Storage requirements | Medium | Frame compression, cleanup policies, CDN |
| Complex error handling | Medium | Graceful degradation, fallback to text-only |
| Feature detection accuracy | Low | Multiple detection methods, confidence thresholds |

---

## Success Metrics

- ✅ Multimodal analysis completes in < 3 minutes
- ✅ Cost increase < $0.30 per video
- ✅ Visual scores add meaningful insights
- ✅ Frame extraction < 30 seconds
- ✅ Storage < 50MB per video for frames
- ✅ 95%+ success rate for face detection
- ✅ Visual feedback rated helpful by users

---

## Future Enhancements (Post-Sprint)

1. **Real-time Analysis**: Live promo feedback during recording
2. **Comparison Mode**: Side-by-side visual analysis of multiple promos
3. **Highlight Generation**: Auto-generate highlight clips
4. **Style Transfer**: "Your body language vs. The Rock's"
5. **AR Feedback**: Overlay suggestions on video playback
6. **Crowd Analysis**: Analyze audience reactions when visible
7. **Video Editing Suggestions**: Recommend better cuts/angles

---

## Documentation Deliverables

1. **MULTIMODAL_INTEGRATION.md**: Technical overview
2. **FRAME_EXTRACTION.md**: Frame extraction guide
3. **VISUAL_ANALYSIS.md**: Visual analysis documentation
4. **API_REFERENCE.md** updates: New endpoints
5. **USER_GUIDE.md**: Using visual analysis features

---

## Ready to Start?

**Week 1 Focus**: Frame extraction and visual feature detection foundation

First tasks:
1. Set up frame extraction infrastructure
2. Create Frame model and database migration
3. Implement key frame selection algorithm
4. Test on sample videos

Shall we begin with Week 1?
