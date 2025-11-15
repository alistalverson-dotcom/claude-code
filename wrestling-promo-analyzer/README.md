# 🎭 Wrestling Promo Analyzer - Sprint 1 MVP

AI-powered wrestling promo analysis with Jake Morrison personality.

## 🚀 Quick Start

### Prerequisites
- Docker Desktop installed
- Anthropic API key ([get one here](https://console.anthropic.com/))
- 2GB+ free disk space

### Setup (5 minutes)

```bash
# 1. Clone/navigate to project
cd wrestling-promo-analyzer

# 2. Create .env file
cp .env.example .env

# 3. Edit .env and add your API key
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# POSTGRES_PASSWORD=your_secure_password

# 4. Start services
docker-compose up -d

# 5. Watch logs
docker-compose logs -f

# 6. Access application
# Frontend: http://localhost:3000
# Backend API: http://localhost:8000
# API Docs: http://localhost:8000/docs
# Celery Monitor: http://localhost:5555
```

### First Time Setup

After starting services, initialize the database:

```bash
# Run database migrations
docker-compose exec backend python -c "from database import init_db; init_db()"
```

## 📊 Architecture

```
User → Frontend (React) → Backend (FastAPI) → Celery Worker
                              ↓                    ↓
                         PostgreSQL            Processing:
                                              1. FFmpeg
                                              2. Whisper
                                              3. Claude API
```

## 🎯 Sprint 1 Features

- ✅ Video upload (MP4, MOV, AVI, MKV up to 500MB)
- ✅ 4-task processing pipeline:
  1. Extract metadata (ffprobe)
  2. Extract audio (FFmpeg → 16kHz WAV)
  3. Transcribe (Whisper → timestamped text)
  4. Analyze (Jake Morrison → scores & feedback)
- ✅ Real-time processing status
- ✅ Results visualization

## 🛠️ Development

### Backend Development

```bash
# Access backend container
docker-compose exec backend bash

# Run tests
pytest

# Format code
black .

# Database migrations
alembic upgrade head
```

### Frontend Development

```bash
# Access frontend container
docker-compose exec frontend sh

# Install new package
npm install <package-name>

# Build for production
npm run build
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart celery_worker

# Rebuild and restart
docker-compose up -d --build backend
```

## 📁 Project Structure

```
wrestling-promo-analyzer/
├── docker-compose.yml          # Service orchestration
├── .env.example                # Environment template
│
├── backend/                    # Python FastAPI Backend
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── main.py                 # FastAPI app
│   ├── models.py               # Database models
│   ├── schemas.py              # Pydantic schemas
│   ├── database.py             # DB connection
│   ├── config.py               # Configuration
│   ├── tasks.py                # Celery tasks
│   ├── schema.sql              # Database schema
│   └── jake_morrison_prompt.md # Judge prompt
│
├── frontend/                   # React TypeScript Frontend
│   ├── Dockerfile.dev
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── src/
│       ├── main.tsx
│       ├── App.tsx
│       ├── api/client.ts
│       ├── pages/
│       └── components/
│
└── uploads/                    # Video storage
    └── processed/              # Audio files
```

## 🔧 Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker ps

# Check ports not in use
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# Remove all containers and volumes
docker-compose down -v
docker-compose up -d
```

### Database connection errors

```bash
# Check PostgreSQL is healthy
docker-compose exec postgres pg_isready -U promo_admin

# Connect to database
docker-compose exec postgres psql -U promo_admin -d promo_analyzer

# View tables
\dt

# View video records
SELECT id, status, created_at FROM videos ORDER BY created_at DESC LIMIT 5;
```

### Celery worker not processing

```bash
# Check worker is running
docker-compose exec celery_worker celery -A tasks inspect active

# Check registered tasks
docker-compose exec celery_worker celery -A tasks inspect registered

# Restart worker
docker-compose restart celery_worker
```

### Frontend can't connect to backend

```bash
# Check backend is responding
curl http://localhost:8000/health

# Check CORS settings in backend .env
# CORS_ORIGINS should include http://localhost:3000

# Check frontend .env
# VITE_API_URL should be http://localhost:8000
```

## 📊 Monitoring

### Celery Flower

Monitor Celery tasks in real-time:
http://localhost:5555

### API Documentation

Interactive API docs:
http://localhost:8000/docs

### Database

```bash
# Connect to database
docker-compose exec postgres psql -U promo_admin -d promo_analyzer

# View recent videos
SELECT id, original_filename, status, created_at
FROM videos
ORDER BY created_at DESC
LIMIT 10;

# View analyses
SELECT v.original_filename, a.overall_score, a.overall_grade
FROM videos v
JOIN analyses a ON v.id = a.video_id
ORDER BY v.created_at DESC
LIMIT 10;
```

## 🎯 Sprint 1 Checklist

- [ ] Docker Compose running all services
- [ ] Can upload video via frontend
- [ ] Video processes through 4 tasks
- [ ] Jake Morrison provides analysis
- [ ] Results display in frontend
- [ ] Processing time < 2 minutes
- [ ] No errors in logs

## 📝 Next Steps

After Sprint 1 completes:
1. Test with 5-10 sample promos
2. Refine Jake Morrison's personality
3. Gather feedback
4. Plan Sprint 2 (user testing)

## 🆘 Getting Help

- Check logs: `docker-compose logs -f`
- Check service status: `docker-compose ps`
- API docs: http://localhost:8000/docs
- Database: `docker-compose exec postgres psql -U promo_admin -d promo_analyzer`

## 📄 License

Private project - All rights reserved

---

**Sprint 1 Goal:** Working video upload → transcription → Jake analysis → results

**Target:** Complete by end of Week 2
