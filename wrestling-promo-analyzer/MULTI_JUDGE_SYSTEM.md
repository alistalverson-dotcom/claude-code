# Multi-Judge System

## Overview

The Wrestling Promo Analyzer now supports **multiple AI judge personalities**, each offering a unique perspective on wrestling promos. Users can select which judge analyzes their promo, providing different feedback styles and evaluation criteria.

---

## Available Judges

### 1. **Jake Morrison** - "The Veteran Coach"
**Slug:** `jake-morrison`
**Personality Type:** Veteran Coach
**Experience:** 25 years training world champions

**Evaluation Focus:**
- Psychology (25%) - Mental game and storytelling
- Character Work (20%) - Authenticity and distinctiveness
- Delivery (20%) - Voice control and pacing
- Story Structure (15%) - Beginning, middle, end
- Crowd Connection (15%) - Audience engagement
- Originality (5%) - Fresh ideas and creativity
- Facial Expressions - Emotion conveyance
- Body Language - Physical presence
- Visual Presence - Camera work and charisma

**Style:**
- Direct and honest, never cruel
- Passionate about the craft
- Uses wrestling terminology naturally
- Focuses on practical, actionable advice
- Old-school wisdom meets modern sensibilities

**Best For:**
- Traditional wrestling performance evaluation
- Storytelling and psychology feedback
- Practical coaching-style advice
- Understanding wrestling fundamentals

---

### 2. **Dr. Diana Sterling** - "The Performance Psychologist"
**Slug:** `diana-sterling`
**Personality Type:** Performance Psychologist
**Experience:** PhD in Performance Psychology, 15 years working with performers

**Evaluation Focus:**
- Emotional Authenticity (20%) - Genuine vs. performed emotion
- Psychological Depth (15%) - Real psychology behind character
- Non-Verbal Communication (15%) - Body language and micro-expressions
- Audience Psychology (15%) - Understanding how to influence minds
- Vocal Dynamics (10%) - Psychological effectiveness of voice
- Cognitive Clarity (10%) - Message clarity and memorability
- Character Consistency (5%) - Psychological consistency
- Emotional Intelligence (5%) - Awareness of emotions
- Presence & Charisma (5%) - Psychological attention command

**Style:**
- Analytically empathetic
- Scientifically grounded (references psychological research)
- Emotionally intelligent
- Explains the "why" behind what works
- Focuses on psychological mechanisms

**Best For:**
- Understanding psychological authenticity
- Analyzing emotional impact
- Non-verbal communication feedback
- Audience psychology insights
- Performers interested in the science of performance

---

## Key Differences Between Judges

| Aspect | Jake Morrison | Dr. Diana Sterling |
|--------|---------------|-------------------|
| **Perspective** | Wrestling coach | Performance psychologist |
| **Language** | Wrestling terminology | Psychological terminology |
| **Focus** | Practical performance | Psychological authenticity |
| **Top Priority** | Psychology & storytelling | Emotional authenticity |
| **Feedback Style** | Direct, coaching-oriented | Analytical, explaining "why" |
| **Best Analysis** | Story structure, crowd work | Emotional congruence, body language |

---

## How to Use Multi-Judge System

### **1. During Video Upload**

When uploading a video, select your preferred judge:

```bash
curl -X POST http://localhost:8000/api/v1/videos/upload \
  -F "file=@my_promo.mp4" \
  -F "promo_title=Championship Challenge" \
  -F "character_type=heel" \
  -F "promo_type=challenge" \
  -F "judge_slug=diana-sterling"
```

**Frontend (React):**
```typescript
const formData = new FormData();
formData.append('file', videoFile);
formData.append('promo_title', 'Championship Challenge');
formData.append('character_type', 'heel');
formData.append('judge_slug', 'diana-sterling'); // or 'jake-morrison'

const response = await fetch('/api/v1/videos/upload', {
  method: 'POST',
  body: formData
});
```

**Default:** If no `judge_slug` is specified, Jake Morrison is used by default.

---

### **2. List All Available Judges**

**Endpoint:** `GET /api/v1/judges`

```bash
curl http://localhost:8000/api/v1/judges
```

**Response:**
```json
[
  {
    "id": "...",
    "slug": "jake-morrison",
    "name": "Jake Morrison",
    "personality_type": "Veteran Coach",
    "description": "Jake Morrison is a veteran wrestling coach...",
    "evaluation_focus": "Jake focuses on six core categories...",
    "is_active": true
  },
  {
    "id": "...",
    "slug": "diana-sterling",
    "name": "Dr. Diana Sterling",
    "personality_type": "Performance Psychologist",
    "description": "Dr. Diana Sterling is a performance psychologist...",
    "evaluation_focus": "Dr. Sterling focuses on nine psychological categories...",
    "is_active": true
  }
]
```

---

### **3. Get Specific Judge Details**

**Endpoint:** `GET /api/v1/judges/{slug}`

```bash
curl http://localhost:8000/api/v1/judges/diana-sterling
```

**Response:**
```json
{
  "id": "...",
  "slug": "diana-sterling",
  "name": "Dr. Diana Sterling",
  "personality_type": "Performance Psychologist",
  "description": "Dr. Diana Sterling is a performance psychologist...",
  "evaluation_focus": "Dr. Sterling focuses on nine psychological categories...",
  "scoring_criteria": {
    "emotional_authenticity": {
      "weight": 20,
      "description": "Genuine emotion vs. performed emotion",
      "focus": ["authentic expression", "emotional vulnerability", ...]
    },
    ...
  },
  "is_active": true
}
```

