"""
SQLAlchemy ORM Models for Wrestling Promo Analyzer
"""

from sqlalchemy import Column, String, Integer, BigInteger, Boolean, Text, DECIMAL, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime
import uuid

from database import Base


# ============================================================================
# USER MODEL
# ============================================================================

class User(Base):
    """User account (wrestler, trainer, fan, admin)"""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)

    # Profile
    full_name = Column(String(100))
    ring_name = Column(String(100))

    # User type
    user_type = Column(String(20), default="wrestler", index=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    last_login = Column(TIMESTAMP(timezone=True))

    # Relationships
    videos = relationship("Video", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User {self.username} ({self.user_type})>"


# ============================================================================
# VIDEO MODEL
# ============================================================================

class Video(Base):
    """Uploaded wrestling promo video"""
    __tablename__ = "videos"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"))

    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger, nullable=False)
    mime_type = Column(String(50), nullable=False)

    # Video metadata (populated by ffprobe)
    duration_seconds = Column(DECIMAL(10, 2))
    width = Column(Integer)
    height = Column(Integer)
    codec = Column(String(50))
    fps = Column(DECIMAL(5, 2))
    bitrate = Column(Integer)

    # Processing status
    status = Column(
        String(20),
        default="uploaded",
        nullable=False,
        index=True
    )

    # Optional promo metadata
    promo_title = Column(String(200))
    promo_type = Column(String(50), index=True)
    character_type = Column(String(50))
    promo_context = Column(Text)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())
    processing_started_at = Column(TIMESTAMP(timezone=True))
    processing_completed_at = Column(TIMESTAMP(timezone=True))

    # Relationships
    user = relationship("User", back_populates="videos")
    transcript = relationship("Transcript", back_populates="video", uselist=False, cascade="all, delete-orphan")
    analyses = relationship("Analysis", back_populates="video", cascade="all, delete-orphan")
    processing_jobs = relationship("ProcessingJob", back_populates="video", cascade="all, delete-orphan")
    frames = relationship("Frame", back_populates="video", cascade="all, delete-orphan")

    # Check constraint
    __table_args__ = (
        CheckConstraint(
            "status IN ('uploaded', 'processing', 'completed', 'failed')",
            name="check_video_status"
        ),
    )

    def __repr__(self):
        return f"<Video {self.original_filename} ({self.status})>"


# ============================================================================
# TRANSCRIPT MODEL
# ============================================================================

class Transcript(Base):
    """Whisper AI transcription of video audio"""
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Transcript content
    full_text = Column(Text, nullable=False)

    # Timestamped segments from Whisper
    # Format: [{"start": 0.0, "end": 2.5, "text": "..."}, ...]
    segments = Column(JSONB, nullable=False)

    # Metadata
    language = Column(String(10), default="en")
    whisper_model = Column(String(50), default="base")
    word_count = Column(Integer)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    video = relationship("Video", back_populates="transcript")
    analyses = relationship("Analysis", back_populates="transcript")

    def __repr__(self):
        return f"<Transcript {self.video_id} ({self.word_count} words)>"


# ============================================================================
# JUDGE MODEL
# ============================================================================

class Judge(Base):
    """AI judge personality (Jake Morrison, Marcus Dante, David Chen)"""
    __tablename__ = "judges"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # Judge information
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(50), unique=True, nullable=False, index=True)

    # Personality
    personality_type = Column(String(50), nullable=False)
    description = Column(Text, nullable=False)
    evaluation_focus = Column(Text, nullable=False)

    # Scoring configuration
    # Format: {"psychology": 25, "character_work": 20, ...}
    scoring_criteria = Column(JSONB, nullable=False)

    # AI prompts
    system_prompt = Column(Text, nullable=False)
    user_prompt_template = Column(Text, nullable=False)

    # Status
    is_active = Column(Boolean, default=True, index=True)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    analyses = relationship("Analysis", back_populates="judge")

    def __repr__(self):
        return f"<Judge {self.name} ({self.personality_type})>"


# ============================================================================
# ANALYSIS MODEL
# ============================================================================

