"""
Visual Analysis Utilities for Multimodal Analysis

Detects and analyzes visual features in video frames:
- Face detection and landmarks
- Pose estimation (body language)
- Emotion recognition
- Production quality metrics
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Try to import MediaPipe (optional dependency)
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("MediaPipe not available - some visual features will be limited")


class VisualAnalysisError(Exception):
    """Error during visual analysis"""
    pass


class VisualAnalyzer:
    """
    Analyzes visual features in video frames

    Uses OpenCV for basic detection and optionally MediaPipe for advanced features.
    """

    def __init__(self):
        """Initialize visual analyzer with detection models"""

        # Load OpenCV face detector (Haar Cascade - lightweight)
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # Initialize MediaPipe if available
        self.mp_face_mesh = None
        self.mp_pose = None
        self.mp_hands = None

        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    min_detection_confidence=0.5
                )
                self.mp_pose = mp.solutions.pose.Pose(
                    static_image_mode=True,
                    min_detection_confidence=0.5
                )
                self.mp_hands = mp.solutions.hands.Hands(
                    static_image_mode=True,
                    max_num_hands=2,
                    min_detection_confidence=0.5
                )
                logger.info("MediaPipe initialized successfully")
            except Exception as e:
                logger.warning(f"MediaPipe initialization failed: {e}")
                MEDIAPIPE_AVAILABLE = False

    def analyze_frame(self, frame_path: str) -> Dict:
        """
        Analyze visual features in a single frame

        Args:
            frame_path: Path to frame image file

        Returns:
            Dictionary with visual analysis:
            {
                "faces_detected": 1,
                "primary_face_confidence": 0.95,
                "face_landmarks": {...},
                "pose_detected": True,
                "pose_landmarks": {...},
                "hands_detected": 0,
                "production_quality": {...}
            }
        """
        # Read image
        img = cv2.imread(frame_path)
        if img is None:
            raise VisualAnalysisError(f"Could not read image: {frame_path}")

        # Convert to RGB for MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        # Analyze different features
        face_results = self._detect_faces(img, img_rgb)
        pose_results = self._detect_pose(img_rgb)
        hands_results = self._detect_hands(img_rgb)
        production_results = self._analyze_production_quality(img)

        # Combine results
        analysis = {
            **face_results,
            **pose_results,
            **hands_results,
            **production_results,
        }

        return analysis

    def _detect_faces(self, img_bgr, img_rgb) -> Dict:
        """
        Detect faces using OpenCV and optionally MediaPipe

        Args:
            img_bgr: Image in BGR format (OpenCV)
            img_rgb: Image in RGB format (MediaPipe)

        Returns:
            Dictionary with face detection results
        """
        # Convert to grayscale for OpenCV
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # Detect faces using Haar Cascade
        faces = self.face_cascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        result = {
            "faces_detected": len(faces),
            "primary_face_confidence": Decimal("0.0"),
            "face_landmarks": None,
        }

        if len(faces) == 0:
            return result

        # Get largest face (likely the speaker)
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        x, y, w, h = largest_face

        # Estimate confidence based on face size relative to image
        img_area = img_bgr.shape[0] * img_bgr.shape[1]
        face_area = w * h
        size_ratio = face_area / img_area

        # Confidence based on size (larger face = more confident detection)
        # Typical good framing: face is 10-30% of image
        if 0.05 < size_ratio < 0.50:
            confidence = min(0.95, size_ratio * 4)  # Scale to 0-1 range
        else:
            confidence = 0.60  # Lower confidence for poorly framed shots

        result["primary_face_confidence"] = Decimal(str(round(confidence, 2)))

        # Get detailed face landmarks using MediaPipe if available
        if MEDIAPIPE_AVAILABLE and self.mp_face_mesh:
            try:
                face_mesh_results = self.mp_face_mesh.process(img_rgb)

                if face_mesh_results.multi_face_landmarks:
                    landmarks = face_mesh_results.multi_face_landmarks[0]

                    # Extract key landmarks (simplified)
                    # MediaPipe face mesh has 468 landmarks
                    result["face_landmarks"] = {
                        "landmark_count": len(landmarks.landmark),
                        "has_detailed_mesh": True,
                    }

                    # Increase confidence if MediaPipe also detects face
                    result["primary_face_confidence"] = Decimal("0.95")

            except Exception as e:
                logger.warning(f"MediaPipe face mesh failed: {e}")

        return result

    def _detect_pose(self, img_rgb) -> Dict:
        """
        Detect body pose using MediaPipe

        Args:
            img_rgb: Image in RGB format

        Returns:
            Dictionary with pose detection results
        """
        result = {
            "pose_detected": False,
            "pose_landmarks": None,
            "posture_type": None,
        }

        if not MEDIAPIPE_AVAILABLE or not self.mp_pose:
            return result

        try:
            pose_results = self.mp_pose.process(img_rgb)

            if pose_results.pose_landmarks:
                result["pose_detected"] = True

                # Analyze posture
                landmarks = pose_results.pose_landmarks.landmark

                # Get key points
                left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
                right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
                left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]
                right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW]

                # Analyze posture (simplified)
                # Check if arms are visible and spread (open posture)
                if all([left_shoulder.visibility > 0.5, right_shoulder.visibility > 0.5,
                        left_elbow.visibility > 0.5, right_elbow.visibility > 0.5]):

                    # Calculate shoulder width
                    shoulder_width = abs(left_shoulder.x - right_shoulder.x)

                    # Calculate elbow spread (how far elbows are from body)
                    shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2
                    left_elbow_distance = abs(left_elbow.x - shoulder_center_x)
                    right_elbow_distance = abs(right_elbow.x - shoulder_center_x)
                    avg_elbow_spread = (left_elbow_distance + right_elbow_distance) / 2

                    # Determine posture type
                    if avg_elbow_spread > shoulder_width * 0.5:
                        result["posture_type"] = "open"  # Arms spread, confident
                    else:
                        result["posture_type"] = "neutral"  # Arms closer to body
                else:
                    result["posture_type"] = "partial"  # Not all body parts visible

                result["pose_landmarks"] = {
                    "landmark_count": len(landmarks),
                    "posture": result["posture_type"],
                }

        except Exception as e:
            logger.warning(f"MediaPipe pose detection failed: {e}")

        return result

    def _detect_hands(self, img_rgb) -> Dict:
        """
        Detect hands and gestures using MediaPipe

        Args:
            img_rgb: Image in RGB format

        Returns:
            Dictionary with hand detection results
        """
        result = {
            "hands_detected": 0,
            "hand_landmarks": None,
        }

        if not MEDIAPIPE_AVAILABLE or not self.mp_hands:
            return result

        try:
            hands_results = self.mp_hands.process(img_rgb)

            if hands_results.multi_hand_landmarks:
                result["hands_detected"] = len(hands_results.multi_hand_landmarks)

                # Store landmark count for each hand
                result["hand_landmarks"] = {
                    "hands": [
                        {"landmark_count": len(hand.landmark)}
                        for hand in hands_results.multi_hand_landmarks
                    ]
                }

        except Exception as e:
            logger.warning(f"MediaPipe hand detection failed: {e}")

        return result

    def _analyze_production_quality(self, img_bgr) -> Dict:
        """
        Analyze production quality (lighting, sharpness, etc.)

        Args:
            img_bgr: Image in BGR format

        Returns:
            Dictionary with production quality metrics
        """
        # Convert to grayscale
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)

        # 1. Brightness (average pixel value)
        brightness = np.mean(gray) / 255.0  # Normalize to 0-1

        # Good brightness is around 0.4-0.6 (not too dark, not too bright)
        if 0.3 < brightness < 0.7:
            brightness_score = 1.0 - abs(brightness - 0.5) * 2
        else:
            brightness_score = max(0.0, 1.0 - abs(brightness - 0.5) * 3)

        # 2. Contrast (standard deviation of pixel values)
        contrast = np.std(gray) / 128.0  # Normalize
        contrast_score = min(1.0, contrast)

        # 3. Sharpness (Laplacian variance)
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
        sharpness_score = min(1.0, laplacian_var / 500.0)

        # 4. Overall lighting quality (combination of brightness and contrast)
        lighting_quality = (brightness_score * 0.6 + contrast_score * 0.4)

        return {
            "production_quality": {
                "brightness": round(brightness, 3),
                "brightness_score": round(brightness_score, 3),
                "contrast_score": round(contrast_score, 3),
                "sharpness_score": round(sharpness_score, 3),
                "lighting_quality": round(lighting_quality, 3),
            }
        }


# Convenience function for batch analysis

def analyze_frames(frame_paths: List[str]) -> List[Dict]:
    """
    Analyze multiple frames

    Args:
        frame_paths: List of frame file paths

    Returns:
        List of analysis dictionaries
    """
    analyzer = VisualAnalyzer()
    results = []

    for frame_path in frame_paths:
        try:
            analysis = analyzer.analyze_frame(frame_path)
            analysis["frame_path"] = frame_path
            results.append(analysis)
        except Exception as e:
            logger.error(f"Error analyzing {frame_path}: {e}")
            # Add failed result
            results.append({
                "frame_path": frame_path,
                "error": str(e),
                "faces_detected": 0,
            })

    return results


def get_key_frame_analysis_summary(frame_analyses: List[Dict]) -> Dict:
    """
    Summarize analysis results across multiple key frames

    Args:
        frame_analyses: List of frame analysis dictionaries

    Returns:
        Summary dictionary with aggregate metrics
    """
    if not frame_analyses:
        return {}

    # Filter out failed analyses
    valid_analyses = [a for a in frame_analyses if "error" not in a]

    if not valid_analyses:
        return {"error": "No valid frame analyses"}

    # Aggregate metrics
    total_faces = sum(a.get("faces_detected", 0) for a in valid_analyses)
    frames_with_faces = sum(1 for a in valid_analyses if a.get("faces_detected", 0) > 0)
    frames_with_pose = sum(1 for a in valid_analyses if a.get("pose_detected", False))

    avg_face_confidence = 0.0
    if frames_with_faces > 0:
        confidences = [float(a.get("primary_face_confidence", 0))
                       for a in valid_analyses if a.get("faces_detected", 0) > 0]
        avg_face_confidence = sum(confidences) / len(confidences)

    # Production quality averages
    lighting_scores = []
    for a in valid_analyses:
        pq = a.get("production_quality", {})
        if "lighting_quality" in pq:
            lighting_scores.append(pq["lighting_quality"])

    avg_lighting = sum(lighting_scores) / len(lighting_scores) if lighting_scores else 0.0

    # Posture analysis
    posture_types = [a.get("posture_type") for a in valid_analyses if a.get("posture_type")]
    open_postures = sum(1 for p in posture_types if p == "open")

    return {
        "total_frames_analyzed": len(valid_analyses),
        "frames_with_faces": frames_with_faces,
        "face_detection_rate": frames_with_faces / len(valid_analyses) if valid_analyses else 0.0,
        "avg_face_confidence": round(avg_face_confidence, 3),
        "frames_with_pose_detected": frames_with_pose,
        "pose_detection_rate": frames_with_pose / len(valid_analyses) if valid_analyses else 0.0,
        "open_posture_count": open_postures,
        "avg_lighting_quality": round(avg_lighting, 3),
    }
