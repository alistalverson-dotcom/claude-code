# Claude API Integration with Feedback System

## 🔄 Overview

The Wrestling Promo Analyzer uses the Claude API in a **multimodal** way, sending both text (transcript) and images (video frames) to get comprehensive performance feedback. Here's how it all connects.

---

## 📊 Integration Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    VIDEO UPLOAD & PROCESSING                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  1. EXTRACT COMPONENTS                                          │
│     • Audio → Whisper AI → Transcript                           │
│     • Video → FFmpeg → Frames (every 2 seconds)                 │
│     • Metadata (duration, resolution, etc.)                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  2. PRE-ANALYSIS (Computer Vision)                              │
│     • Emotion detection (confident, intense, neutral...)        │
│     • Gesture recognition (pointing, open hands, fist...)       │
│     • Eye contact tracking                                      │
│     • Posture analysis (power poses)                            │
│     • Camera framing analysis                                   │
│     • Visual effects detection (color grading, filters)         │
│     • Background music detection (tempo, intensity, key)        │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  3. FRAME SELECTION (Cost Optimization)                         │
│     • Select 10-15 "key frames" (most important moments)        │
│     • Compress images to ~100KB each (JPEG, 85% quality)        │
│     • Encode to base64 for API transmission                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  4. PROMPT CONSTRUCTION                                         │
│                                                                 │
│  System Prompt (Character/Personality)                          │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ "You are Jake Morrison, veteran wrestling coach..."  │     │
│  │ - Direct and honest feedback style                   │     │
│  │ - Wrestling terminology usage                        │     │
│  │ - Scoring framework (0-100 for 9 categories)         │     │
│  └───────────────────────────────────────────────────────┘     │
│                                                                 │
│  User Prompt (Multimodal Content)                              │
│  ┌───────────────────────────────────────────────────────┐     │
│  │ TEXT BLOCK:                                           │     │
│  │ - Promo metadata (title, character type, duration)   │     │
│  │ - Full transcript with timestamps                    │     │
│  │ - Pre-analysis summary (emotions, gestures, etc.)    │     │
│  │ - Frame timestamps (0.5s, 2.3s, 4.7s...)            │     │
│  │ - Task instructions (JSON format required)           │     │
│  │                                                       │     │
│  │ IMAGE BLOCKS (10-15 frames):                         │     │
│  │ - Frame 1: base64 encoded JPEG                       │     │
│  │ - Frame 2: base64 encoded JPEG                       │     │
│  │ - ... (chronological order)                          │     │
│  └───────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  5. CLAUDE API CALL (messages.create)                           │
│                                                                 │
│  client.messages.create(                                        │
│    model="claude-3-5-sonnet-20241022",                         │
│    max_tokens=4096,                                            │
│    system="You are Jake Morrison...",                          │
│    messages=[{                                                 │
│      "role": "user",                                           │
│      "content": [                                              │
│        {"type": "text", "text": "Analyze this promo..."},     │
│        {"type": "image", "source": {...base64...}},           │
│        {"type": "image", "source": {...base64...}},           │
│        ...                                                     │
│      ]                                                         │
│    }]                                                          │
│  )                                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  6. CLAUDE RESPONSE (JSON)                                      │
│                                                                 │
│  {                                                              │
│    "overall_score": 85,                                        │
│    "overall_grade": "A-",                                      │
│    "category_scores": {                                        │
│      "psychology": 88,                                         │
│      "character_work": 82,                                     │
│      "delivery": 90,                                           │
│      "facial_expressions": 87,                                 │
│      "body_language": 90,                                      │
│      "visual_presence": 88,                                    │
│      ...                                                       │
│    },                                                          │
│    "summary": "This is a powerful heel promo...",             │
│    "strengths": [...],                                         │
│    "weaknesses": [...],                                        │
│    "timestamped_feedback": [                                   │
│      {                                                         │
│        "timestamp": "00:15",                                   │
│        "comment": "Excellent eye contact here...",            │
│        "type": "positive",                                    │
│        "visual_element": "eye_contact"                        │
│      }                                                         │
│    ],                                                          │
│    "visual_analysis": {                                        │
│      "emotion_breakdown": {"confident": 0.6, ...},           │
│      "top_gestures": [...],                                   │
│      "production_quality": {...}                              │
│    }                                                           │
│  }                                                             │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  7. PARSE & STORE                                               │
│     • Extract JSON from response                                │
│     • Validate structure                                        │
│     • Store in PostgreSQL database                              │
│     • Track token usage and costs                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  8. DISPLAY TO USER                                             │
│     • React frontend fetches analysis                           │
│     • Renders score cards, category bars, feedback lists       │
│     • Shows timestamped comments with visual badges            │
│     • Displays visual analysis (emotions, gestures, effects)   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔌 API Integration Code

