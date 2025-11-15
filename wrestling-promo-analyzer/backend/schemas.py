"""
Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional, Dict, Any
from datetime import datetime
from decimal import Decimal


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    """Base user schema"""
    email: EmailStr
    username: str
    full_name: Optional[str] = None
    ring_name: Optional[str] = None
    user_type: str = "wrestler"


class UserCreate(UserBase):
    """Schema for creating a user"""
    password: str


class UserResponse(UserBase):
    """Schema for user response"""
    id: str
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================================
# VIDEO SCHEMAS
# ============================================================================

class VideoUploadResponse(BaseModel):
    """Response after video upload"""
    video_id: str
    filename: str
    original_filename: str
    file_size_bytes: int
    status: str
    message: str
    created_at: datetime

    class Config:
        from_attributes = True


class VideoMetadata(BaseModel):
    """Video metadata"""
    duration_seconds: Optional[Decimal] = None
    width: Optional[int] = None
    height: Optional[int] = None
    codec: Optional[str] = None
    fps: Optional[Decimal] = None
    bitrate: Optional[int] = None


class VideoListItem(BaseModel):
    """Video item in list view"""
    video_id: str
    original_filename: str
    promo_title: Optional[str] = None
    status: str
    duration_seconds: Optional[Decimal] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# TRANSCRIPT SCHEMAS
# ============================================================================

class TranscriptSegment(BaseModel):
    """Single transcript segment with timestamp"""
    start: float
    end: float
    text: str


class TranscriptResponse(BaseModel):
    """Transcript response"""
    id: str
    video_id: str
    full_text: str
    segments: List[Dict[str, Any]]
    language: str
    word_count: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# ANALYSIS SCHEMAS
# ============================================================================

class CategoryScores(BaseModel):
    """Category breakdown scores"""
    psychology: Optional[Decimal] = None
    character_work: Optional[Decimal] = None
    delivery: Optional[Decimal] = None
    story_structure: Optional[Decimal] = None
    crowd_connection: Optional[Decimal] = None
    originality: Optional[Decimal] = None


class TimestampedFeedback(BaseModel):
    """Timestamped feedback item"""
    timestamp: str
    comment: str
    type: str  # positive, negative, neutral


class AnalysisResponse(BaseModel):
    """Analysis response with all scores and feedback"""
    analysis_id: str
    judge_name: str
    overall_score: Decimal
    overall_grade: Optional[str] = None

    # Category scores
    category_scores: Dict[str, float]

    # Feedback
    summary: str
    strengths: List[str]
    weaknesses: List[str]
    timestamped_feedback: List[Dict[str, Any]]
    specific_recommendations: List[str]

    # Metadata
    processing_time_seconds: Optional[Decimal] = None

    # Cost tracking
    input_tokens: Optional[int] = None
    output_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    estimated_cost_usd: Optional[Decimal] = None
    model_version: Optional[str] = None

    created_at: datetime

    class Config:
        from_attributes = True


# ============================================================================
# VIDEO DETAIL SCHEMAS
# ============================================================================

class VideoDetailResponse(BaseModel):
    """Complete video details with transcript and analyses"""
    video_id: str
    filename: str
    original_filename: str
    file_size_bytes: int
    mime_type: str

    # Metadata
    duration_seconds: Optional[Decimal] = None
    width: Optional[int] = None
    height: Optional[int] = None
    codec: Optional[str] = None
    fps: Optional[Decimal] = None

    # Status
    status: str

    # Promo metadata
    promo_title: Optional[str] = None
    promo_type: Optional[str] = None
    character_type: Optional[str] = None
    promo_context: Optional[str] = None

    # Timestamps
    created_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_completed_at: Optional[datetime] = None

    # Related data
    transcript: Optional[TranscriptResponse] = None
    analyses: List[AnalysisResponse] = []

    class Config:
        from_attributes = True


# ============================================================================
# JUDGE SCHEMAS
# ============================================================================

class JudgeResponse(BaseModel):
    """Judge information"""
    id: str
    name: str
    slug: str
    personality_type: str
    description: str
    evaluation_focus: str
    is_active: bool

    class Config:
        from_attributes = True


# ============================================================================
# HEALTH CHECK SCHEMAS
# ============================================================================

class HealthCheckResponse(BaseModel):
    """Health check response"""
    status: str
    timestamp: datetime
    database: str = "unknown"
    redis: str = "unknown"
    celery: str = "unknown"


# ============================================================================
# ERROR SCHEMAS
# ============================================================================

class ErrorResponse(BaseModel):
    """Error response"""
    detail: str
    error_code: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def build_analysis_response(analysis) -> AnalysisResponse:
    """
    Build AnalysisResponse from Analysis model

    Args:
        analysis: Analysis ORM model instance

    Returns:
        AnalysisResponse Pydantic model
    """
    return AnalysisResponse(
        analysis_id=str(analysis.id),
        judge_name=analysis.judge.name,
        overall_score=analysis.overall_score,
        overall_grade=analysis.overall_grade,
        category_scores={
            "psychology": float(analysis.psychology_score) if analysis.psychology_score else 0,
            "character_work": float(analysis.character_score) if analysis.character_score else 0,
            "delivery": float(analysis.delivery_score) if analysis.delivery_score else 0,
            "story_structure": float(analysis.structure_score) if analysis.structure_score else 0,
            "crowd_connection": float(analysis.crowd_connection_score) if analysis.crowd_connection_score else 0,
            "originality": float(analysis.originality_score) if analysis.originality_score else 0,
        },
        summary=analysis.summary,
        strengths=analysis.strengths or [],
        weaknesses=analysis.weaknesses or [],
        timestamped_feedback=analysis.timestamped_feedback or [],
        specific_recommendations=analysis.specific_recommendations or [],
        processing_time_seconds=analysis.processing_time_seconds,
        # Cost tracking
        input_tokens=analysis.input_tokens,
        output_tokens=analysis.output_tokens,
        total_tokens=analysis.total_tokens,
        estimated_cost_usd=analysis.estimated_cost_usd,
        model_version=analysis.model_version,
        created_at=analysis.created_at,
    )


def build_transcript_response(transcript) -> TranscriptResponse:
    """
    Build TranscriptResponse from Transcript model

    Args:
        transcript: Transcript ORM model instance

    Returns:
        TranscriptResponse Pydantic model
    """
    return TranscriptResponse(
        id=str(transcript.id),
        video_id=str(transcript.video_id),
        full_text=transcript.full_text,
        segments=transcript.segments or [],
        language=transcript.language,
        word_count=transcript.word_count,
        created_at=transcript.created_at,
    )


def build_video_detail_response(video) -> VideoDetailResponse:
    """
    Build VideoDetailResponse from Video model with all relationships

    Args:
        video: Video ORM model instance (with loaded relationships)

    Returns:
        VideoDetailResponse Pydantic model
    """
    # Build transcript response if exists
    transcript_response = None
    if video.transcript:
        transcript_response = build_transcript_response(video.transcript)

    # Build analysis responses
    analysis_responses = []
    for analysis in video.analyses:
        analysis_responses.append(build_analysis_response(analysis))

    return VideoDetailResponse(
        video_id=str(video.id),
        filename=video.filename,
        original_filename=video.original_filename,
        file_size_bytes=video.file_size_bytes,
        mime_type=video.mime_type,
        duration_seconds=video.duration_seconds,
        width=video.width,
        height=video.height,
        codec=video.codec,
        fps=video.fps,
        status=video.status,
        promo_title=video.promo_title,
        promo_type=video.promo_type,
        character_type=video.character_type,
        promo_context=video.promo_context,
        created_at=video.created_at,
        processing_started_at=video.processing_started_at,
        processing_completed_at=video.processing_completed_at,
        transcript=transcript_response,
        analyses=analysis_responses,
    )
