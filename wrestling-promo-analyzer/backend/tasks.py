"""
Celery Tasks for Wrestling Promo Analyzer
Processing Pipeline: Metadata → Audio → Transcription → Analysis
"""

import os
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from decimal import Decimal

from celery import Celery, chain, group
from celery.utils.log import get_task_logger
import ffmpeg
import whisper
from anthropic import Anthropic

# Local imports
from config import settings
from database import SessionLocal
from models import Video, Transcript, Analysis, ProcessingJob, Judge

# ============================================================================
# CELERY APP CONFIGURATION
# ============================================================================

app = Celery(
    "promo_analyzer",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
)

app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=3600,  # 1 hour hard limit
    task_soft_time_limit=3000,  # 50 minutes soft limit
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    # Error handling defaults
    task_reject_on_worker_lost=True,
    task_acks_on_failure_or_timeout=True,
)

logger = get_task_logger(__name__)


# ============================================================================
# ERROR HANDLING CLASSES
# ============================================================================

class VideoProcessingError(Exception):
    """Base exception for video processing errors"""
    pass


class VideoNotFoundError(VideoProcessingError):
    """Video not found in database or filesystem"""
    pass


class FFmpegError(VideoProcessingError):
    """FFmpeg processing error"""
    pass


class WhisperError(VideoProcessingError):
    """Whisper transcription error"""
    pass


class ClaudeAPIError(VideoProcessingError):
    """Claude API error"""
    pass


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def update_video_status(video_id: str, status: str, error_message: Optional[str] = None):
    """Update video processing status in database"""
    db = SessionLocal()
    try:
        video = db.query(Video).filter(Video.id == video_id).first()
        if video:
            video.status = status
            if status == "processing" and not video.processing_started_at:
                video.processing_started_at = datetime.utcnow()
            elif status == "completed":
                video.processing_completed_at = datetime.utcnow()

            db.commit()
            logger.info(f"Video {video_id} status updated to: {status}")
    except Exception as e:
        logger.error(f"Failed to update video status: {e}")
        db.rollback()
    finally:
        db.close()


def create_processing_job(video_id: str, job_type: str, task_id: str) -> str:
    """Create a processing job record"""
    db = SessionLocal()
    try:
        job = ProcessingJob(
            video_id=video_id,
            job_type=job_type,
            celery_task_id=task_id,
            status="running",
            started_at=datetime.utcnow(),
        )
        db.add(job)
        db.commit()
        db.refresh(job)
        return str(job.id)
    except Exception as e:
        logger.error(f"Failed to create processing job: {e}")
        db.rollback()
        return None
    finally:
        db.close()


def update_processing_job(job_id: str, status: str, error_message: Optional[str] = None):
    """Update processing job status"""
    db = SessionLocal()
    try:
        job = db.query(ProcessingJob).filter(ProcessingJob.id == job_id).first()
        if job:
            job.status = status
            if error_message:
                job.error_message = error_message
            if status in ["completed", "failed"]:
                job.completed_at = datetime.utcnow()
            db.commit()
    except Exception as e:
        logger.error(f"Failed to update processing job: {e}")
        db.rollback()
    finally:
        db.close()


# ============================================================================
# TASK 1: EXTRACT METADATA
# ============================================================================