### **1. Client Initialization**

```python
# backend/utils/multimodal_claude.py

from anthropic import Anthropic

class MultimodalClaudeClient:
    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        self.client = Anthropic(api_key=api_key)
        self.model = model
```

### **2. Image Encoding**

```python
def encode_image(self, image_path: str) -> Tuple[str, str, int]:
    """Encode image to base64 for Claude Vision API"""

    # 1. Open and resize image (max 1568x1568px)
    img = Image.open(image_path)
    img.thumbnail((1568, 1568), Image.Resampling.LANCZOS)

    # 2. Convert to JPEG (85% quality for compression)
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=85, optimize=True)

    # 3. Encode to base64
    image_data = base64.standard_b64encode(buffer.getvalue()).decode('utf-8')

    return image_data, "image/jpeg", file_size
```

### **3. Multimodal Content Construction**

```python
def create_multimodal_content(self, text: str, image_paths: List[str]):
    """Create content blocks with text + images"""

    content_blocks = []

    # Add text block first
    content_blocks.append({
        "type": "text",
        "text": text
    })

    # Add image blocks
    for image_path in image_paths:
        image_data, media_type, _ = self.encode_image(image_path)

        content_blocks.append({
            "type": "image",
            "source": {
                "type": "base64",
                "media_type": media_type,
                "data": image_data
            }
        })

    return content_blocks
```

### **4. API Call**

```python
def analyze_with_vision(
    self,
    system_prompt: str,
    user_text: str,
    frame_paths: List[str],
    max_tokens: int = 4096,
    temperature: float = 1.0
) -> Dict:
    """Send multimodal request to Claude"""

    # Create multimodal content
    content = self.create_multimodal_content(user_text, frame_paths)

    # Make API call
    response = self.client.messages.create(
        model=self.model,
        max_tokens=max_tokens,
        temperature=temperature,
        system=system_prompt,  # Character/personality
        messages=[
            {
                "role": "user",
                "content": content  # Text + images
            }
        ]
    )

    # Extract response
    response_text = response.content[0].text

    return {
        "response_text": response_text,
        "usage": {
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        },
        "model": response.model
    }
```

---

## 📝 Prompt Types & Files

### **System Prompts** (Character/Personality)

**File:** `backend/prompts/jake_morrison_system.md`

Defines the AI judge's personality and evaluation framework:

```markdown
You are Jake Morrison, a veteran wrestling coach with 25 years of experience.

Your Personality:
- Direct and honest - you don't sugarcoat
- Passionate about the craft
- Detail-oriented - you notice everything
- Constructive - harsh criticism comes with advice

Evaluation Framework:
Score on 0-100 scale across categories:
1. Psychology - storytelling, emotional connection
2. Character Work - authenticity, uniqueness
3. Delivery - voice control, pacing
4. Story Structure - beginning, middle, end
5. Crowd Connection - relatability, reaction potential
6. Originality - creativity, avoiding clichés
7. Facial Expressions - emotion conveyance
8. Body Language - posture, gestures
9. Visual Presence - camera work, charisma
```

### **User Prompts** (Task Instructions)

**File:** `backend/utils/multimodal_claude.py` → `build_multimodal_prompt()`

Constructs the task-specific prompt with:

```python
prompt = f"""Analyze this wrestling promo using BOTH the transcript AND the {num_frames} video frames.

**PROMO INFORMATION:**
- Title: {promo_title}
- Duration: {duration} seconds
- Character Type: {character_type}
- Promo Type: {promo_type}

**TRANSCRIPT:**
{transcript}

**VISUAL ANALYSIS:**
{num_frames} key frames at timestamps: {timestamp_list}

**PRE-ANALYSIS VISUAL METRICS:**
- Detected Emotions: confident: 60%, intense: 30%, neutral: 10%
- Key Gestures: pointing (5x), open_hands (3x)
- Average Eye Contact Score: 0.75/1.0
- Power Pose Ratio: 50%
- Dominant Shot Type: medium
- Camera Framing Quality: 0.85/1.0

**YOUR TASK:**
Analyze BOTH verbal and visual performance.

Provide:
1. Overall Score (0-100) and Grade (A+ to D)
2. Category Scores for all 9 categories
3. Summary (2-3 paragraphs)
4. Strengths (3-5 bullet points)
5. Weaknesses (3-5 bullet points)
6. Timestamped Feedback with visual elements
7. Specific Recommendations
8. Visual Analysis Summary

Format as JSON: {{...}}
"""
```

