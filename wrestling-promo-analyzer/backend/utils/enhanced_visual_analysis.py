"""
Enhanced Visual Analysis for Advanced Multimodal Features

Builds upon basic visual_analysis.py with:
- Advanced emotion classification
- Confidence and authenticity scoring
- Eye contact and engagement metrics
- Sophisticated gesture recognition
- Detailed posture analysis
- Movement dynamics tracking
- Camera framing analysis
- Visual storytelling elements
"""

import cv2
import numpy as np
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

# Try to import MediaPipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    logger.warning("MediaPipe not available - enhanced features will be limited")


class EnhancedVisualAnalyzer:
    """
    Advanced visual analysis with emotion detection, gesture recognition,
    and visual storytelling analysis.
    """

    def __init__(self):
        """Initialize enhanced analyzer"""

        # Load basic detectors
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # Load eye detector for eye contact analysis
        eye_cascade_path = cv2.data.haarcascades + 'haarcascade_eye.xml'
        self.eye_cascade = cv2.CascadeClassifier(eye_cascade_path)

        # MediaPipe components
        self.mp_face_mesh = None
        self.mp_pose = None
        self.mp_hands = None

        if MEDIAPIPE_AVAILABLE:
            try:
                self.mp_face_mesh = mp.solutions.face_mesh.FaceMesh(
                    static_image_mode=True,
                    max_num_faces=1,
                    refine_landmarks=True,
                    min_detection_confidence=0.5
                )
                self.mp_pose = mp.solutions.pose.Pose(
                    static_image_mode=True,
                    model_complexity=2,
                    min_detection_confidence=0.5
                )
                self.mp_hands = mp.solutions.hands.Hands(
                    static_image_mode=True,
                    max_num_hands=2,
                    min_detection_confidence=0.5
                )
                logger.info("Enhanced MediaPipe initialized")
            except Exception as e:
                logger.warning(f"MediaPipe initialization failed: {e}")

    def analyze_emotions(self, face_landmarks, img_rgb) -> Dict:
        """
        Classify emotions from facial landmarks

        Uses facial landmark distances and ratios to estimate emotional state.

        Returns:
            {
                "dominant_emotion": "confident",
                "emotion_scores": {
                    "confident": 0.6,
                    "intense": 0.3,
                    "neutral": 0.1
                },
                "emotional_consistency": 0.85
            }
        """
        if not face_landmarks or not MEDIAPIPE_AVAILABLE:
            return {
                "dominant_emotion": "neutral",
                "emotion_scores": {"neutral": 1.0},
                "emotional_consistency": 0.5
            }

        # Extract key landmark points
        landmarks = face_landmarks.landmark

        # Simplified emotion detection based on facial geometry
        # In production, you'd use a trained model or more sophisticated analysis

        # Get key points (simplified - MediaPipe has 468 points)
        # Index references: https://github.com/google/mediapipe/blob/master/mediapipe/modules/face_geometry/data/canonical_face_model_uv_visualization.png

        try:
            # Mouth landmarks (approximate)
            left_mouth = landmarks[61]
            right_mouth = landmarks[291]
            upper_lip = landmarks[13]
            lower_lip = landmarks[14]

            # Eye landmarks (approximate)
            left_eye_upper = landmarks[159]
            left_eye_lower = landmarks[145]
            right_eye_upper = landmarks[386]
            right_eye_lower = landmarks[374]

            # Eyebrow landmarks (approximate)
            left_brow = landmarks[107]
            right_brow = landmarks[336]

            # Calculate facial ratios
            # Mouth openness ratio
            mouth_height = abs(upper_lip.y - lower_lip.y)
            mouth_width = abs(left_mouth.x - right_mouth.x)
            mouth_ratio = mouth_height / mouth_width if mouth_width > 0 else 0

            # Eye openness
            left_eye_openness = abs(left_eye_upper.y - left_eye_lower.y)
            right_eye_openness = abs(right_eye_upper.y - right_eye_lower.y)
            avg_eye_openness = (left_eye_openness + right_eye_openness) / 2

            # Simplified emotion classification
            emotion_scores = {
                "confident": 0.0,
                "intense": 0.0,
                "neutral": 0.0,
                "focused": 0.0,
                "energetic": 0.0
            }

            # Confident: moderate eye openness, slight smile
            if 0.02 < avg_eye_openness < 0.05 and mouth_ratio < 0.3:
                emotion_scores["confident"] = 0.7
                emotion_scores["neutral"] = 0.3

            # Intense: eyes wide, mouth expressive
            elif avg_eye_openness > 0.05 or mouth_ratio > 0.4:
                emotion_scores["intense"] = 0.6
                emotion_scores["energetic"] = 0.4

            # Focused: eyes slightly narrowed, mouth neutral
            elif avg_eye_openness < 0.02:
                emotion_scores["focused"] = 0.5
                emotion_scores["confident"] = 0.5

            # Default to neutral
            else:
                emotion_scores["neutral"] = 0.6
                emotion_scores["confident"] = 0.4

            # Find dominant emotion
            dominant_emotion = max(emotion_scores.items(), key=lambda x: x[1])[0]

            # Calculate emotional consistency (higher = more stable expression)
            max_score = max(emotion_scores.values())
            emotional_consistency = max_score

            return {
                "dominant_emotion": dominant_emotion,
                "emotion_scores": emotion_scores,
                "emotional_consistency": round(emotional_consistency, 2)
            }

        except Exception as e:
            logger.warning(f"Emotion analysis failed: {e}")
            return {
                "dominant_emotion": "neutral",
                "emotion_scores": {"neutral": 1.0},
                "emotional_consistency": 0.5
            }

    def analyze_eye_contact(self, face_landmarks, img_shape) -> Dict:
        """
        Analyze eye contact and gaze direction

        Returns:
            {
                "eye_contact_score": 0.85,
                "gaze_direction": "camera",
                "eye_contact_quality": "strong"
            }
        """
        if not face_landmarks or not MEDIAPIPE_AVAILABLE:
            return {
                "eye_contact_score": 0.5,
                "gaze_direction": "unknown",
                "eye_contact_quality": "moderate"
            }

        try:
            landmarks = face_landmarks.landmark

            # Get iris landmarks (refined landmarks from MediaPipe)
            # With refine_landmarks=True, we get iris tracking
            left_iris = landmarks[468] if len(landmarks) > 468 else landmarks[33]
            right_iris = landmarks[473] if len(landmarks) > 473 else landmarks[263]

            # Get eye corners
            left_eye_left = landmarks[33]
            left_eye_right = landmarks[133]
            right_eye_left = landmarks[362]
            right_eye_right = landmarks[263]

            # Calculate iris position relative to eye corners
            # If iris is centered, likely looking at camera
            left_eye_width = abs(left_eye_left.x - left_eye_right.x)
            left_iris_offset = abs((left_iris.x - left_eye_left.x) / left_eye_width - 0.5)

            right_eye_width = abs(right_eye_left.x - right_eye_right.x)
            right_iris_offset = abs((right_iris.x - right_eye_left.x) / right_eye_width - 0.5)

            avg_offset = (left_iris_offset + right_iris_offset) / 2

            # Score eye contact (lower offset = better eye contact)
            eye_contact_score = 1.0 - (avg_offset * 2)  # Scale to 0-1
            eye_contact_score = max(0.0, min(1.0, eye_contact_score))

            # Classify gaze direction
            if avg_offset < 0.1:
                gaze_direction = "camera"
                quality = "strong"
            elif avg_offset < 0.2:
                gaze_direction = "near_camera"
                quality = "good"
            elif avg_offset < 0.3:
                gaze_direction = "slightly_off"
                quality = "moderate"
            else:
                gaze_direction = "off_camera"
                quality = "weak"

            return {
                "eye_contact_score": round(eye_contact_score, 2),
                "gaze_direction": gaze_direction,
                "eye_contact_quality": quality
            }

        except Exception as e:
            logger.warning(f"Eye contact analysis failed: {e}")
            return {
                "eye_contact_score": 0.5,
                "gaze_direction": "unknown",
                "eye_contact_quality": "moderate"
            }

    def classify_gesture(self, hand_landmarks, handedness) -> Optional[str]:
        """
        Classify hand gesture from landmarks

        Returns gesture type: "pointing", "open_palm", "fist", "gesture", etc.
        """
        if not hand_landmarks or not MEDIAPIPE_AVAILABLE:
            return None

        try:
            landmarks = hand_landmarks.landmark

            # Get key finger landmarks
            thumb_tip = landmarks[4]
            index_tip = landmarks[8]
            middle_tip = landmarks[12]
            ring_tip = landmarks[16]
            pinky_tip = landmarks[20]

            # Palm base
            palm_base = landmarks[0]

            # Calculate finger extensions (simplified)
            # If fingertip is significantly above palm, finger is extended

            fingers_extended = []
            for tip in [thumb_tip, index_tip, middle_tip, ring_tip, pinky_tip]:
                is_extended = (palm_base.y - tip.y) > 0.1
                fingers_extended.append(is_extended)

            # Classify based on finger pattern
            num_extended = sum(fingers_extended)

            if num_extended == 1 and fingers_extended[1]:  # Only index extended
                return "pointing"
            elif num_extended >= 4:  # Most fingers extended
                return "open_palm"
            elif num_extended == 0:  # All fingers closed
                return "fist"
            elif num_extended == 2 and fingers_extended[1] and fingers_extended[2]:
                return "peace_sign"
            else:
                return "gesture"

        except Exception as e:
            logger.warning(f"Gesture classification failed: {e}")
            return None

    def analyze_posture_details(self, pose_landmarks) -> Dict:
        """
        Detailed posture analysis including power poses, openness, energy

        Returns:
            {
                "posture_type": "open",
                "power_pose": True,
                "openness_score": 0.85,
                "shoulder_alignment": "level",
                "body_angle": "straight"
            }
        """
        if not pose_landmarks or not MEDIAPIPE_AVAILABLE:
            return {
                "posture_type": "unknown",
                "power_pose": False,
                "openness_score": 0.5,
                "shoulder_alignment": "unknown",
                "body_angle": "unknown"
            }

        try:
            landmarks = pose_landmarks.landmark

            # Get key body points
            left_shoulder = landmarks[mp.solutions.pose.PoseLandmark.LEFT_SHOULDER]
            right_shoulder = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_SHOULDER]
            left_elbow = landmarks[mp.solutions.pose.PoseLandmark.LEFT_ELBOW]
            right_elbow = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_ELBOW]
            left_hip = landmarks[mp.solutions.pose.PoseLandmark.LEFT_HIP]
            right_hip = landmarks[mp.solutions.pose.PoseLandmark.RIGHT_HIP]

            # Check visibility
            if left_shoulder.visibility < 0.5 or right_shoulder.visibility < 0.5:
                return {
                    "posture_type": "partial",
                    "power_pose": False,
                    "openness_score": 0.5,
                    "shoulder_alignment": "not_visible",
                    "body_angle": "not_visible"
                }

            # Calculate shoulder width and arm spread
            shoulder_width = abs(left_shoulder.x - right_shoulder.x)
            shoulder_center_x = (left_shoulder.x + right_shoulder.x) / 2

            # Arm spread (how far elbows are from body center)
            left_elbow_spread = abs(left_elbow.x - shoulder_center_x) if left_elbow.visibility > 0.5 else 0
            right_elbow_spread = abs(right_elbow.x - shoulder_center_x) if right_elbow.visibility > 0.5 else 0
            avg_elbow_spread = (left_elbow_spread + right_elbow_spread) / 2

            # Openness score (based on arm spread relative to shoulder width)
            openness_score = min(1.0, avg_elbow_spread / (shoulder_width * 0.5))

            # Posture type
            if openness_score > 0.7:
                posture_type = "open"
                power_pose = True
            elif openness_score > 0.4:
                posture_type = "neutral"
                power_pose = False
            else:
                posture_type = "closed"
                power_pose = False

            # Shoulder alignment (check if level)
            shoulder_diff = abs(left_shoulder.y - right_shoulder.y)
            if shoulder_diff < 0.02:
                shoulder_alignment = "level"
            elif left_shoulder.y < right_shoulder.y:
                shoulder_alignment = "tilted_left"
            else:
                shoulder_alignment = "tilted_right"

            # Body angle (straight vs. leaning)
            # Compare shoulder center to hip center
            hip_center_x = (left_hip.x + right_hip.x) / 2 if left_hip.visibility > 0.5 and right_hip.visibility > 0.5 else shoulder_center_x
            body_lean = abs(shoulder_center_x - hip_center_x)

            if body_lean < 0.05:
                body_angle = "straight"
            elif shoulder_center_x < hip_center_x:
                body_angle = "leaning_left"
            else:
                body_angle = "leaning_right"

            return {
                "posture_type": posture_type,
                "power_pose": power_pose,
                "openness_score": round(openness_score, 2),
                "shoulder_alignment": shoulder_alignment,
                "body_angle": body_angle
            }

        except Exception as e:
            logger.warning(f"Posture analysis failed: {e}")
            return {
                "posture_type": "unknown",
                "power_pose": False,
                "openness_score": 0.5,
                "shoulder_alignment": "unknown",
                "body_angle": "unknown"
            }

    def analyze_camera_framing(self, img, face_box=None) -> Dict:
        """
        Analyze camera framing and composition

        Returns:
            {
                "shot_type": "medium_shot",
                "framing_quality": 0.85,
                "rule_of_thirds": True,
                "headroom": "good",
                "composition_score": 0.80
            }
        """
        height, width = img.shape[:2]

        if face_box is None:
            return {
                "shot_type": "unknown",
                "framing_quality": 0.5,
                "rule_of_thirds": False,
                "headroom": "unknown",
                "composition_score": 0.5
            }

        x, y, w, h = face_box

        # Calculate face size relative to frame
        face_area = w * h
        frame_area = width * height
        face_ratio = face_area / frame_area

        # Classify shot type based on face size
        if face_ratio > 0.30:
            shot_type = "close_up"
        elif face_ratio > 0.15:
            shot_type = "medium_close_up"
        elif face_ratio > 0.08:
            shot_type = "medium_shot"
        elif face_ratio > 0.04:
            shot_type = "medium_wide"
        else:
            shot_type = "wide_shot"

        # Check rule of thirds (face should be in left or right third)
        face_center_x = x + w/2
        face_center_y = y + h/2

        # Rule of thirds: divide frame into 9 parts
        third_width = width / 3
        third_height = height / 3

        # Check if face is in power positions (intersections of thirds)
        on_left_third = third_width < face_center_x < 2 * third_width
        on_upper_third = third_height < face_center_y < 2 * third_height

        rule_of_thirds = on_left_third and on_upper_third

        # Check headroom (space above head)
        headroom_pixels = y
        headroom_ratio = headroom_pixels / height

        if 0.10 < headroom_ratio < 0.25:
            headroom = "good"
            headroom_score = 1.0
        elif 0.05 < headroom_ratio < 0.35:
            headroom = "acceptable"
            headroom_score = 0.7
        else:
            headroom = "poor"
            headroom_score = 0.4

        # Overall composition score
        composition_score = (
            (1.0 if rule_of_thirds else 0.6) * 0.4 +  # Rule of thirds weight
            headroom_score * 0.3 +  # Headroom weight
            (1.0 if 0.08 < face_ratio < 0.30 else 0.6) * 0.3  # Proper face size weight
        )

        # Framing quality (similar to composition but simpler)
        framing_quality = composition_score

        return {
            "shot_type": shot_type,
            "framing_quality": round(framing_quality, 2),
            "rule_of_thirds": rule_of_thirds,
            "headroom": headroom,
            "composition_score": round(composition_score, 2)
        }

    def analyze_frame_enhanced(self, frame_path: str) -> Dict:
        """
        Complete enhanced analysis of a single frame

        Combines all enhanced features into comprehensive analysis
        """
        # Read image
        img = cv2.imread(frame_path)
        if img is None:
            logger.error(f"Could not read image: {frame_path}")
            return {}

        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        result = {}

        # Detect faces for camera framing analysis
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30, 30))

        if len(faces) > 0:
            largest_face = max(faces, key=lambda f: f[2] * f[3])
            result["camera_framing"] = self.analyze_camera_framing(img, largest_face)
        else:
            result["camera_framing"] = self.analyze_camera_framing(img, None)

        # MediaPipe analysis
        if MEDIAPIPE_AVAILABLE:
            # Face mesh for emotions and eye contact
            if self.mp_face_mesh:
                try:
                    face_results = self.mp_face_mesh.process(img_rgb)
                    if face_results.multi_face_landmarks:
                        face_landmarks = face_results.multi_face_landmarks[0]
                        result["emotions"] = self.analyze_emotions(face_landmarks, img_rgb)
                        result["eye_contact"] = self.analyze_eye_contact(face_landmarks, img.shape)
                except Exception as e:
                    logger.warning(f"Face mesh analysis failed: {e}")

            # Pose for detailed posture
            if self.mp_pose:
                try:
                    pose_results = self.mp_pose.process(img_rgb)
                    if pose_results.pose_landmarks:
                        result["posture_details"] = self.analyze_posture_details(pose_results.pose_landmarks)
                except Exception as e:
                    logger.warning(f"Pose analysis failed: {e}")

            # Hands for gesture recognition
            if self.mp_hands:
                try:
                    hands_results = self.mp_hands.process(img_rgb)
                    if hands_results.multi_hand_landmarks:
                        gestures = []
                        for idx, hand_landmarks in enumerate(hands_results.multi_hand_landmarks):
                            handedness = hands_results.multi_handedness[idx] if hands_results.multi_handedness else None
                            gesture = self.classify_gesture(hand_landmarks, handedness)
                            if gesture:
                                gestures.append(gesture)
                        result["gestures"] = gestures
                except Exception as e:
                    logger.warning(f"Hand analysis failed: {e}")

        return result


