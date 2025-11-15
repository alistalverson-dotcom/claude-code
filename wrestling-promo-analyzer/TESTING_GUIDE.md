# Wrestling Promo Analyzer - Testing Guide

## 🎬 How to Upload and Test Videos

This guide walks you through uploading test videos and viewing the multimodal analysis results.

---

## **Quick Start**

### **1. Access the Application**

**Frontend:** http://localhost:3000/

The development server is running and ready to accept uploads!

---

## **Upload Process**

### **Step 1: Navigate to Upload Page**

Click **"Upload Video"** from the homepage or navigation menu.

You'll see the upload form with these fields:

```
┌─────────────────────────────────────────┐
│ Upload Wrestling Promo Video            │
│                                         │
│ [Choose File] No file chosen            │
│                                         │
│ Video Title (optional)                  │
│ [                                    ]  │
│                                         │
│ Character Type                          │
│ [ Select... ▼ ]                        │
│   - Heel (Bad Guy)                     │
│   - Face (Good Guy)                    │
│   - Tweener (In Between)               │
│                                         │
│ Promo Type                              │
│ [ Select... ▼ ]                        │
│   - Heel Promo                         │
│   - Face Promo                         │
│   - Challenge                          │
│   - Revenge                            │
│   - Celebration                        │
│   - Debut                              │
│   - Retirement                         │
│                                         │
│ Context (optional)                      │
│ [                                    ]  │
│ [                                    ]  │
│                                         │
│ [Upload Video]                         │
└─────────────────────────────────────────┘
```

### **Step 2: Select Your Video File**

**Supported Formats:**
- MP4 (recommended)
- AVI
- MOV
- WebM

**Requirements:**
- Clear audio (for transcription)
- Visible face/body (for visual analysis)
- 10 seconds - 5 minutes length (optimal)

### **Step 3: Fill in Metadata (Optional but Recommended)**

**Promo Title:** Give your video a descriptive name
- Example: "Stone Cold vs The Rock - Raw 1999"

**Character Type:** Select the wrestler's alignment
- **Heel:** Villain/bad guy
- **Face:** Hero/good guy
- **Tweener:** Morally ambiguous

**Promo Type:** What kind of promo is it?
- **Heel Promo:** Antagonistic, cocky
- **Face Promo:** Heroic, motivational
- **Challenge:** Calling someone out
- **Revenge:** Getting even
- **Celebration:** Victory speech
- **Debut:** First appearance
- **Retirement:** Farewell speech

**Context:** Any relevant background
- Example: "Setting up main event at WrestleMania"

### **Step 4: Upload**

Click **"Upload Video"** button.

You'll see:
```
┌─────────────────────────────────────────┐
│ ✓ Upload Successful!                    │
│                                         │
│ Video uploaded and queued for processing│
│                                         │
│ [View Video Details]                   │
└─────────────────────────────────────────┘
```

---

## **Processing Pipeline**

Once uploaded, the video goes through 5 stages:

### **Stage 1: Metadata Extraction** (~5 seconds)
```
⏳ Extracting video metadata...
├─ Duration: 1:23
├─ Resolution: 1920x1080
├─ Codec: h264
└─ FPS: 30
```

### **Stage 2: Frame Extraction** (~15 seconds)
```
🎬 Extracting key frames...
├─ Total frames: ~30
├─ Key frames selected: 10
├─ Scene changes detected
└─ Visual analysis running
```

**Enhanced Visual Analysis:**
- Facial expression detection
- Emotion classification
- Gesture recognition
- Posture analysis
- Eye contact detection
- Camera framing assessment

### **Stage 3: Audio Extraction** (~10 seconds)
```
🔊 Extracting audio...
├─ Format: 16kHz mono WAV
└─ Size: 2.3MB
```

### **Stage 4: Transcription** (~30 seconds)
```
📝 Transcribing with Whisper...
├─ Model: base
├─ Language: English
└─ Word count: 245
```

### **Stage 5: Multimodal Analysis** (~60 seconds)
```
🤖 Jake Morrison analyzing...
├─ Processing transcript
├─ Analyzing 10 key frames
├─ Generating insights
└─ Scoring performance
```

**Total Processing Time:** 2-3 minutes for 1-minute video

---

## **Viewing Results**

### **Processing Status Page**

