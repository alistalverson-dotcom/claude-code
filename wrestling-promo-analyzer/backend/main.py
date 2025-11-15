"""
FastAPI Application for Wrestling Promo Analyzer
Main entry point with all API endpoints
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Form, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import Optional, List
import shutil
import uuid
from pathlib import Path
from datetime import datetime
import mimetypes

# Local imports
from database import get_db, engine, Base, check_db_connection, validate_database
from models import Video, Transcript, Analysis, Judge, User
from schemas import (
    VideoUploadResponse,
    VideoDetailResponse,
    VideoListItem,
    JudgeResponse,
    HealthCheckResponse,
    build_video_detail_response,
)
from config import settings, validate_settings, print_settings

# Import tasks (will be implemented next)
# from tasks import process_video_pipeline

# ============================================================================
# APPLICATION SETUP
# ============================================================================

# Validate configuration on startup
try:
    validate_settings()
    print_settings()
except ValueError as e:
    print(f"❌ Configuration Error: {e}")
    print("Please check your .env file and try again.")
    # In production, you might want to exit here
    # import sys; sys.exit(1)

# Create FastAPI application
app = FastAPI(
    title="Wrestling Promo Analyzer API",
    description="AI-powered wrestling promo analysis with Jake Morrison",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ============================================================================
# CORS MIDDLEWARE
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# STARTUP/SHUTDOWN EVENTS
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Run on application startup"""
    print("=" * 60)
    print("🎭 WRESTLING PROMO ANALYZER - STARTING UP")
    print("=" * 60)

    # Validate database connection
    try:
        validate_database()
    except Exception as e:
        print(f"⚠️  Database validation failed: {e}")

    # Create upload directories if they don't exist
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)
    Path(settings.UPLOAD_DIR, "processed").mkdir(parents=True, exist_ok=True)

    print("✅ Application startup complete")
    print("=" * 60)


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown"""
    print("=" * 60)
    print("👋 WRESTLING PROMO ANALYZER - SHUTTING DOWN")
    print("=" * 60)


# ============================================================================
# HEALTH CHECK ENDPOINTS
# ============================================================================

@app.get("/health", response_model=HealthCheckResponse, tags=["Health"])
async def health_check():
    """
    Health check endpoint

    Returns system health status including database and Redis connectivity
    """
    # Check database
    db_status = "connected" if check_db_connection() else "disconnected"

    # Check Redis (simple ping)
    redis_status = "unknown"
    try:
        import redis
        r = redis.from_url(settings.REDIS_URL)
        r.ping()
        redis_status = "connected"
    except:
        redis_status = "disconnected"

    return HealthCheckResponse(
        status="healthy" if db_status == "connected" else "unhealthy",
        timestamp=datetime.utcnow(),
        database=db_status,
        redis=redis_status,
        celery="unknown",  # Can be enhanced with Celery inspect
    )


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "message": "Wrestling Promo Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }


# ============================================================================
# VIDEO UPLOAD ENDPOINT
# ============================================================================

@app.post("/api/v1/videos/upload", response_model=VideoUploadResponse, tags=["Videos"], status_code=201)
async def upload_video(
    file: UploadFile = File(..., description="Video file (MP4, MOV, AVI, MKV)"),
    promo_title: Optional[str] = Form(None, description="Optional title for the promo"),
    promo_type: Optional[str] = Form(None, description="Optional type (heel_promo, face_promo, etc.)"),
    character_type: Optional[str] = Form(None, description="Optional character type (heel, face, tweener)"),
    promo_context: Optional[str] = Form(None, description="Optional context notes"),
    db: Session = Depends(get_db),
):
    """
    Upload a wrestling promo video for analysis

    **Supported formats:** MP4, MOV, AVI, MKV
    **Maximum size:** 500MB
    **Processing time:** ~2 minutes for 5-minute video

    After upload, the video will be automatically processed through:
    1. Metadata extraction (ffprobe)
    2. Audio extraction (FFmpeg)
    3. Transcription (Whisper AI)
    4. Analysis (Jake Morrison AI)

    Returns video_id which can be used to check status and retrieve results.
    """

    # ========================================================================
    # VALIDATE FILE EXTENSION
    # ========================================================================
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in settings.allowed_formats_list:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file type '{file_ext}'. Allowed formats: {', '.join(settings.allowed_formats_list)}",
        )

    # ========================================================================
    # GENERATE UNIQUE FILENAME
    # ========================================================================
    video_id = str(uuid.uuid4())
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{timestamp}_{video_id[:8]}{file_ext}"
    file_path = Path(settings.UPLOAD_DIR) / filename

    # ========================================================================
    # SAVE FILE WITH SIZE VALIDATION
    # ========================================================================
    file_size = 0
    try:
        with open(file_path, "wb") as buffer:
            # Read file in chunks to validate size
            while chunk := await file.read(1024 * 1024):  # 1MB chunks
                file_size += len(chunk)
                if file_size > settings.max_upload_size_bytes:
                    buffer.close()
                    file_path.unlink()  # Delete partial file
                    raise HTTPException(
                        status_code=413,
                        detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE_MB}MB. Got: {file_size // 1024 // 1024}MB",
                    )
                buffer.write(chunk)
    except HTTPException:
        raise
    except Exception as e:
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"File upload failed: {str(e)}",
        )

    # ========================================================================
    # DETECT MIME TYPE
    # ========================================================================
    mime_type, _ = mimetypes.guess_type(str(file_path))
    if not mime_type:
        mime_type = "video/mp4"  # Default fallback

    # ========================================================================
    # CREATE DATABASE RECORD
    # ========================================================================
    try:
        video = Video(
            id=video_id,
            filename=filename,
            original_filename=file.filename,
            file_path=str(file_path),
            file_size_bytes=file_size,
            mime_type=mime_type,
            promo_title=promo_title,
            promo_type=promo_type,
            character_type=character_type,
            promo_context=promo_context,
            status="uploaded",
        )

        db.add(video)
        db.commit()
        db.refresh(video)

        # ====================================================================
        # QUEUE PROCESSING PIPELINE (Celery)
        # ====================================================================
        # Uncomment when tasks.py is ready:
        # from tasks import process_video_pipeline
        # process_video_pipeline.delay(video_id)

        return VideoUploadResponse(
            video_id=str(video.id),
            filename=video.filename,
            original_filename=video.original_filename,
            file_size_bytes=video.file_size_bytes,
            status=video.status,
            message="Video uploaded successfully. Processing will begin shortly.",
            created_at=video.created_at,
        )

    except Exception as e:
        db.rollback()
        # Clean up file if database insert fails
        if file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=500,
            detail=f"Database error: {str(e)}",
        )


# ============================================================================
# VIDEO RETRIEVAL ENDPOINTS
# ============================================================================

@app.get("/api/v1/videos/{video_id}", response_model=VideoDetailResponse, tags=["Videos"])
async def get_video(
    video_id: str,
    db: Session = Depends(get_db),
):
    """
    Get video details, transcript, and analysis results

    Returns complete video information including:
    - Video metadata (duration, resolution, etc.)
    - Processing status
    - Transcript (if completed)
    - Analysis from Jake Morrison (if completed)
    """
    try:
        # Parse UUID
        video_uuid = uuid.UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")

    # Query video with all relationships
    video = db.query(Video).filter(Video.id == video_uuid).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Build complete response
    return build_video_detail_response(video)


@app.get("/api/v1/videos", response_model=List[VideoListItem], tags=["Videos"])
async def list_videos(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of records to return"),
    status: Optional[str] = Query(None, description="Filter by status (uploaded, processing, completed, failed)"),
    db: Session = Depends(get_db),
):
    """
    List all videos with optional filtering and pagination

    **Query parameters:**
    - skip: Offset for pagination (default: 0)
    - limit: Maximum results (default: 20, max: 100)
    - status: Filter by processing status

    Returns list of videos ordered by creation date (newest first).
    """
    query = db.query(Video)

    # Apply status filter if provided
    if status:
        if status not in ["uploaded", "processing", "completed", "failed"]:
            raise HTTPException(
                status_code=400,
                detail="Invalid status. Must be one of: uploaded, processing, completed, failed",
            )
        query = query.filter(Video.status == status)

    # Order by created_at descending (newest first)
    query = query.order_by(Video.created_at.desc())

    # Apply pagination
    videos = query.offset(skip).limit(limit).all()

    # Build response
    return [
        VideoListItem(
            video_id=str(v.id),
            original_filename=v.original_filename,
            promo_title=v.promo_title,
            status=v.status,
            duration_seconds=v.duration_seconds,
            created_at=v.created_at,
        )
        for v in videos
    ]


# ============================================================================
# VIDEO DELETION ENDPOINT
# ============================================================================

@app.delete("/api/v1/videos/{video_id}", tags=["Videos"], status_code=204)
async def delete_video(
    video_id: str,
    db: Session = Depends(get_db),
):
    """
    Delete a video and all associated data

    This will permanently delete:
    - Video file from storage
    - Database record
    - Transcript
    - All analyses
    - All processing jobs

    **Warning:** This action cannot be undone!
    """
    try:
        video_uuid = uuid.UUID(video_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid video ID format")

    video = db.query(Video).filter(Video.id == video_uuid).first()

    if not video:
        raise HTTPException(status_code=404, detail="Video not found")

    # Delete file from storage
    try:
        file_path = Path(video.file_path)
        if file_path.exists():
            file_path.unlink()
    except Exception as e:
        print(f"Warning: Could not delete file {video.file_path}: {e}")

    # Delete database record (cascade will delete related records)
    try:
        db.delete(video)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete video: {str(e)}",
        )

    return None  # 204 No Content


# ============================================================================
# JUDGE ENDPOINTS
# ============================================================================

@app.get("/api/v1/judges", response_model=List[JudgeResponse], tags=["Judges"])
async def list_judges(
    active_only: bool = Query(True, description="Return only active judges"),
    db: Session = Depends(get_db),
):
    """
    List all AI judge personalities

    Returns list of available judges (Jake Morrison, Marcus Dante, David Chen).
    """
    query = db.query(Judge)

    if active_only:
        query = query.filter(Judge.is_active == True)

    judges = query.all()

    return [
        JudgeResponse(
            id=str(j.id),
            name=j.name,
            slug=j.slug,
            personality_type=j.personality_type,
            description=j.description,
            evaluation_focus=j.evaluation_focus,
            is_active=j.is_active,
        )
        for j in judges
    ]


@app.get("/api/v1/judges/{slug}", response_model=JudgeResponse, tags=["Judges"])
async def get_judge(
    slug: str,
    db: Session = Depends(get_db),
):
    """
    Get specific judge by slug

    **Available slugs:**
    - jake-morrison
    - marcus-dante (coming soon)
    - david-chen (coming soon)
    """
    judge = db.query(Judge).filter(Judge.slug == slug).first()

    if not judge:
        raise HTTPException(status_code=404, detail="Judge not found")

    return JudgeResponse(
        id=str(judge.id),
        name=judge.name,
        slug=judge.slug,
        personality_type=judge.personality_type,
        description=judge.description,
        evaluation_focus=judge.evaluation_focus,
        is_active=judge.is_active,
    )


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(404)
async def not_found_handler(request, exc):
    """Custom 404 handler"""
    return JSONResponse(
        status_code=404,
        content={
            "detail": "Not found",
            "path": str(request.url),
        },
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    """Custom 500 handler"""
    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "message": "An unexpected error occurred. Please try again later.",
        },
    )


# ============================================================================
# MAIN (for development)
# ============================================================================

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
    )