### **Enhancement Prompts** (Additional Analysis)

**File:** `backend/prompts/visual_effects_prompt.txt`

For visual effects analysis:

```
VISUAL EFFECTS & PRODUCTION TECHNIQUE ANALYSIS

Analyze the production techniques in this frame:

1. COLOR GRADING & FILTERS:
   - Color palette (teal/orange, warm, cool)?
   - Vignette effect?
   - Saturation and contrast levels?

2. VISUAL EFFECTS:
   - Film grain, glitch effects?
   - Text overlays, graphics?
   - Light leaks, lens flares?

3. EFFECTIVENESS:
   - Do effects ENHANCE or DISTRACT?
   - Appropriate for character type?
   - Professional execution?

Provide JSON response: {{...}}
```

**File:** `backend/prompts/background_music_prompt.txt`

For music analysis:

```
BACKGROUND MUSIC ANALYSIS

Audio features detected:
- Tempo: {bpm} BPM ({tempo_category})
- Intensity: {intensity_level}
- Key: {key_type} (Emotional Tone: {emotional_tone})

Analyze:
1. Music appropriateness for character
2. Mixing quality (volume balance, ducking)
3. Effectiveness (enhance vs distract)

Provide JSON response: {{...}}
```

---

## 💾 Response Structure & Database Storage

### **Claude API Response**

```json
{
  "overall_score": 85,
  "overall_grade": "A-",
  "category_scores": {
    "psychology": 88,
    "character_work": 82,
    "delivery": 90,
    "story_structure": 80,
    "crowd_connection": 85,
    "originality": 75,
    "facial_expressions": 87,
    "body_language": 90,
    "visual_presence": 88
  },
  "summary": "This is a powerful heel promo that demonstrates...",
  "strengths": [
    "Excellent vocal dynamics with strategic volume changes",
    "Strong eye contact during key moments reinforces intimidation",
    "Effective use of pointing gestures to emphasize threats"
  ],
  "weaknesses": [
    "Pacing rushes in the middle section around 01:30",
    "Posture becomes closed at 02:15, undermining confidence",
    "Some clichéd phrases reduce originality score"
  ],
  "timestamped_feedback": [
    {
      "timestamp": "00:15",
      "comment": "Perfect use of silence here - the pause adds weight to the threat",
      "type": "positive",
      "visual_element": "eye_contact"
    },
    {
      "timestamp": "01:23",
      "comment": "Slouched posture contradicts your aggressive words",
      "type": "negative",
      "visual_element": "posture"
    }
  ],
  "specific_recommendations": [
    "Slow down pacing in middle section by 20%",
    "Maintain open, power poses throughout",
    "Replace generic phrases with character-specific language"
  ],
  "visual_analysis": {
    "emotion_breakdown": {
      "confident": 0.6,
      "intense": 0.3,
      "neutral": 0.1
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
  }
}
```

### **Database Storage**

**Table:** `analyses`

```sql
INSERT INTO analyses (
  video_id,
  judge_id,
  transcript_id,
  overall_score,              -- 85
  overall_grade,              -- "A-"
  psychology_score,           -- 88
  character_score,            -- 82
  delivery_score,             -- 90
  structure_score,            -- 80
  crowd_connection_score,     -- 85
  originality_score,          -- 75
  summary,                    -- "This is a powerful..."
  strengths,                  -- ARRAY['...', '...']
  weaknesses,                 -- ARRAY['...', '...']
  timestamped_feedback,       -- JSONB
  specific_recommendations,   -- ARRAY['...', '...']
  input_tokens,               -- 15234
  output_tokens,              -- 2456
  total_tokens,               -- 17690
  estimated_cost_usd,         -- 0.0531
  model_version               -- "claude-3-5-sonnet-20241022"
)
```

**Table:** `visual_analyses`

```sql
INSERT INTO visual_analyses (
  analysis_id,
  facial_expression_score,    -- 87
  body_language_score,        -- 90
  visual_presence_score,      -- 88
  production_quality_score,   -- 85
  emotion_breakdown,          -- JSONB {"confident": 0.6, ...}
  gesture_analysis,           -- JSONB [{"gesture": "pointing", ...}]
  visual_feedback,            -- JSONB (timestamped with visual elements)
  production_details,         -- JSONB {"lighting": 0.85, ...}
  effects_analysis,           -- JSONB (color grading, filters, etc.)
  music_analysis              -- JSONB (tempo, mixing, etc.)
)
```