While processing, you'll see:

```
┌─────────────────────────────────────────┐
│ Video Processing Status                 │
│                                         │
│ ⏳ Processing (Step 3 of 5)            │
│                                         │
│ ████████████░░░░░░░░░░░░  60%         │
│                                         │
│ Current: Transcribing audio...         │
│                                         │
│ [Auto-refresh every 3 seconds]         │
└─────────────────────────────────────────┘
```

The page auto-refreshes and redirects when complete.

### **Analysis Results Page**

Once complete, you'll see the full analysis with:

**1. Overall Score Card**
```
┌─────────────────────────────────────────┐
│ Jake Morrison's Verdict                 │
│                                         │
│ 85/100 - Grade: A-                      │
└─────────────────────────────────────────┘
```

**2. Summary**
2-3 paragraphs of overall analysis

**3. 📹 Visual Performance Analysis** (NEW!)
- 4-card metrics grid
- Emotion breakdown chart
- Top gestures analysis
- Production quality details

**4. Category Breakdown** (9 scores)
- Psychology
- Character Work
- Delivery
- Story Structure
- Crowd Connection
- Originality
- Facial Expressions (NEW)
- Body Language (NEW)
- Visual Presence (NEW)

**5. Timestamped Feedback**
With visual element badges showing specific aspects

**6. Strengths & Weaknesses**
Side-by-side cards

**7. Action Items**
Specific recommendations

**8. Full Transcript**
With timestamps

---

## **Test Video Recommendations**

### **Good Test Videos**

**High Quality:**
- Professional wrestling promos from YouTube
- Clear audio, good lighting
- Wrestler's face clearly visible
- 30 seconds - 2 minutes length

**Examples to Search:**
- "CM Punk pipe bomb promo"
- "The Rock promo"
- "Stone Cold Steve Austin promo"
- "MJF AEW promo"

**Download Method:**
```bash
# Using youtube-dl or yt-dlp
yt-dlp "https://www.youtube.com/watch?v=VIDEO_ID" -f mp4
```

### **Poor Test Videos (Edge Cases)**

Test the system's robustness:
- Low quality webcam recording
- Multiple people in frame
- Background noise
- No face visible (voice-over)
- Very short (<10 seconds)
- Very long (>5 minutes)

---

## **Expected Results by Video Type**

### **Professional Promo (High Quality)**
```
Visual Scores: 80-95
- Facial Expressions: 85-90
- Body Language: 85-95
- Visual Presence: 80-90
- Production Quality: 85-95

Emotions: Confident (60%), Intense (30%)
Gestures: Varied and effective (80%+)
Eye Contact: Strong (0.7-0.9)
Power Poses: 50-70%
```

### **Amateur Promo (Medium Quality)**
```
Visual Scores: 60-75
- Facial Expressions: 65-75
- Body Language: 60-70
- Visual Presence: 60-70
- Production Quality: 50-65

Emotions: Mix of confident/neutral
Gestures: Limited variety (50-70%)
Eye Contact: Moderate (0.4-0.6)
Power Poses: 20-40%
```

### **Webcam Promo (Lower Quality)**
```
Visual Scores: 40-60
- Facial Expressions: 50-60
- Body Language: 45-55
- Visual Presence: 40-50
- Production Quality: 30-50

Emotions: More neutral
Gestures: Minimal (30-50%)
Eye Contact: Varies widely
Production: Poor lighting/framing
```

---

## **Backend Requirements**

Make sure these services are running:

### **1. PostgreSQL Database**
```bash
# Check if running
docker ps | grep postgres

# Start if needed
docker-compose up -d postgres
```

### **2. Redis**
```bash
# Check if running
docker ps | grep redis

# Start if needed
docker-compose up -d redis
```

### **3. Celery Worker**
```bash
# Start Celery worker
cd wrestling-promo-analyzer/backend
celery -A tasks worker --loglevel=info
```

### **4. FastAPI Backend**
```bash
# Start backend API
cd wrestling-promo-analyzer/backend
uvicorn main:app --reload --port 8000
```

### **5. Frontend (Already Running)**
```bash
# Already running at http://localhost:3000
# Port: 3000 (or check terminal output)
```

---

## **Troubleshooting**

### **Upload Fails**