@app.task(
    bind=True,
    max_retries=3,
    autoretry_for=(FFmpegError,),
    retry_backoff=True,
    retry_backoff_max=600,
    retry_jitter=True,
)
def extract_metadata(self, video_id: str) -> Dict[str, Any]:
    """
    Extract video metadata using ffprobe

    Args:
        video_id: UUID of video to process

    Returns:
        Dict with metadata: duration, width, height, codec, fps, bitrate

    Raises:
        VideoNotFoundError: If video not found
        FFmpegError: If ffprobe fails
    """
    logger.info(f"[TASK 1/4] Starting metadata extraction for video {video_id}")

    db = SessionLocal()
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            error_msg = f"Video {video_id} not found in database"
            logger.error(error_msg)
            raise VideoNotFoundError(error_msg)

        file_path = Path(video.file_path)
        if not file_path.exists():
            error_msg = f"Video file not found: {file_path}"
            logger.error(error_msg)
            raise VideoNotFoundError(error_msg)

        # Run ffprobe to get metadata
        logger.info(f"Running ffprobe on {file_path}")

        try:
            probe = ffmpeg.probe(str(file_path))
        except ffmpeg.Error as e:
            error_msg = f"FFprobe failed: {e.stderr.decode() if e.stderr else str(e)}"
            logger.error(error_msg)
            update_video_status(video_id, "failed", error_msg)
            raise FFmpegError(error_msg)

        # Extract video stream info
        video_stream = next(
            (stream for stream in probe['streams'] if stream['codec_type'] == 'video'),
            None
        )

        if not video_stream:
            error_msg = "No video stream found in file - file may be corrupt or invalid format"
            logger.error(error_msg)
            update_video_status(video_id, "failed", error_msg)
            raise FFmpegError(error_msg)

        # Parse metadata
        metadata = {
            'duration_seconds': float(probe['format'].get('duration', 0)),
            'width': int(video_stream.get('width', 0)),
            'height': int(video_stream.get('height', 0)),
            'codec': video_stream.get('codec_name', 'unknown'),
            'fps': eval(video_stream.get('r_frame_rate', '0/1')),  # e.g., "30/1" -> 30.0
            'bitrate': int(probe['format'].get('bit_rate', 0)),
        }

        # Update database
        video.duration_seconds = Decimal(str(metadata['duration_seconds']))
        video.width = metadata['width']
        video.height = metadata['height']
        video.codec = metadata['codec']
        video.fps = Decimal(str(metadata['fps']))
        video.bitrate = metadata['bitrate']

        db.commit()

        logger.info(f"✅ Metadata extracted: {metadata['duration_seconds']:.2f}s, "
                   f"{metadata['width']}x{metadata['height']}, {metadata['codec']}")

        return metadata

    except Exception as e:
        logger.error(f"❌ Metadata extraction failed: {e}")
        db.rollback()
        update_video_status(video_id, "failed")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()


# ============================================================================
# TASK 2: EXTRACT AUDIO
# ============================================================================

