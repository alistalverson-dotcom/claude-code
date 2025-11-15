# Multi-Judge System - Setup Instructions

## Overview

This guide walks through setting up the multi-judge system which allows users to select different AI personalities to analyze their wrestling promos.

---

## 🚀 Quick Setup

### 1. Run Database Migration

Add the `selected_judge_slug` column to the `videos` table:

```bash
cd backend
python migrate_add_judge_selection.py
```

**Output:**
```
======================================================================
MIGRATION: Add selected_judge_slug to videos table
======================================================================
Adding 'selected_judge_slug' column to videos table...
✅ Migration successful!
   - Added column: selected_judge_slug VARCHAR(50)
   - Default value: 'jake-morrison'
   - Verified: 0 existing videos now have default judge
======================================================================
```

### 2. Seed Judges into Database

Populate the database with Jake Morrison and Dr. Diana Sterling:

```bash
cd backend
python seed_judges.py
```

**Output:**
```
Checking database...
✅ Database connection successful
============================================================
SEEDING JUDGES TABLE
============================================================
Creating Jake Morrison...
✅ Jake Morrison seeded successfully
   ID: ...
   Name: Jake Morrison
   Slug: jake-morrison
   Personality: Veteran Coach
   Active: True

============================================================
SEEDING DR. DIANA STERLING
============================================================
Creating Dr. Diana Sterling...
✅ Dr. Diana Sterling seeded successfully
   ID: ...
   Name: Dr. Diana Sterling
   Slug: diana-sterling
   Personality: Performance Psychologist
   Active: True

📋 Future judges to implement:
   - Marcus Dante (Harsh Critic)
   - David Chen (Technical Analyst)
============================================================

✅ Database seeding complete!
```

### 3. Rebuild Frontend

Rebuild the frontend to include the new JudgeSelector component:

```bash
cd frontend
npm run build
```

### 4. Restart Services

```bash
# If using Docker
docker-compose restart backend frontend

# If running directly
# Restart your backend and frontend servers
```

---

## ✅ Verification

### Test Judge Selection API

**List all judges:**
```bash
curl http://localhost:8000/api/v1/judges
```

**Expected Response:**
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

### Test Upload with Judge Selection

```bash
curl -X POST http://localhost:8000/api/v1/videos/upload \
  -F "file=@test_promo.mp4" \
  -F "promo_title=Test Promo" \
  -F "character_type=heel" \
  -F "judge_slug=diana-sterling"
```

---

## 📁 Files Changed

### Backend

**New Files:**
- `backend/prompts/diana_sterling_system.md` - Dr. Sterling's evaluation framework (210 lines)
- `backend/migrate_add_judge_selection.py` - Database migration script

**Modified Files:**
- `backend/models.py` - Added `selected_judge_slug` field to Video model
- `backend/main.py` - Added `judge_slug` parameter to upload endpoint
- `backend/tasks.py` - Updated analysis task to use selected judge
- `backend/seed_judges.py` - Added Dr. Diana Sterling seeding

### Frontend

**New Files:**
- `frontend/src/components/JudgeSelector.tsx` - Judge selection UI component

**Modified Files:**
- `frontend/src/pages/UploadPage.tsx` - Integrated JudgeSelector component
- `frontend/src/types.ts` - Added `judge_slug` to VideoUploadForm
- `frontend/src/services/api.ts` - Added judge_slug to upload FormData

### Documentation

**New Files:**
- `MULTI_JUDGE_SYSTEM.md` - Comprehensive multi-judge documentation
- `SETUP_MULTI_JUDGE.md` - This setup guide

---

## 🎭 Using the Multi-Judge System

### Frontend UI

1. Navigate to the Upload page
2. Select your video file
3. Fill in optional metadata (title, character type, etc.)
4. **Select your preferred judge** from the "Select AI Judge" section
5. Click "Upload & Analyze"

### Judge Options

**Jake Morrison** (Default)
- Veteran wrestling coach
- Traditional performance evaluation
- Focuses on psychology, character work, delivery
- Best for: Classic coaching feedback

**Dr. Diana Sterling** (New!)
- Performance psychologist
- Scientific psychological analysis
- Focuses on emotional authenticity, non-verbal communication
- Best for: Understanding psychological impact

### API Usage

When uploading programmatically, include `judge_slug`:

```javascript
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

---

## 🔧 Troubleshooting

### Migration Fails: "Column already exists"

If you see `Column 'selected_judge_slug' already exists`:
- This is normal if you've run the migration before
- The migration script checks for existing columns
- No action needed

### No Judges Returned from API

**Check 1:** Verify judges are seeded
```bash
cd backend
python -c "from database import SessionLocal; from models import Judge; db = SessionLocal(); print(f'Judges: {db.query(Judge).count()}'); db.close()"
```

**Check 2:** Re-run seed script
```bash
python seed_judges.py
```

### Frontend Can't Find JudgeSelector

**Rebuild frontend:**
```bash
cd frontend
npm run build
```

### Videos Still Use Jake Morrison by Default

**This is expected behavior:**
- All new uploads default to Jake Morrison unless a judge is selected
- Existing videos keep their original judge (or default to Jake)
- This ensures backwards compatibility

---

## 🔄 Rollback Instructions

### Remove Judge Selection Column

```bash
cd backend
python migrate_add_judge_selection.py rollback
```

### Remove Judges from Database

```bash
cd backend
python -c "from database import SessionLocal; from models import Judge; db = SessionLocal(); db.query(Judge).delete(); db.commit(); print('Judges removed'); db.close()"
```

---

## 📊 Database Schema

### Videos Table (Updated)

```sql
CREATE TABLE videos (
    ...existing fields...
    selected_judge_slug VARCHAR(50) DEFAULT 'jake-morrison',
    ...
);
```

### Judges Table

```sql
CREATE TABLE judges (
    id UUID PRIMARY KEY,
    slug VARCHAR(50) UNIQUE,
    name VARCHAR(100),
    personality_type VARCHAR(100),
    description TEXT,
    evaluation_focus TEXT,
    scoring_criteria JSONB,
    system_prompt TEXT,
    user_prompt_template TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);
```

### Analyses Table (Existing - No Changes)

```sql
CREATE TABLE analyses (
    ...
    judge_id UUID REFERENCES judges(id),
    ...
);
```

**Relationship:** `Video.selected_judge_slug` → Judge used for analysis → `Analysis.judge_id`

---

## ✨ Next Steps

### Add More Judges

Follow the guide in `MULTI_JUDGE_SYSTEM.md` section "Adding New Judges":

1. Create new system prompt file: `backend/prompts/{slug}_system.md`
2. Update `backend/seed_judges.py`
3. Run seed script
4. Judge will automatically appear in UI

### Future Enhancements

- Multi-judge comparison view (analyze same video with multiple judges)
- Judge recommendation based on promo type
- User ratings of judge feedback quality
- Custom judge creation (advanced feature)

---

## 📖 Reference

- **Full Documentation**: `MULTI_JUDGE_SYSTEM.md`
- **API Integration Guide**: `CLAUDE_API_INTEGRATION.md`
- **Prompt Examples**:
  - `backend/prompts/jake_morrison_system.md`
  - `backend/prompts/diana_sterling_system.md`

---

## ✅ Checklist

- [ ] Run database migration
- [ ] Seed judges into database
- [ ] Verify judges API endpoint
- [ ] Rebuild frontend
- [ ] Restart services
- [ ] Test upload with judge selection
- [ ] Verify different judges provide different analysis styles

**All done? You're ready to use the multi-judge system!** 🎬✨