---

## 💰 Cost Tracking

### **Token Calculation**

```python
# Images are converted to tokens based on size
# Approximation: 1 image ≈ 1000-2000 tokens (100KB JPEG)

image_tokens = num_images * 1500  # Average
text_tokens = 2000  # Prompt + transcript
total_input = image_tokens + text_tokens

# For 10 images:
# Input: (10 * 1500) + 2000 = 17,000 tokens
# Output: ~2000 tokens
# Total: ~19,000 tokens

# Cost (Claude 3.5 Sonnet):
# Input: $3 per 1M tokens
# Output: $15 per 1M tokens
#
# = (17000 * 3 / 1000000) + (2000 * 15 / 1000000)
# = $0.051 + $0.030
# = $0.081 per analysis
```

**Stored in database:**
```python
{
  "input_tokens": 17000,
  "output_tokens": 2000,
  "total_tokens": 19000,
  "estimated_cost_usd": 0.081,
  "model_version": "claude-3-5-sonnet-20241022"
}
```

---

## 🎯 Key Features of Integration

### **1. Multimodal Input**
- ✅ Text (transcript) + Images (frames) in single API call
- ✅ Images encoded as base64 in content blocks
- ✅ Chronological frame ordering for context

### **2. Pre-Analysis Enhancement**
- ✅ Computer vision detects emotions, gestures before Claude
- ✅ Summary included in prompt to guide AI analysis
- ✅ Reduces token usage vs. describing everything in prompt

### **3. Structured Output**
- ✅ JSON format enforced via prompt instructions
- ✅ Consistent schema for database storage
- ✅ Type-safe parsing with validation

### **4. Cost Optimization**
- ✅ Frame selection (10-15 vs. all frames)
- ✅ Image compression (100KB vs. original size)
- ✅ Efficient prompt design (reusable system prompt)

### **5. Character-Based Feedback**
- ✅ System prompt defines personality (Jake Morrison)
- ✅ Scoring framework built into prompt
- ✅ Extensible for multiple "judges" with different styles

---

## 🔄 Full Request/Response Example

### **Request to Claude API**

```python
{
  "model": "claude-3-5-sonnet-20241022",
  "max_tokens": 4096,
  "temperature": 1.0,
  "system": "You are Jake Morrison, veteran wrestling coach...",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "Analyze this wrestling promo...\n\nTRANSCRIPT:\n'Listen up...'..."
        },
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "/9j/4AAQSkZJRgABAQEAYABgAAD..."
          }
        },
        {
          "type": "image",
          "source": {
            "type": "base64",
            "media_type": "image/jpeg",
            "data": "/9j/4AAQSkZJRgABAQEAYABgAAD..."
          }
        }
        // ... 8 more images
      ]
    }
  ]
}
```

### **Response from Claude API**

```python
{
  "id": "msg_01XYZ...",
  "type": "message",
  "role": "assistant",
  "content": [
    {
      "type": "text",
      "text": "{\"overall_score\": 85, \"overall_grade\": \"A-\", ...}"
    }
  ],
  "model": "claude-3-5-sonnet-20241022",
  "stop_reason": "end_turn",
  "usage": {
    "input_tokens": 17234,
    "output_tokens": 2456
  }
}
```

---

## 🚀 Summary

**The Claude API integration is a sophisticated multimodal pipeline that:**

1. **Extracts** transcript and frames from video
2. **Pre-analyzes** frames with computer vision
3. **Selects** 10-15 key frames for cost efficiency
4. **Encodes** images to base64 for API transmission
5. **Constructs** prompts with system (personality) + user (task) components
6. **Sends** multimodal content (text + images) to Claude
7. **Receives** structured JSON feedback
8. **Stores** analysis with token tracking
9. **Displays** results to user in React frontend

**Cost:** ~$0.03-0.08 per video with multimodal analysis
**Processing Time:** ~60-120 seconds for Claude API call
**Quality:** Comprehensive feedback combining verbal + visual analysis

The system uses **three specialized prompts**:
- **System Prompt**: Judge personality (Jake Morrison)
- **User Prompt**: Multimodal task with transcript + frames
- **Enhancement Prompts**: Visual effects, music analysis (optional)

All working together to provide production-quality coaching! 🎬✨