class Analysis(Base):
    """Judge analysis of a promo with scores and feedback"""
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)
    judge_id = Column(UUID(as_uuid=True), ForeignKey("judges.id", ondelete="CASCADE"), nullable=False)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id", ondelete="CASCADE"), nullable=False)

    # Overall scores
    overall_score = Column(DECIMAL(5, 2), nullable=False)
    overall_grade = Column(String(2))

    # Category scores (0-100 scale)
    psychology_score = Column(DECIMAL(5, 2))
    character_score = Column(DECIMAL(5, 2))
    delivery_score = Column(DECIMAL(5, 2))
    structure_score = Column(DECIMAL(5, 2))
    crowd_connection_score = Column(DECIMAL(5, 2))
    originality_score = Column(DECIMAL(5, 2))

    # Feedback
    summary = Column(Text, nullable=False)
    strengths = Column(ARRAY(Text), nullable=False, default=[])
    weaknesses = Column(ARRAY(Text), nullable=False, default=[])

    # Timestamped feedback
    # Format: [{"timestamp": "00:15", "comment": "...", "type": "positive"}, ...]
    timestamped_feedback = Column(JSONB, nullable=False, default=[])

    # Recommendations
    specific_recommendations = Column(ARRAY(Text), default=[])

    # Processing metadata
    processing_time_seconds = Column(DECIMAL(10, 2))

    # Cost tracking
    input_tokens = Column(Integer)  # Tokens sent to API
    output_tokens = Column(Integer)  # Tokens received from API
    total_tokens = Column(Integer)  # Total tokens (input + output)
    estimated_cost_usd = Column(DECIMAL(10, 4))  # Estimated cost in USD
    model_version = Column(String(50))  # Claude model used (e.g., "claude-3-5-sonnet-20241022")

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), index=True)

    # Relationships
    video = relationship("Video", back_populates="analyses")
    judge = relationship("Judge", back_populates="analyses")
    transcript = relationship("Transcript", back_populates="analyses")
    visual_analysis = relationship("VisualAnalysis", back_populates="analysis", uselist=False, cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        # Ensure one analysis per judge per video
        CheckConstraint("overall_score >= 0 AND overall_score <= 100", name="check_overall_score"),
        CheckConstraint("psychology_score >= 0 AND psychology_score <= 100", name="check_psychology_score"),
        CheckConstraint("character_score >= 0 AND character_score <= 100", name="check_character_score"),
        CheckConstraint("delivery_score >= 0 AND delivery_score <= 100", name="check_delivery_score"),
        CheckConstraint("structure_score >= 0 AND structure_score <= 100", name="check_structure_score"),
        CheckConstraint("crowd_connection_score >= 0 AND crowd_connection_score <= 100", name="check_crowd_connection_score"),
        CheckConstraint("originality_score >= 0 AND originality_score <= 100", name="check_originality_score"),
    )

    def __repr__(self):
        return f"<Analysis {self.judge.name if self.judge else 'Unknown'} - Score: {self.overall_score}>"


# ============================================================================
# PROCESSING JOB MODEL
# ============================================================================

class ProcessingJob(Base):
    """Celery background job tracking"""
    __tablename__ = "processing_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)

    # Job information
    job_type = Column(String(50), nullable=False)
    celery_task_id = Column(String(255), unique=True)

    # Status
    status = Column(String(20), default="pending", index=True)
    progress_percentage = Column(Integer, default=0)

    # Error handling
    error_message = Column(Text)

    # Timestamps
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    video = relationship("Video", back_populates="processing_jobs")

    # Constraints
    __table_args__ = (
        CheckConstraint(
            "status IN ('pending', 'running', 'completed', 'failed')",
            name="check_job_status"
        ),
        CheckConstraint(
            "progress_percentage >= 0 AND progress_percentage <= 100",
            name="check_progress_percentage"
        ),
    )

    def __repr__(self):
        return f"<ProcessingJob {self.job_type} ({self.status})>"


# ============================================================================
# FRAME MODEL (Multimodal)
# ============================================================================

