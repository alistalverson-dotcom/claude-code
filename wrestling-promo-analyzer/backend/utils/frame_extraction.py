"""
Frame Extraction Utilities for Multimodal Analysis

Extracts key frames from videos for visual analysis using FFmpeg and OpenCV.
Implements intelligent frame selection based on scene changes, motion, and temporal distribution.
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from decimal import Decimal
import cv2
import numpy as np
from PIL import Image
import logging

logger = logging.getLogger(__name__)


class FrameExtractionError(Exception):
    """Error during frame extraction"""
    pass


class FrameExtractor:
    """
    Extracts and selects key frames from video files

    Strategy:
    1. Extract frames at regular intervals (every N seconds)
    2. Compute scene change scores
    3. Compute motion scores
    4. Select most important frames for analysis
    """

    def __init__(
        self,
        output_dir: str = "uploads/frames",
        interval_seconds: float = 3.0,  # Extract frame every 3 seconds
        max_frames_per_video: int = 100,  # Maximum frames to extract
        target_key_frames: int = 10,  # Target number for Claude API
    ):
        """
        Initialize frame extractor

        Args:
            output_dir: Directory to save extracted frames
            interval_seconds: Seconds between extracted frames
            max_frames_per_video: Maximum total frames to extract
            target_key_frames: Target number of key frames for API
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.interval_seconds = interval_seconds
        self.max_frames_per_video = max_frames_per_video
        self.target_key_frames = target_key_frames

    def extract_frames(
        self,
        video_path: str,
        video_id: str,
    ) -> List[Dict]:
        """
        Extract frames from video at regular intervals

        Args:
            video_path: Path to video file
            video_id: UUID of video for naming frames

        Returns:
            List of frame dictionaries with metadata:
            [
                {
                    "frame_number": 0,
                    "timestamp_seconds": 0.0,
                    "file_path": "...",
                    "width": 1920,
                    "height": 1080,
                    "file_size_bytes": 12345,
                },
                ...
            ]
        """
        logger.info(f"Extracting frames from {video_path}")

        video_path = Path(video_path)
        if not video_path.exists():
            raise FrameExtractionError(f"Video file not found: {video_path}")

        # Get video info
        duration = self._get_video_duration(str(video_path))
        if duration is None:
            raise FrameExtractionError("Could not determine video duration")

        logger.info(f"Video duration: {duration:.2f}s")

        # Calculate number of frames to extract
        num_frames = min(
            int(duration / self.interval_seconds),
            self.max_frames_per_video
        )

        logger.info(f"Will extract {num_frames} frames at {self.interval_seconds}s intervals")

        # Extract frames using FFmpeg
        frames = []
        for i in range(num_frames):
            timestamp = i * self.interval_seconds

            # Don't extract past video duration
            if timestamp >= duration:
                break

            frame_path = self._extract_frame_at_timestamp(
                video_path=str(video_path),
                video_id=video_id,
                timestamp=timestamp,
                frame_number=i
            )

            if frame_path:
                # Get frame metadata
                frame_info = self._get_frame_info(frame_path, i, timestamp)
                frames.append(frame_info)

        logger.info(f"✅ Extracted {len(frames)} frames")
        return frames

    def _extract_frame_at_timestamp(
        self,
        video_path: str,
        video_id: str,
        timestamp: float,
        frame_number: int
    ) -> Optional[str]:
        """
        Extract single frame at specific timestamp using FFmpeg

        Args:
            video_path: Path to video file
            video_id: Video UUID
            timestamp: Time in seconds
            frame_number: Frame sequence number

        Returns:
            Path to extracted frame or None if failed
        """
        # Output filename
        output_filename = f"{video_id}_frame_{frame_number:04d}.jpg"
        output_path = self.output_dir / output_filename

        # FFmpeg command to extract frame
        cmd = [
            "ffmpeg",
            "-ss", str(timestamp),  # Seek to timestamp
            "-i", video_path,  # Input video
            "-vframes", "1",  # Extract 1 frame
            "-q:v", "2",  # High quality (1-31, lower is better)
            "-y",  # Overwrite output
            str(output_path)
        ]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30
            )

            if result.returncode == 0 and output_path.exists():
                return str(output_path)
            else:
                logger.error(f"FFmpeg failed for frame {frame_number}: {result.stderr.decode()[:200]}")
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"FFmpeg timeout for frame {frame_number}")
            return None
        except Exception as e:
            logger.error(f"Error extracting frame {frame_number}: {e}")
            return None

    def _get_frame_info(
        self,
        frame_path: str,
        frame_number: int,
        timestamp: float
    ) -> Dict:
        """
        Get metadata for extracted frame

        Args:
            frame_path: Path to frame image
            frame_number: Frame sequence number
            timestamp: Timestamp in seconds

        Returns:
            Dictionary with frame metadata
        """
        frame_path_obj = Path(frame_path)

        # Get image dimensions using PIL (faster than OpenCV)
        try:
            with Image.open(frame_path) as img:
                width, height = img.size
        except Exception as e:
            logger.warning(f"Could not read frame dimensions: {e}")
            width, height = None, None

        # Get file size
        file_size = frame_path_obj.stat().st_size if frame_path_obj.exists() else 0

        return {
            "frame_number": frame_number,
            "timestamp_seconds": Decimal(str(round(timestamp, 2))),
            "file_path": str(frame_path),
            "width": width,
            "height": height,
            "file_size_bytes": file_size,
        }

    def _get_video_duration(self, video_path: str) -> Optional[float]:
        """
        Get video duration using ffprobe

        Args:
            video_path: Path to video file

        Returns:
            Duration in seconds or None if failed
        """
        cmd = [
            "ffprobe",
            "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=noprint_wrappers=1:nokey=1",
            video_path
        ]

        try:
            result = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=10
            )

            if result.returncode == 0:
                duration_str = result.stdout.decode().strip()
                return float(duration_str)
            else:
                logger.error(f"ffprobe failed: {result.stderr.decode()}")
                return None

        except Exception as e:
            logger.error(f"Error getting video duration: {e}")
            return None

    def compute_scene_change_scores(self, frames: List[Dict]) -> List[Dict]:
        """
        Compute scene change scores by comparing consecutive frames

        Uses histogram comparison to detect significant visual changes.

        Args:
            frames: List of frame dictionaries

        Returns:
            Updated frames with scene_change_score added
        """
        logger.info("Computing scene change scores...")

        prev_hist = None

        for frame in frames:
            frame_path = frame["file_path"]

            # Read frame
            img = cv2.imread(frame_path)
            if img is None:
                frame["scene_change_score"] = Decimal("0.0")
                continue

            # Compute histogram
            hist = cv2.calcHist([img], [0, 1, 2], None, [8, 8, 8], [0, 256, 0, 256, 0, 256])
            hist = cv2.normalize(hist, hist).flatten()

            # Compare with previous frame
            if prev_hist is not None:
                # Use correlation for comparison
                correlation = cv2.compareHist(prev_hist, hist, cv2.HISTCMP_CORREL)
                # Convert to difference score (0 = same, 1 = completely different)
                difference = 1.0 - correlation
                frame["scene_change_score"] = Decimal(str(round(max(0.0, difference), 3)))
            else:
                # First frame has no previous frame to compare
                frame["scene_change_score"] = Decimal("0.0")

            prev_hist = hist

        logger.info("✅ Scene change scores computed")
        return frames

    def compute_motion_scores(self, frames: List[Dict]) -> List[Dict]:
        """
        Compute motion scores for each frame

        Analyzes amount of visual activity/motion in each frame.

        Args:
            frames: List of frame dictionaries

        Returns:
            Updated frames with motion_level added
        """
        logger.info("Computing motion scores...")

        for frame in frames:
            frame_path = frame["file_path"]

            # Read frame
            img = cv2.imread(frame_path)
            if img is None:
                frame["motion_level"] = Decimal("0.0")
                continue

            # Convert to grayscale
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Compute Laplacian variance (measure of sharpness/motion)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

            # Normalize to 0-1 scale (typical range: 0-1000)
            motion_score = min(1.0, laplacian_var / 500.0)

            frame["motion_level"] = Decimal(str(round(motion_score, 3)))

        logger.info("✅ Motion scores computed")
        return frames

    def select_key_frames(self, frames: List[Dict]) -> List[Dict]:
        """
        Select key frames for Claude Vision API analysis

        Strategy:
        1. Combine scene_change_score and motion_level into importance_score
        2. Ensure temporal distribution (don't cluster all frames at start/end)
        3. Select top N frames based on importance

        Args:
            frames: List of frame dictionaries with scores

        Returns:
            Frames with is_key_frame and importance_score set
        """
        logger.info(f"Selecting {self.target_key_frames} key frames from {len(frames)} total...")

        if not frames:
            return frames

        # Compute importance scores
        for frame in frames:
            scene_score = float(frame.get("scene_change_score", 0))
            motion_score = float(frame.get("motion_level", 0))

            # Weighted combination (scene changes are more important)
            importance = (scene_score * 0.7) + (motion_score * 0.3)

            frame["importance_score"] = Decimal(str(round(importance, 3)))
            frame["is_key_frame"] = False

        # Sort by importance
        sorted_frames = sorted(frames, key=lambda f: float(f["importance_score"]), reverse=True)

        # Select top N frames
        num_to_select = min(self.target_key_frames, len(sorted_frames))

        # Mark as key frames
        selected_frames = sorted_frames[:num_to_select]
        for frame in selected_frames:
            frame["is_key_frame"] = True

        # Ensure temporal distribution - if all selected frames are clustered,
        # add some evenly distributed frames
        selected_timestamps = sorted([float(f["timestamp_seconds"]) for f in selected_frames])
        if len(selected_timestamps) > 1:
            gaps = [selected_timestamps[i+1] - selected_timestamps[i]
                    for i in range(len(selected_timestamps)-1)]
            max_gap = max(gaps) if gaps else 0

            # If there's a large gap (> 60s), add a frame from that region
            if max_gap > 60 and num_to_select < len(frames):
                gap_index = gaps.index(max_gap)
                gap_start = selected_timestamps[gap_index]
                gap_end = selected_timestamps[gap_index + 1]
                gap_middle = (gap_start + gap_end) / 2

                # Find frame closest to gap middle
                for frame in frames:
                    if not frame["is_key_frame"]:
                        timestamp = float(frame["timestamp_seconds"])
                        if gap_start < timestamp < gap_end:
                            # Add this frame
                            frame["is_key_frame"] = True
                            logger.info(f"Added frame at {timestamp:.1f}s to fill temporal gap")
                            break

        key_frame_count = sum(1 for f in frames if f["is_key_frame"])
        logger.info(f"✅ Selected {key_frame_count} key frames")

        return frames


