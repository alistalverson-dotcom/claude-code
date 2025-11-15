# Wrestling Promo Analyzer - Quick Start Guide

## 🚀 Getting the System Running

### **Prerequisites**
- Docker and Docker Compose installed
- Anthropic API key (get from https://console.anthropic.com/)

---

## **Option 1: Automated Startup (Easiest)**

```bash
# Navigate to project directory
cd wrestling-promo-analyzer

# Run the startup script
./start.sh
```

The script will:
1. Create .env file if needed
2. Ask for your Anthropic API key
3. Start all Docker services
4. Show service status

---

## **Option 2: Manual Setup**

### **Step 1: Configure Environment**

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Anthropic API key
nano .env  # or use any editor

# Find this line and replace with your actual key:
ANTHROPIC_API_KEY=your-api-key-here
```

### **Step 2: Start All Services**

```bash
# Start everything with Docker Compose
docker-compose up -d

# This starts:
# - PostgreSQL database (port 5432)
# - Redis (port 6379)
# - FastAPI backend (port 8000)
# - Celery worker (background processing)
# - React frontend (port 3000)
# - Flower monitoring (port 5555)
```

### **Step 3: Verify Services**

```bash
# Check all services are running
docker-compose ps

# You should see all services "Up"
```

### **Step 4: Check Service Health**

```bash
# Test backend API
curl http://localhost:8000/api/v1/health

# Should return: {"status":"healthy"}
```

---

## **Access Points**

Once running, access:

| Service | URL | Description |
|---------|-----|-------------|
| **Frontend** | http://localhost:3000 | Main web interface |
| **Backend API** | http://localhost:8000 | REST API |
| **API Docs** | http://localhost:8000/docs | Interactive API documentation |
| **Flower** | http://localhost:5555 | Celery task monitoring |

---

## **Using the System**

### **1. Upload a Video**

1. Go to http://localhost:3000
2. Click "Upload Video"
3. Drag & drop a wrestling promo video (MP4, MOV, AVI, or MKV)
4. Fill in optional metadata:
   - Promo title
   - Character type (Heel/Face/Tweener)
   - Promo type (Challenge, Revenge, etc.)
   - Context notes
5. Click "Upload & Analyze"

### **2. Watch Processing**

The system will:
1. Extract metadata (5 sec)
2. Extract key frames (15 sec)
3. Extract audio (10 sec)
4. Transcribe with Whisper (30 sec)
5. Analyze with Claude Vision (60 sec)

**Total time: ~2-3 minutes**

### **3. View Results**

Once complete, you'll see:
- Overall score (0-100) and grade
- **Visual Performance Analysis** (NEW!)
  - 4-card metrics grid
  - Emotion breakdown
  - Top gestures
  - Production quality
- 9 category scores (6 verbal + 3 visual)
- Timestamped feedback with visual badges
- Strengths and weaknesses
- Action items

---

## **Monitoring & Logs**

### **View Logs**

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f celery_worker
docker-compose logs -f frontend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### **Monitor Celery Tasks**

Go to http://localhost:5555 (Flower dashboard)

- See active tasks
- Monitor processing queue
- Track task history
- View worker status

---

## **Stopping the System**

```bash
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including database
docker-compose down -v
```

---

## **Troubleshooting**

### **Services won't start**

```bash
# Check Docker is running
docker --version
docker-compose --version

# Check ports aren't already in use
lsof -i :3000  # Frontend
lsof -i :8000  # Backend
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis
```

### **Backend shows "Anthropic API error"**

- Check your API key in `.env` is correct
- Verify you have credits at https://console.anthropic.com/

### **Processing stuck**

```bash
# Restart Celery worker
docker-compose restart celery_worker

# Check Celery logs
docker-compose logs -f celery_worker
```

### **Frontend won't connect to backend**

1. Check backend is running: `curl http://localhost:8000/api/v1/health`
2. Check CORS settings in `.env`:
   ```
   CORS_ORIGINS=http://localhost:3000,http://localhost:8000
   ```
3. Restart frontend: `docker-compose restart frontend`

### **Database connection errors**

```bash
# Check PostgreSQL is running
docker-compose ps postgres

# Check database logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

---

## **Development Mode**

### **Run without Docker (Advanced)**

If you prefer running services individually:

**Terminal 1: Database & Redis**
```bash
docker-compose up postgres redis
```

**Terminal 2: Backend**
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

**Terminal 3: Celery Worker**
```bash
cd backend
celery -A tasks worker --loglevel=info
```

**Terminal 4: Frontend**
```bash
cd frontend
npm install
npm run dev
```

---

## **Database Management**

### **View Database**

```bash
# Connect to PostgreSQL
docker-compose exec postgres psql -U promo_admin -d promo_analyzer

# List tables
\dt

# View videos
SELECT video_id, original_filename, status FROM videos;

# Exit
\q
```

### **Reset Database**

```bash
# Stop services
docker-compose down

# Remove database volume
docker volume rm wrestling-promo-analyzer_postgres_data

# Restart (will recreate database)
docker-compose up -d
```

---

## **Cost Tracking**

Each video analysis costs approximately:

- **Text-only:** $0.01-0.02
- **Multimodal (with visual analysis):** $0.03-0.08

The cost depends on:
- Video length (longer = more transcript)
- Number of frames analyzed (~10 key frames)
- Claude model used

Track usage at: https://console.anthropic.com/

---

## **Next Steps**

1. ✅ Get system running
2. ✅ Upload a test video
3. ✅ View multimodal analysis results
4. 📊 Track performance with Flower
5. 🎨 Customize prompts (see `backend/prompts/`)
6. 🚀 Deploy to production

---

## **System Architecture**

```
┌─────────────┐
│   Browser   │
│ (localhost: │
│    3000)    │
└──────┬──────┘
       │
       ↓
┌─────────────┐      ┌──────────────┐
│   React     │      │   FastAPI    │
│  Frontend   │─────→│   Backend    │
│   (Vite)    │      │ (localhost:  │
└─────────────┘      │    8000)     │
                     └──────┬───────┘
                            │
                ┌───────────┼───────────┐
                ↓           ↓           ↓
         ┌──────────┐ ┌──────────┐ ┌────────┐
         │PostgreSQL│ │  Redis   │ │ Celery │
         │ Database │ │  Queue   │ │ Worker │
         │          │ │          │ │        │
         └──────────┘ └──────────┘ └────────┘
                                        │
                                        ↓
                              ┌──────────────────┐
                              │ Video Processing │
                              ├──────────────────┤
                              │ • FFmpeg         │
                              │ • Whisper        │
                              │ • OpenCV         │
                              │ • MediaPipe      │
                              │ • Claude Vision  │
                              └──────────────────┘
```

---

## **Support**

- **Documentation:** See all `*.md` files in project root
- **API Docs:** http://localhost:8000/docs (when running)
- **Issues:** Check Docker logs first

---

**You're ready to analyze some promos!** 🎬💪