class Frame(Base):
    """Extracted video frame for visual analysis"""
    __tablename__ = "frames"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    video_id = Column(UUID(as_uuid=True), ForeignKey("videos.id", ondelete="CASCADE"), nullable=False)

    # Frame identification
    frame_number = Column(Integer, nullable=False)
    timestamp_seconds = Column(DECIMAL(10, 2), nullable=False, index=True)

    # File information
    file_path = Column(String(500), nullable=False)
    file_size_bytes = Column(BigInteger)

    # Frame dimensions
    width = Column(Integer)
    height = Column(Integer)

    # Visual features (populated by analysis)
    faces_detected = Column(Integer, default=0)
    primary_face_confidence = Column(DECIMAL(5, 2))

    # Frame selection scores
    scene_change_score = Column(DECIMAL(5, 2))  # How different from previous frame
    motion_level = Column(DECIMAL(5, 2))  # Amount of motion in frame
    importance_score = Column(DECIMAL(5, 2))  # Overall importance for analysis

    # Flags
    is_key_frame = Column(Boolean, default=False)  # Selected for Claude analysis
    sent_to_api = Column(Boolean, default=False)  # Sent to Claude Vision API

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    video = relationship("Video", back_populates="frames")

    def __repr__(self):
        return f"<Frame {self.video_id} @ {self.timestamp_seconds}s>"


# ============================================================================
# VISUAL ANALYSIS MODEL (Multimodal)
# ============================================================================

class VisualAnalysis(Base):
    """Visual analysis results from multimodal Claude"""
    __tablename__ = "visual_analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), unique=True, nullable=False)

    # Overall visual scores (0-100 scale)
    facial_expression_score = Column(DECIMAL(5, 2))
    body_language_score = Column(DECIMAL(5, 2))
    visual_presence_score = Column(DECIMAL(5, 2))
    production_quality_score = Column(DECIMAL(5, 2))

    # Detailed analysis (JSON)
    # Format: {"confident": 0.6, "intense": 0.3, "neutral": 0.1}
    emotion_breakdown = Column(JSONB)

    # Format: [{"timestamp": "00:15", "gesture": "pointing", "effectiveness": 0.8}, ...]
    gesture_analysis = Column(JSONB)

    # Format: [{"timestamp": "00:15", "comment": "...", "type": "positive", "visual_element": "eye_contact", "frame_id": "..."}, ...]
    visual_feedback = Column(JSONB)

    # Production quality details
    # Format: {"lighting": 0.85, "framing": 0.90, "background": 0.80}
    production_details = Column(JSONB)

    # Visual effects and filters analysis (NEW)
    # Format: {
    #   "color_grading": {"style": "teal_orange", "saturation": 0.75, ...},
    #   "filters": {"film_grain": true, "intensity": 0.35, ...},
    #   "motion_effects": {"camera_shake": 0.2, "handheld_style": true, ...},
    #   "overlays": {"text_detected": true, "graphics_present": false, ...},
    #   "production_technique_score": 78,
    #   "effects_summary": "Cinematic teal/orange grading...",
    #   "effectiveness_feedback": "The color grading creates...",
    #   "recommendations": ["Reduce glitch effects...", ...]
    # }
    effects_analysis = Column(JSONB)

    # Production technique score (0-100)
    production_technique_score = Column(DECIMAL(5, 2))

    # Background music analysis (NEW)
    # Format: {
    #   "music_detected": true,
    #   "music_characteristics": {"tempo_bpm": 125, "intensity": "intense", "key_type": "minor", ...},
    #   "mixing_quality": {"balance_quality": "excellent", "ducking_detected": true, ...},
    #   "music_effectiveness": {"overall_score": 82, "fits_character": true, ...},
    #   "strengths": ["Tempo matches intensity...", ...],
    #   "weaknesses": ["Music too loud at 00:45...", ...],
    #   "recommendations": ["Lower volume by 3dB...", ...]
    # }
    music_analysis = Column(JSONB)

    # Music effectiveness score (0-100)
    music_effectiveness_score = Column(DECIMAL(5, 2))

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    analysis = relationship("Analysis", back_populates="visual_analysis")

    # Constraints
    __table_args__ = (
        CheckConstraint("facial_expression_score >= 0 AND facial_expression_score <= 100", name="check_facial_expression_score"),
        CheckConstraint("body_language_score >= 0 AND body_language_score <= 100", name="check_body_language_score"),
        CheckConstraint("visual_presence_score >= 0 AND visual_presence_score <= 100", name="check_visual_presence_score"),
        CheckConstraint("production_quality_score >= 0 AND production_quality_score <= 100", name="check_production_quality_score"),
        CheckConstraint("production_technique_score >= 0 AND production_technique_score <= 100", name="check_production_technique_score"),
        CheckConstraint("music_effectiveness_score >= 0 AND music_effectiveness_score <= 100", name="check_music_effectiveness_score"),
    )

    def __repr__(self):
        return f"<VisualAnalysis {self.analysis_id}>"