# Convenience functions for use in Celery tasks

def extract_and_analyze_frames(
    video_path: str,
    video_id: str,
    interval_seconds: float = 3.0,
    target_key_frames: int = 10
) -> List[Dict]:
    """
    Extract frames and compute all scores in one call

    Args:
        video_path: Path to video file
        video_id: Video UUID
        interval_seconds: Seconds between frames
        target_key_frames: Number of key frames to select

    Returns:
        List of frame dictionaries with all scores computed
    """
    extractor = FrameExtractor(
        interval_seconds=interval_seconds,
        target_key_frames=target_key_frames
    )

    # Extract frames
    frames = extractor.extract_frames(video_path, video_id)

    # Compute scores
    frames = extractor.compute_scene_change_scores(frames)
    frames = extractor.compute_motion_scores(frames)

    # Select key frames
    frames = extractor.select_key_frames(frames)

    return frames


def cleanup_frames(video_id: str, output_dir: str = "uploads/frames"):
    """
    Delete all frames for a video

    Args:
        video_id: Video UUID
        output_dir: Directory containing frames
    """
    frame_dir = Path(output_dir)
    if not frame_dir.exists():
        return

    # Find and delete all frames for this video
    pattern = f"{video_id}_frame_*.jpg"
    deleted_count = 0

    for frame_file in frame_dir.glob(pattern):
        try:
            frame_file.unlink()
            deleted_count += 1
        except Exception as e:
            logger.error(f"Error deleting frame {frame_file}: {e}")

    logger.info(f"Deleted {deleted_count} frames for video {video_id}")