@app.task(bind=True, max_retries=3)
def extract_audio(self, video_id: str, metadata: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract audio from video as 16kHz mono WAV for Whisper

    Args:
        video_id: UUID of video to process
        metadata: Metadata from previous task

    Returns:
        Dict with audio_path and duration
    """
    logger.info(f"[TASK 2/4] Starting audio extraction for video {video_id}")

    db = SessionLocal()
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found in database")

        video_path = Path(video.file_path)

        # Create output path for audio
        audio_filename = f"{video_path.stem}_audio.wav"
        audio_path = Path(settings.UPLOAD_DIR) / "processed" / audio_filename
        audio_path.parent.mkdir(parents=True, exist_ok=True)

        # Extract audio using FFmpeg
        # Convert to 16kHz mono WAV (Whisper's preferred format)
        logger.info(f"Extracting audio to {audio_path}")

        stream = ffmpeg.input(str(video_path))
        stream = ffmpeg.output(
            stream,
            str(audio_path),
            acodec='pcm_s16le',  # 16-bit PCM
            ac=1,  # Mono
            ar='16000',  # 16kHz sample rate
        )

        ffmpeg.run(stream, overwrite_output=True, capture_stdout=True, capture_stderr=True)

        # Verify audio file was created
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio extraction failed: {audio_path} not created")

        audio_size_mb = audio_path.stat().st_size / 1024 / 1024
        logger.info(f"✅ Audio extracted: {audio_size_mb:.2f}MB WAV at 16kHz mono")

        return {
            'audio_path': str(audio_path),
            'duration': metadata['duration_seconds'],
            'audio_size_mb': audio_size_mb,
        }

    except Exception as e:
        logger.error(f"❌ Audio extraction failed: {e}")
        update_video_status(video_id, "failed")
        raise self.retry(exc=e, countdown=60)
    finally:
        db.close()


# ============================================================================
# TASK 3: TRANSCRIBE AUDIO
# ============================================================================

@app.task(bind=True, max_retries=2)
def transcribe_audio(self, video_id: str, audio_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Transcribe audio using OpenAI Whisper

    Args:
        video_id: UUID of video to process
        audio_data: Audio file path and metadata from previous task

    Returns:
        Dict with transcript_id and word_count
    """
    logger.info(f"[TASK 3/4] Starting transcription for video {video_id}")

    db = SessionLocal()
    try:
        # Get video from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found in database")

        audio_path = Path(audio_data['audio_path'])
        if not audio_path.exists():
            raise FileNotFoundError(f"Audio file not found: {audio_path}")

        # Load Whisper model
        logger.info(f"Loading Whisper model: {settings.WHISPER_MODEL}")
        model = whisper.load_model(settings.WHISPER_MODEL, device=settings.WHISPER_DEVICE)

        # Transcribe
        logger.info(f"Transcribing audio ({audio_data['duration']:.2f}s)...")
        start_time = time.time()

        result = model.transcribe(
            str(audio_path),
            language='en',
            task='transcribe',
            verbose=False,
        )

        transcription_time = time.time() - start_time
        logger.info(f"Transcription completed in {transcription_time:.2f}s")

        # Extract segments with timestamps
        segments = []
        for segment in result['segments']:
            segments.append({
                'start': segment['start'],
                'end': segment['end'],
                'text': segment['text'].strip(),
            })

        # Build full text
        full_text = result['text'].strip()
        word_count = len(full_text.split())

        # Save to database
        transcript = Transcript(
            video_id=video.id,
            full_text=full_text,
            segments=segments,
            language=result.get('language', 'en'),
            whisper_model=settings.WHISPER_MODEL,
            word_count=word_count,
        )

        db.add(transcript)
        db.commit()
        db.refresh(transcript)

        # Clean up audio file
        try:
            audio_path.unlink()
            logger.info(f"Cleaned up temporary audio file: {audio_path}")
        except Exception as e:
            logger.warning(f"Could not delete audio file: {e}")

        logger.info(f"✅ Transcription saved: {word_count} words, {len(segments)} segments")

        return {
            'transcript_id': str(transcript.id),
            'word_count': word_count,
            'full_text': full_text,
            'segments': segments,
            'transcription_time': transcription_time,
        }

    except Exception as e:
        logger.error(f"❌ Transcription failed: {e}")
        update_video_status(video_id, "failed")
        raise self.retry(exc=e, countdown=120)
    finally:
        db.close()


# ============================================================================
# TASK 4: ANALYZE WITH JAKE MORRISON
# ============================================================================

@app.task(bind=True, max_retries=3)
def analyze_with_jake(self, video_id: str, transcript_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze promo using Jake Morrison AI judge (Claude API)

    Args:
        video_id: UUID of video to process
        transcript_data: Transcript text and metadata from previous task

    Returns:
        Dict with analysis_id and overall_score
    """
    logger.info(f"[TASK 4/4] Starting Jake Morrison analysis for video {video_id}")

    db = SessionLocal()
    try:
        # Get video and transcript from database
        video = db.query(Video).filter(Video.id == video_id).first()
        if not video:
            raise ValueError(f"Video {video_id} not found in database")

        transcript = db.query(Transcript).filter(Transcript.id == transcript_data['transcript_id']).first()
        if not transcript:
            raise ValueError(f"Transcript {transcript_data['transcript_id']} not found")

        # Get Jake Morrison judge
        jake = db.query(Judge).filter(Judge.slug == "jake-morrison").first()
        if not jake:
            raise ValueError("Jake Morrison judge not found in database")

        # Initialize Claude client
        client = Anthropic(api_key=settings.ANTHROPIC_API_KEY)

        # Build analysis prompt
        user_prompt = f"""Analyze this wrestling promo transcript:

**Promo Title:** {video.promo_title or 'Untitled'}
**Character Type:** {video.character_type or 'Not specified'}
**Promo Type:** {video.promo_type or 'Not specified'}
**Context:** {video.promo_context or 'None provided'}
**Duration:** {float(video.duration_seconds):.1f} seconds
**Word Count:** {transcript.word_count} words

**TRANSCRIPT:**
{transcript.full_text}

---

Provide a detailed analysis with:
1. Overall score (0-100)
2. Category scores for: psychology, character_work, delivery, story_structure, crowd_connection, originality
3. Summary (2-3 paragraphs)
4. Strengths (3-5 bullet points)
5. Weaknesses (3-5 bullet points)
6. Timestamped feedback (reference specific moments)
7. Specific recommendations (3-5 actionable items)

Format your response as JSON with this structure:
{{
  "overall_score": 85,
  "overall_grade": "A-",
  "category_scores": {{
    "psychology": 88,
    "character_work": 82,
    "delivery": 90,
    "story_structure": 80,
    "crowd_connection": 85,
    "originality": 75
  }},
  "summary": "...",
  "strengths": ["...", "...", "..."],
  "weaknesses": ["...", "...", "..."],
  "timestamped_feedback": [
    {{"timestamp": "00:15", "comment": "...", "type": "positive"}},
    {{"timestamp": "01:23", "comment": "...", "type": "negative"}}
  ],
  "specific_recommendations": ["...", "...", "..."]
}}
"""

        # Call Claude API
        logger.info(f"Calling Claude API ({settings.ANTHROPIC_MODEL})...")
        start_time = time.time()

        response = client.messages.create(
            model=settings.ANTHROPIC_MODEL,
            max_tokens=settings.ANTHROPIC_MAX_TOKENS,
            temperature=settings.ANTHROPIC_TEMPERATURE,
            system=jake.system_prompt,
            messages=[
                {"role": "user", "content": user_prompt}
            ]
        )

        analysis_time = time.time() - start_time
        logger.info(f"Claude API call completed in {analysis_time:.2f}s")

        # Parse response
        response_text = response.content[0].text

        # Extract JSON from response (handle potential markdown code blocks)
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            response_text = response_text[json_start:json_end].strip()

        analysis_result = json.loads(response_text)

        # Calculate grade if not provided
        if 'overall_grade' not in analysis_result:
            score = analysis_result['overall_score']
            if score >= 95:
                grade = 'A+'
            elif score >= 90:
                grade = 'A'
            elif score >= 85:
                grade = 'A-'
            elif score >= 80:
                grade = 'B+'
            elif score >= 75:
                grade = 'B'
            elif score >= 70:
                grade = 'B-'
            elif score >= 65:
                grade = 'C+'
            elif score >= 60:
                grade = 'C'
            else:
                grade = 'D'
            analysis_result['overall_grade'] = grade

        # Save analysis to database
        analysis = Analysis(
            video_id=video.id,
            judge_id=jake.id,
            transcript_id=transcript.id,
            overall_score=Decimal(str(analysis_result['overall_score'])),
            overall_grade=analysis_result['overall_grade'],
            psychology_score=Decimal(str(analysis_result['category_scores']['psychology'])),
            character_score=Decimal(str(analysis_result['category_scores']['character_work'])),
            delivery_score=Decimal(str(analysis_result['category_scores']['delivery'])),
            structure_score=Decimal(str(analysis_result['category_scores']['story_structure'])),
            crowd_connection_score=Decimal(str(analysis_result['category_scores']['crowd_connection'])),
            originality_score=Decimal(str(analysis_result['category_scores']['originality'])),
            summary=analysis_result['summary'],
            strengths=analysis_result['strengths'],
            weaknesses=analysis_result['weaknesses'],
            timestamped_feedback=analysis_result.get('timestamped_feedback', []),
            specific_recommendations=analysis_result.get('specific_recommendations', []),
            processing_time_seconds=Decimal(str(analysis_time)),
            token_count=response.usage.input_tokens + response.usage.output_tokens,
            model_version=settings.ANTHROPIC_MODEL,
        )

        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        logger.info(f"✅ Analysis complete: Overall Score = {analysis.overall_score} ({analysis.overall_grade})")
        logger.info(f"   Token usage: {response.usage.input_tokens} in + {response.usage.output_tokens} out = {response.usage.input_tokens + response.usage.output_tokens} total")

        return {
            'analysis_id': str(analysis.id),
            'overall_score': float(analysis.overall_score),
            'overall_grade': analysis.overall_grade,
            'token_count': analysis.token_count,
            'analysis_time': analysis_time,
        }

    except json.JSONDecodeError as e:
        logger.error(f"❌ Failed to parse Claude response as JSON: {e}")
        logger.error(f"Raw response: {response_text[:500]}...")
        update_video_status(video_id, "failed")
        raise
    except Exception as e:
        logger.error(f"❌ Analysis failed: {e}")
        update_video_status(video_id, "failed")
        raise self.retry(exc=e, countdown=120)
    finally:
        db.close()


# ============================================================================
# PIPELINE ORCHESTRATION
# ============================================================================

@app.task(bind=True)
def process_video_pipeline(self, video_id: str):
    """
    Complete video processing pipeline

    Chains all 4 tasks together:
    1. Extract metadata (ffprobe)
    2. Extract audio (FFmpeg)
    3. Transcribe (Whisper)
    4. Analyze (Jake Morrison)

    Args:
        video_id: UUID of video to process
    """
    logger.info(f"=" * 80)
    logger.info(f"🎬 STARTING PIPELINE FOR VIDEO {video_id}")
    logger.info(f"=" * 80)

    # Update video status to processing
    update_video_status(video_id, "processing")

    try:
        # Chain all tasks together
        # Each task receives output from previous task
        pipeline = chain(
            extract_metadata.s(video_id),
            extract_audio.s(video_id),
            transcribe_audio.s(video_id),
            analyze_with_jake.s(video_id),
        )

        # Execute pipeline
        result = pipeline.apply_async()

        # Wait for completion (in production, you'd monitor this differently)
        final_result = result.get()

        # Update video status to completed
        update_video_status(video_id, "completed")

        logger.info(f"=" * 80)
        logger.info(f"✅ PIPELINE COMPLETE FOR VIDEO {video_id}")
        logger.info(f"   Final Score: {final_result['overall_score']} ({final_result['overall_grade']})")
        logger.info(f"=" * 80)

        return final_result

    except Exception as e:
        logger.error(f"=" * 80)
        logger.error(f"❌ PIPELINE FAILED FOR VIDEO {video_id}")
        logger.error(f"   Error: {e}")
        logger.error(f"=" * 80)

        update_video_status(video_id, "failed")
        raise


# ============================================================================
# UTILITY TASKS
# ============================================================================

@app.task
def cleanup_old_files(days: int = 30):
    """
    Clean up old video and audio files

    Args:
        days: Delete files older than this many days
    """
    logger.info(f"Starting cleanup of files older than {days} days")

    upload_dir = Path(settings.UPLOAD_DIR)
    cutoff_time = time.time() - (days * 24 * 60 * 60)

    deleted_count = 0
    freed_bytes = 0

    for file_path in upload_dir.rglob("*"):
        if file_path.is_file():
            if file_path.stat().st_mtime < cutoff_time:
                file_size = file_path.stat().st_size
                try:
                    file_path.unlink()
                    deleted_count += 1
                    freed_bytes += file_size
                    logger.info(f"Deleted: {file_path}")
                except Exception as e:
                    logger.error(f"Failed to delete {file_path}: {e}")

    freed_mb = freed_bytes / 1024 / 1024
    logger.info(f"Cleanup complete: {deleted_count} files deleted, {freed_mb:.2f}MB freed")

    return {
        'deleted_count': deleted_count,
        'freed_mb': freed_mb,
    }


@app.task
def health_check():
    """Simple health check task"""
    return {
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'celery': 'running',
    }
