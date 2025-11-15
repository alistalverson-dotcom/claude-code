# 🎭 Wrestling Promo Analyzer

AI-powered wrestling promo analysis with Jake Morrison - Get professional feedback on your promos in under 2 minutes.

![Sprint 1 MVP](https://img.shields.io/badge/Sprint_1-MVP_Complete-brightgreen)
![Backend](https://img.shields.io/badge/Backend-FastAPI_+_Celery-blue)
![Frontend](https://img.shields.io/badge/Frontend-React_18_+_TypeScript-blue)
![AI](https://img.shields.io/badge/AI-Claude_Sonnet_4_+_Whisper-purple)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Quick Start](#quick-start)
- [Detailed Setup](#detailed-setup)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Development](#development)
- [Troubleshooting](#troubleshooting)

---

## ✨ Features

### Sprint 1 MVP (Complete)

- ✅ **Video Upload** - Drag-and-drop interface supporting MP4, MOV, AVI, MKV (up to 500MB)
- ✅ **Automatic Transcription** - OpenAI Whisper converts speech to text with timestamps
- ✅ **AI Analysis** - Claude Sonnet 4 provides detailed feedback as Jake Morrison
- ✅ **6 Category Scoring**:
  - Psychology (25%) - Mental game and storytelling
  - Character Work (20%) - Authenticity and persona
  - Delivery (20%) - Voice, pacing, emotional range
  - Story Structure (15%) - Beginning, middle, end
  - Crowd Connection (15%) - Audience engagement
  - Originality (5%) - Fresh perspective
- ✅ **Detailed Feedback**:
  - Overall score (0-100) + letter grade
  - Written summary (2-3 paragraphs)
  - Strengths and weaknesses
  - Timestamped comments
  - Actionable recommendations
- ✅ **Real-time Processing** - Auto-polling shows progress, ~2 minutes for 5-min video
- ✅ **Video Library** - View all uploads with status filtering

---

## 🛠️ Tech Stack

### Backend

- **Python 3.11** - Core language
- **FastAPI** - High-performance REST API
- **PostgreSQL** - Primary database
- **SQLAlchemy** - ORM and migrations
- **Celery** - Async task queue
- **Redis** - Message broker + result backend
- **FFmpeg** - Video/audio processing
- **Whisper AI** - Speech-to-text transcription
- **Claude API** - AI analysis (Anthropic)

### Frontend

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite** - Build tool + dev server
- **TailwindCSS** - Utility-first styling
- **React Router** - Client-side routing

### Infrastructure

- **Docker Compose** - Local orchestration
- **PostgreSQL 15** - Database container
- **Redis 7** - Cache container

---

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose installed
- **Anthropic API Key** ([get one here](https://console.anthropic.com/))
- 8GB RAM minimum
- 10GB disk space

### 5-Minute Setup

1. **Clone the repository**

```bash
git clone <your-repo-url>
cd wrestling-promo-analyzer
```

2. **Create environment file**

```bash
cp .env.example .env
```

3. **Add your API key**

Edit `.env` and set:

```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
```

4. **Start all services**

```bash
docker-compose up -d
```

5. **Initialize database**

```bash
# Create tables
docker-compose exec backend python -c "from database import init_db; init_db()"

# Seed Jake Morrison judge
docker-compose exec backend python seed_judges.py
```

6. **Open the app**

- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs
- Celery Monitor: http://localhost:5555

That's it! Upload a video and get analysis.

---

## 📖 Detailed Setup

### Step 1: Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
# ============================================================================
# CRITICAL SETTINGS (Must change)
# ============================================================================
ANTHROPIC_API_KEY=sk-ant-xxx  # Get from https://console.anthropic.com/
POSTGRES_PASSWORD=changeme123  # Change to secure password

# ============================================================================
# APPLICATION SETTINGS
# ============================================================================
APP_ENV=development
DEBUG=True

# ============================================================================
# DATABASE
# ============================================================================
POSTGRES_USER=promo_admin
POSTGRES_DB=promo_analyzer
DATABASE_URL=postgresql://promo_admin:changeme123@postgres:5432/promo_analyzer

# ============================================================================
# REDIS & CELERY
# ============================================================================
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# ============================================================================
# FILE UPLOADS
# ============================================================================
UPLOAD_DIR=/app/uploads
MAX_UPLOAD_SIZE_MB=500
ALLOWED_VIDEO_FORMATS=mp4,mov,avi,mkv

# ============================================================================
# VIDEO PROCESSING
# ============================================================================
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
WHISPER_DEVICE=cpu  # Options: cpu, cuda

# ============================================================================
# AI SETTINGS
# ============================================================================
ANTHROPIC_MODEL=claude-sonnet-4-20250514
ANTHROPIC_MAX_TOKENS=4000
ANTHROPIC_TEMPERATURE=0.7

# ============================================================================
# CORS
# ============================================================================
CORS_ORIGINS=http://localhost:3000,http://localhost:8000
```

### Step 2: Docker Compose Services

The stack includes 6 services:

```yaml
services:
  postgres:       # Database
  redis:          # Message broker
  backend:        # FastAPI server (port 8000)
  celery_worker:  # Background task processor
  flower:         # Celery monitoring UI (port 5555)
  frontend:       # React dev server (port 3000)
```

### Step 3: Database Initialization

```bash
# Start services
docker-compose up -d postgres redis

# Create all tables
docker-compose exec backend python -c "from database import init_db; init_db()"

# Seed Jake Morrison AI judge
docker-compose exec backend python seed_judges.py
```

Expected output:

```
============================================================
SEEDING JUDGES TABLE
============================================================
Creating Jake Morrison...
✅ Jake Morrison seeded successfully
   ID: <uuid>
   Name: Jake Morrison
   Slug: jake-morrison
   Personality: Veteran Coach
   Active: True
============================================================
```

### Step 4: Verify Services

Check all containers are running:

```bash
docker-compose ps
```

Should show:

```
NAME                          STATUS
promo-analyzer-postgres       Up (healthy)
promo-analyzer-redis          Up (healthy)
promo-analyzer-backend        Up
promo-analyzer-celery         Up
promo-analyzer-flower         Up
promo-analyzer-frontend       Up
```

---

## 🎬 Usage

### Upload a Video

1. Navigate to http://localhost:3000
2. Drag and drop a video (or click to browse)
3. Optionally add metadata:
   - Promo title
   - Character type (Heel, Face, Tweener)
   - Promo type (Challenge, Revenge, etc.)
   - Context notes
4. Click "Upload & Analyze"

### View Results

After upload, you'll be redirected to the video detail page where you'll see:

1. **Processing Status** (real-time updates):
   - Video uploaded ✓
   - Extracting audio & transcribing ⏳
   - Jake Morrison analysis...

2. **Analysis Results** (when complete):
   - Overall Score: 85/100 (A-)
   - Category breakdown with visual bars
   - Summary paragraph from Jake
   - Strengths (3-5 items)
   - Weaknesses (3-5 items)
   - Timestamped feedback (e.g., "00:15 - Great opening hook!")
   - Action items (3-5 recommendations)
   - Full transcript (toggle full text or segments)

### Processing Time

- **1-minute video**: ~30 seconds
- **5-minute video**: ~90 seconds
- **10-minute video**: ~3 minutes

Factors:
- Whisper transcription: ~1/10 of video duration
- Claude analysis: 10-20 seconds
- Audio extraction: 5-10 seconds

### Cost per Video

Based on a 5-minute promo:

- Whisper API: Free (running locally)
- Claude API: ~$0.30-0.50 (depends on transcript length)
- **Total: ~$0.40 per video**

---

## 📚 API Documentation

### Interactive Docs

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### Key Endpoints

#### Upload Video

```http
POST /api/v1/videos/upload
Content-Type: multipart/form-data

Parameters:
  file: File (required) - Video file
  promo_title: string (optional)
  promo_type: string (optional)
  character_type: string (optional)
  promo_context: string (optional)

Response: 201 Created
{
  "video_id": "uuid",
  "filename": "video.mp4",
  "status": "uploaded",
  "message": "Video uploaded successfully..."
}
```

#### Get Video Details

```http
GET /api/v1/videos/{video_id}

Response: 200 OK
{
  "video_id": "uuid",
  "status": "completed",
  "transcript": { ... },
  "analyses": [ ... ]
}
```

#### List Videos

```http
GET /api/v1/videos?status=completed&limit=20

Response: 200 OK
[
  {
    "video_id": "uuid",
    "original_filename": "promo.mp4",
    "status": "completed",
    "created_at": "2025-01-15T10:30:00Z"
  }
]
```

#### Health Check

```http
GET /health

Response: 200 OK
{
  "status": "healthy",
  "database": "connected",
  "redis": "connected",
  "celery": "running"
}
```

---

## 📁 Project Structure

```
wrestling-promo-analyzer/
├── backend/
│   ├── main.py              # FastAPI app + endpoints
│   ├── tasks.py             # Celery processing pipeline
│   ├── config.py            # Configuration management
│   ├── database.py          # SQLAlchemy setup
│   ├── models.py            # ORM models (6 tables)
│   ├── schemas.py           # Pydantic schemas
│   ├── seed_judges.py       # Database seeding
│   ├── prompts/
│   │   └── jake_morrison_system.md  # AI judge prompt
│   ├── requirements.txt     # Python dependencies
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── UploadPage.tsx
│   │   │   ├── VideosListPage.tsx
│   │   │   └── VideoDetailPage.tsx
│   │   ├── components/
│   │   │   ├── CategoryScoreBar.tsx
│   │   │   ├── TimestampedFeedbackList.tsx
│   │   │   └── TranscriptView.tsx
│   │   ├── services/
│   │   │   └── api.ts       # API client
│   │   ├── types.ts         # TypeScript interfaces
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── index.html
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── Dockerfile
├── docker-compose.yml       # Service orchestration
├── .env.example             # Environment template
└── README.md
```

---

## 🔧 Development

### Backend Development

```bash
# Enter backend container
docker-compose exec backend bash

# Run migrations (when schema changes)
alembic upgrade head

# Access Python REPL with app context
python
>>> from database import SessionLocal
>>> from models import Video
>>> db = SessionLocal()
>>> videos = db.query(Video).all()

# View logs
docker-compose logs -f backend
docker-compose logs -f celery_worker
```

### Frontend Development

```bash
# Install dependencies locally (for IDE support)
cd frontend
npm install

# The dev server runs in Docker with hot reload
# Edit files in src/ and changes auto-refresh

# View logs
docker-compose logs -f frontend

# Build for production
npm run build
```

### Database Management

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U promo_admin -d promo_analyzer

# Useful queries
SELECT * FROM videos ORDER BY created_at DESC LIMIT 10;
SELECT * FROM analyses WHERE overall_score > 80;
SELECT status, COUNT(*) FROM videos GROUP BY status;

# Reset database (WARNING: deletes all data)
docker-compose exec backend python -c "from database import drop_db, init_db; drop_db(); init_db()"
```

### Celery Monitoring

```bash
# Flower dashboard
http://localhost:5555

# View Celery logs
docker-compose logs -f celery_worker

# Inspect active tasks
docker-compose exec celery_worker celery -A tasks inspect active

# Purge task queue
docker-compose exec celery_worker celery -A tasks purge
```

---

## 🐛 Troubleshooting

### Database Connection Failed

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres

# Verify connection
docker-compose exec backend python -c "from database import check_db_connection; print(check_db_connection())"
```

### Celery Tasks Not Processing

```bash
# Check if worker is running
docker-compose ps celery_worker

# View worker logs
docker-compose logs -f celery_worker

# Check Redis connection
docker-compose exec redis redis-cli ping
# Should return: PONG

# Restart worker
docker-compose restart celery_worker
```

### Upload Fails with 500 Error

Common causes:

1. **Missing API Key**
   ```bash
   # Check if API key is set
   docker-compose exec backend python -c "from config import settings; print(settings.ANTHROPIC_API_KEY[:20])"
   ```

2. **Upload directory permissions**
   ```bash
   # Check uploads folder exists
   docker-compose exec backend ls -la /app/uploads

   # Fix permissions
   docker-compose exec backend chmod -R 777 /app/uploads
   ```

3. **File too large**
   - Check MAX_UPLOAD_SIZE_MB in .env
   - Default is 500MB

### Frontend Shows "API Error"

```bash
# Check backend is running
curl http://localhost:8000/health

# Check CORS configuration
# Make sure CORS_ORIGINS includes http://localhost:3000

# View backend logs
docker-compose logs backend | grep ERROR
```

### FFmpeg Not Found

```bash
# Verify FFmpeg is installed in container
docker-compose exec backend which ffmpeg

# If missing, rebuild container
docker-compose build backend
docker-compose up -d backend
```

### Whisper Model Download Issues

```bash
# Models are downloaded on first use to ~/.cache/whisper

# Check available disk space
docker-compose exec backend df -h

# Manually download model
docker-compose exec backend python -c "import whisper; whisper.load_model('base')"
```

---

## 📊 Performance Optimization

### Use Smaller Whisper Model

For faster processing (lower accuracy):

```bash
# In .env
WHISPER_MODEL=tiny  # Fastest, lowest accuracy
WHISPER_MODEL=base  # Recommended (default)
WHISPER_MODEL=small # Better accuracy, 2x slower
```

### Enable GPU Acceleration

If you have NVIDIA GPU:

```bash
# In .env
WHISPER_DEVICE=cuda

# Update docker-compose.yml celery_worker service:
deploy:
  resources:
    reservations:
      devices:
        - driver: nvidia
          count: 1
          capabilities: [gpu]
```

### Increase Celery Workers

```bash
# In docker-compose.yml
celery_worker:
  command: celery -A tasks worker --loglevel=info --concurrency=4
```

---

## 🚢 Production Deployment

### Key Changes for Production

1. **Environment Variables**
   ```bash
   APP_ENV=production
   DEBUG=False
   SECRET_KEY=<generate-secure-random-key>
   POSTGRES_PASSWORD=<secure-password>
   ```

2. **Use Production Database**
   - Managed PostgreSQL (AWS RDS, Supabase, etc.)
   - Update DATABASE_URL

3. **Use Production Redis**
   - Managed Redis (Redis Cloud, AWS ElastiCache)
   - Update REDIS_URL

4. **Build Frontend**
   ```bash
   cd frontend
   npm run build
   # Serve dist/ folder with nginx
   ```

5. **Add SSL/HTTPS**
   - Use nginx reverse proxy
   - Get SSL cert from Let's Encrypt

6. **Scale Celery Workers**
   - Run multiple worker instances
   - Consider dedicated machines

7. **Monitoring**
   - Add Sentry for error tracking
   - Use Datadog/New Relic for APM
   - Set up log aggregation

---

## 📝 License

MIT License - See LICENSE file

---

## 🙏 Acknowledgments

- **Anthropic** - Claude AI API
- **OpenAI** - Whisper speech recognition
- **FastAPI** - Excellent Python web framework
- **React** - UI library

---

## 📞 Support

For issues or questions:

- Open an issue on GitHub
- Check the [Troubleshooting](#troubleshooting) section
- Review API docs at /docs endpoint

---

**Built with ❤️ for the wrestling community**

Train like a champion. Get feedback from Jake Morrison AI.