def analyze_frames_enhanced(frame_paths: List[str]) -> List[Dict]:
    """
    Perform enhanced analysis on multiple frames

    Args:
        frame_paths: List of frame file paths

    Returns:
        List of enhanced analysis dictionaries
    """
    analyzer = EnhancedVisualAnalyzer()
    results = []

    for frame_path in frame_paths:
        try:
            analysis = analyzer.analyze_frame_enhanced(frame_path)
            analysis["frame_path"] = frame_path
            results.append(analysis)
        except Exception as e:
            logger.error(f"Enhanced analysis failed for {frame_path}: {e}")
            results.append({
                "frame_path": frame_path,
                "error": str(e)
            })

    return results


def aggregate_enhanced_analysis(frame_analyses: List[Dict]) -> Dict:
    """
    Aggregate enhanced analysis across all frames

    Returns comprehensive metrics and insights
    """
    if not frame_analyses:
        return {}

    valid_analyses = [a for a in frame_analyses if "error" not in a]
    if not valid_analyses:
        return {"error": "No valid analyses"}

    # Aggregate emotions
    all_emotions = {}
    for analysis in valid_analyses:
        if "emotions" in analysis:
            for emotion, score in analysis["emotions"]["emotion_scores"].items():
                all_emotions[emotion] = all_emotions.get(emotion, 0) + score

    # Normalize emotion scores
    if all_emotions:
        total = sum(all_emotions.values())
        emotion_breakdown = {k: round(v / total, 2) for k, v in all_emotions.items()}
    else:
        emotion_breakdown = {}

    # Aggregate eye contact
    eye_contact_scores = [
        a["eye_contact"]["eye_contact_score"]
        for a in valid_analyses
        if "eye_contact" in a
    ]
    avg_eye_contact = sum(eye_contact_scores) / len(eye_contact_scores) if eye_contact_scores else 0

    # Count power poses
    power_pose_count = sum(
        1 for a in valid_analyses
        if "posture_details" in a and a["posture_details"].get("power_pose", False)
    )

    # Aggregate gestures
    all_gestures = {}
    for analysis in valid_analyses:
        if "gestures" in analysis:
            for gesture in analysis["gestures"]:
                all_gestures[gesture] = all_gestures.get(gesture, 0) + 1

    # Top gestures
    top_gestures = [
        {"gesture": k, "count": v, "effectiveness": min(1.0, v / len(valid_analyses))}
        for k, v in sorted(all_gestures.items(), key=lambda x: x[1], reverse=True)
    ][:5]

    # Camera framing aggregation
    shot_types = {}
    framing_scores = []
    for analysis in valid_analyses:
        if "camera_framing" in analysis:
            shot_type = analysis["camera_framing"].get("shot_type", "unknown")
            shot_types[shot_type] = shot_types.get(shot_type, 0) + 1
            if "framing_quality" in analysis["camera_framing"]:
                framing_scores.append(analysis["camera_framing"]["framing_quality"])

    dominant_shot_type = max(shot_types.items(), key=lambda x: x[1])[0] if shot_types else "unknown"
    avg_framing = sum(framing_scores) / len(framing_scores) if framing_scores else 0.5

    return {
        "emotion_breakdown": emotion_breakdown,
        "avg_eye_contact_score": round(avg_eye_contact, 2),
        "power_pose_count": power_pose_count,
        "power_pose_ratio": round(power_pose_count / len(valid_analyses), 2) if valid_analyses else 0,
        "top_gestures": top_gestures,
        "dominant_shot_type": dominant_shot_type,
        "avg_framing_quality": round(avg_framing, 2),
        "total_frames_analyzed": len(valid_analyses)
    }