**Problem:** File too large
**Solution:** Videos should be < 100MB. Compress if needed:
```bash
ffmpeg -i input.mp4 -vcodec h264 -acodec aac output.mp4
```

**Problem:** Unsupported format
**Solution:** Convert to MP4:
```bash
ffmpeg -i input.avi -c:v libx264 -c:a aac output.mp4
```

### **Processing Stuck**

**Problem:** Processing never completes
**Check:**
1. Celery worker is running
2. Check worker logs for errors
3. Verify Redis is running
4. Check database connectivity

**Fix:**
```bash
# Restart Celery worker
celery -A tasks worker --loglevel=debug
```

### **No Visual Analysis**

**Problem:** Only 6 category scores (missing visual scores)
**Causes:**
1. Frame extraction failed
2. No face detected in video
3. OpenCV/MediaPipe not installed

**Check Backend Logs:**
```bash
# Look for frame extraction errors
tail -f backend/logs/celery.log
```

### **Poor Quality Results**

**Problem:** Low scores or poor analysis
**Improvements:**
- Better lighting
- Clear audio
- Face clearly visible
- Remove background noise
- Higher resolution video

---

## **Sample Test Plan**

### **Test Case 1: Professional Promo**
```
Video: CM Punk pipe bomb (YouTube)
Expected: High scores (80-90)
Visual Analysis: Should detect emotions, gestures, eye contact
Processing Time: ~2-3 minutes
```

### **Test Case 2: Amateur Webcam**
```
Video: Your own webcam recording
Expected: Medium scores (50-70)
Visual Analysis: May have lower production quality
Processing Time: ~2 minutes
```

### **Test Case 3: No Face Visible**
```
Video: Audio-only or back-turned
Expected: Lower visual scores or graceful fallback
Visual Analysis: Should handle missing face data
```

### **Test Case 4: Multiple People**
```
Video: Tag team promo
Expected: System picks primary face or averages
Visual Analysis: May be less accurate
```

---

## **Monitoring Processing**

### **Check Status via API**
```bash
# Get video status
curl http://localhost:8000/api/v1/videos/{video_id}

# Response:
{
  "status": "processing",
  "processing_started_at": "2025-11-15T18:00:00Z",
  ...
}
```

### **Watch Celery Logs**
```bash
# In backend directory
tail -f celery.log

# You'll see:
[TASK 1/5] Metadata extraction...
[TASK 2/5] Frame extraction...
[TASK 3/5] Audio extraction...
[TASK 4/5] Transcription...
[TASK 5/5] Multimodal analysis...
✅ PIPELINE COMPLETE
```

---

## **API Cost Tracking**

Each video analysis costs approximately:

**Text-Only Analysis:**
- Whisper transcription: Free (self-hosted)
- Claude API: $0.01-0.02 per video

**Multimodal Analysis:**
- Whisper transcription: Free
- Frame extraction: Free
- Visual analysis: Free (local OpenCV/MediaPipe)
- Claude Vision API: $0.03-0.05 per video

**Cost Breakdown:**
- ~2000 text input tokens: $0.006
- ~10 images @ ~1500 tokens each: $0.045
- ~2000 output tokens: $0.030
- **Total: ~$0.08 per video**

---

## **Next Steps After Testing**

Once you've uploaded and analyzed a few videos:

1. **Compare Results** - Try different promo types
2. **Validate Accuracy** - Check if scores match expectations
3. **Test Edge Cases** - Poor quality, no face, etc.
4. **Performance Tuning** - Optimize slow steps
5. **Cost Analysis** - Track actual API costs
6. **User Feedback** - Get wrestlers to test it

---

## **Quick Reference**

```bash
# Start all services
docker-compose up -d                    # Database & Redis
celery -A tasks worker --loglevel=info  # Celery worker
uvicorn main:app --reload               # Backend API
npm run dev                             # Frontend (already running)

# Access URLs
Frontend: http://localhost:3000
Backend:  http://localhost:8000
API Docs: http://localhost:8000/docs

# Upload a video
1. Go to http://localhost:3000
2. Click "Upload Video"
3. Select file and fill metadata
4. Click "Upload"
5. Wait 2-3 minutes
6. View results!
```

---

**Ready to analyze some promos! 🎬** Upload your first video and see the multimodal analysis in action! 💪