---

## Database Schema

### **Video Model**
```python
class Video(Base):
    # ... other fields
    selected_judge_slug = Column(String(50), default="jake-morrison")
```

### **Judge Model**
```python
class Judge(Base):
    id = Column(UUID, primary_key=True)
    slug = Column(String(50), unique=True)
    name = Column(String(100))
    personality_type = Column(String(100))
    description = Column(Text)
    evaluation_focus = Column(Text)
    scoring_criteria = Column(JSONB)
    system_prompt = Column(Text)
    user_prompt_template = Column(Text)
    is_active = Column(Boolean)
```

---

## Adding New Judges

### **Step 1: Create System Prompt**

Create a new prompt file in `backend/prompts/{judge_slug}_system.md`:

```markdown
# Judge Name - AI Judge System Prompt

You are **Judge Name**, a [description of who they are]...

## Your Personality
...

## Evaluation Framework
...
```

### **Step 2: Update Seed Script**

Add the new judge to `backend/seed_judges.py`:

```python
# Load system prompt
new_judge_prompt_path = Path(__file__).parent / "prompts" / "new_judge_system.md"
with open(new_judge_prompt_path, "r") as f:
    new_judge_prompt = f.read()

# In seed_judges() function:
new_judge = Judge(slug="new-judge-slug")
new_judge.name = "Judge Name"
new_judge.personality_type = "Personality Type"
new_judge.description = """..."""
new_judge.evaluation_focus = """..."""
new_judge.scoring_criteria = {...}
new_judge.system_prompt = new_judge_prompt
new_judge.is_active = True

db.add(new_judge)
db.commit()
```

### **Step 3: Run Seed Script**

```bash
cd backend
python seed_judges.py
```

---

## Example: Analyzing with Different Judges

### **Scenario:** Heel challenge promo

#### **Jake Morrison's Focus:**
- Is the psychology sound? Does the challenge build heat?
- Is the story structure clear (setup → build → climax)?
- Will this get a reaction from the crowd?
- Is the delivery confident and threatening?

#### **Dr. Diana Sterling's Focus:**
- Is the anger authentic or performed?
- Do facial expressions match the aggressive words?
- Are there micro-expressions revealing true emotions?
- Does the body language convey genuine confidence or defensive posturing?
- Is the psychological intimidation effective?

**Result:** Same promo, two different perspectives providing complementary feedback!

---

## System Architecture

```
Video Upload with judge_slug
         ↓
Video saved with selected_judge_slug field
         ↓
process_video_pipeline reads selected_judge_slug
         ↓
analyze_with_jake(judge_slug=selected_judge_slug)
         ↓
Fetches Judge from database by slug
         ↓
Uses Judge's system_prompt for Claude API
         ↓
Analysis saved with judge_id
```

---

## API Integration

### **Claude API Call with Judge**

```python
# Get selected judge
judge = db.query(Judge).filter(Judge.slug == judge_slug).first()

# Use judge's system prompt
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    system=judge.system_prompt,  # Jake's or Diana's personality
    messages=[...],
    ...
)
```

**Each judge provides:**
- Unique `system_prompt` (personality and evaluation framework)
- Custom `scoring_criteria` (different category weights)
- Distinct feedback style and terminology

---

## Future Judge Ideas

### **Marcus "The Provocateur" Dante**
- Harsh, brutally honest critic
- Focuses on originality and breaking clichés
- Emphasizes modern audience expectations
- Low tolerance for generic promos

### **Bobby "The Voice" Valentine**
- Radio/commentary background
- Focuses heavily on vocal delivery and storytelling
- Emphasizes memorability and quotability
- Strong focus on audio quality

### **Coach Tanaka**
- Strong Style wrestling philosophy
- Emphasizes intensity and fighting spirit
- Values authenticity and toughness over polish
- Focus on warrior mentality

---

## Benefits of Multi-Judge System

1. **Multiple Perspectives**: Get coaching and psychological feedback on same promo
2. **Targeted Improvement**: Choose judge that addresses your specific growth areas
3. **Comprehensive Feedback**: Combine multiple judges for well-rounded analysis
4. **Learning Tool**: Understand different evaluation criteria and priorities
5. **Personalization**: Match judge style to your learning preferences

---

## Implementation Status

✅ **Completed:**
- Multi-judge database schema
- Jake Morrison (Veteran Coach)
- Dr. Diana Sterling (Performance Psychologist)
- Judge selection in upload API
- Dynamic judge routing in pipeline
- Judge listing and detail endpoints

🔄 **In Progress:**
- Frontend judge selector UI
- Multi-judge comparison view

📋 **Future:**
- Additional judge personalities
- Judge recommendation based on promo type
- Comparative analysis across multiple judges
- Judge rating/feedback system

---

## Quick Reference

| Task | Endpoint | Method |
|------|----------|--------|
| List all judges | `/api/v1/judges` | GET |
| Get judge details | `/api/v1/judges/{slug}` | GET |
| Upload with judge | `/api/v1/videos/upload` | POST (with `judge_slug` form field) |
| Default judge | - | `jake-morrison` |

---

**Ready to get diverse feedback?** Upload your promo and select a judge! 🎬✨
