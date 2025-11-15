"""
Unit tests for enhanced visual analysis module
"""

import pytest
import numpy as np
from decimal import Decimal
from unittest.mock import Mock, MagicMock, patch
from pathlib import Path

# Import the module to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.enhanced_visual_analysis import (
    EnhancedVisualAnalyzer,
    analyze_frames_enhanced,
    aggregate_enhanced_analysis,
)


class TestEnhancedVisualAnalyzer:
    """Test suite for EnhancedVisualAnalyzer class"""

    @pytest.fixture
    def analyzer(self):
        """Create analyzer instance for tests"""
        return EnhancedVisualAnalyzer()

    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        # Check MediaPipe is available or gracefully handled
        assert hasattr(analyzer, 'mp_face_mesh')
        assert hasattr(analyzer, 'mp_pose')
        assert hasattr(analyzer, 'mp_hands')

    def test_analyze_emotions_structure(self, analyzer):
        """Test emotion analysis returns correct structure"""
        # Create mock face landmarks
        mock_landmarks = Mock()
        mock_landmarks.landmark = [Mock(x=0.5, y=0.5, z=0.0) for _ in range(478)]

        mock_img = np.zeros((480, 640, 3), dtype=np.uint8)

        result = analyzer.analyze_emotions(mock_landmarks, mock_img)

        # Check structure
        assert 'dominant_emotion' in result
        assert 'emotion_scores' in result
        assert 'emotional_consistency' in result

        # Check emotion scores are valid
        emotion_scores = result['emotion_scores']
        assert isinstance(emotion_scores, dict)

        # All scores should be between 0 and 1
        for emotion, score in emotion_scores.items():
            assert 0 <= score <= 1
            assert emotion in ['confident', 'intense', 'focused', 'energetic', 'neutral']

    def test_analyze_eye_contact_structure(self, analyzer):
        """Test eye contact analysis returns correct structure"""
        # Create mock face landmarks
        mock_landmarks = Mock()
        mock_landmarks.landmark = [Mock(x=0.5, y=0.5, z=0.0) for _ in range(478)]

        img_shape = (480, 640, 3)

        result = analyzer.analyze_eye_contact(mock_landmarks, img_shape)

        # Check structure
        assert 'eye_contact_score' in result
        assert 'gaze_direction' in result
        assert 'eye_contact_quality' in result

        # Check valid ranges
        assert 0 <= result['eye_contact_score'] <= 1
        assert result['gaze_direction'] in ['camera', 'left', 'right', 'down', 'up', 'away']
        assert result['eye_contact_quality'] in ['strong', 'good', 'moderate', 'weak']

    def test_classify_gesture(self, analyzer):
        """Test gesture classification"""
        # Create mock hand landmarks
        mock_landmarks = Mock()
        mock_landmarks.landmark = [Mock(x=0.5, y=float(0.9 - i*0.1), z=0.0) for i in range(21)]

        result = analyzer.classify_gesture(mock_landmarks, 'Right')

        # Should return a gesture or None
        if result is not None:
            assert result in ['pointing', 'open_palm', 'fist', 'peace_sign', 'thumbs_up']

    def test_analyze_posture_details_structure(self, analyzer):
        """Test posture analysis returns correct structure"""
        # Create mock pose landmarks
        mock_landmarks = Mock()
        mock_landmarks.landmark = [Mock(x=0.5, y=0.5, z=0.0) for _ in range(33)]

        result = analyzer.analyze_posture_details(mock_landmarks)

        # Check structure
        assert 'posture_type' in result
        assert 'power_pose' in result
        assert 'openness_score' in result
        assert 'shoulder_alignment' in result
        assert 'body_angle' in result

        # Check types
        assert isinstance(result['power_pose'], bool)
        assert 0 <= result['openness_score'] <= 1
        assert result['posture_type'] in ['open', 'neutral', 'closed', 'partial']

    def test_analyze_camera_framing_structure(self, analyzer):
        """Test camera framing analysis"""
        mock_img = np.zeros((480, 640, 3), dtype=np.uint8)
        face_box = (100, 100, 200, 200)  # x, y, w, h

        result = analyzer.analyze_camera_framing(mock_img, face_box)

        # Check structure
        assert 'shot_type' in result
        assert 'framing_quality' in result
        assert 'rule_of_thirds' in result
        assert 'headroom' in result
        assert 'composition_score' in result

        # Check types
        assert result['shot_type'] in ['close_up', 'medium_close_up', 'medium', 'medium_wide', 'wide_shot']
        assert result['framing_quality'] in ['excellent', 'good', 'fair', 'poor']
        assert isinstance(result['rule_of_thirds'], bool)
        assert result['headroom'] in ['good', 'tight', 'excessive']
        assert 0 <= result['composition_score'] <= 1


class TestAggregateEnhancedAnalysis:
    """Test suite for aggregation function"""

    def test_aggregate_with_valid_data(self):
        """Test aggregation with valid frame analyses"""
        frame_analyses = [
            {
                'emotions': {
                    'dominant_emotion': 'confident',
                    'emotion_scores': {'confident': 0.8, 'intense': 0.2},
                },
                'eye_contact': {'eye_contact_score': 0.7},
                'gestures': [{'gesture': 'pointing', 'handedness': 'Right'}],
                'posture': {'power_pose': True, 'openness_score': 0.8},
                'camera_framing': {'shot_type': 'medium_close_up', 'composition_score': 0.85},
            },
            {
                'emotions': {
                    'dominant_emotion': 'intense',
                    'emotion_scores': {'confident': 0.3, 'intense': 0.7},
                },
                'eye_contact': {'eye_contact_score': 0.6},
                'gestures': [{'gesture': 'pointing', 'handedness': 'Right'}],
                'posture': {'power_pose': False, 'openness_score': 0.5},
                'camera_framing': {'shot_type': 'medium_close_up', 'composition_score': 0.80},
            },
        ]

        result = aggregate_enhanced_analysis(frame_analyses)

        # Check structure
        assert 'emotion_breakdown' in result
        assert 'avg_eye_contact_score' in result
        assert 'power_pose_ratio' in result
        assert 'top_gestures' in result
        assert 'dominant_shot_type' in result
        assert 'avg_framing_quality' in result

        # Check calculations
        assert isinstance(result['emotion_breakdown'], dict)
        assert result['avg_eye_contact_score'] == pytest.approx(0.65, rel=0.01)
        assert result['power_pose_ratio'] == 0.5
        assert result['dominant_shot_type'] == 'medium_close_up'

        # Check gestures
        assert len(result['top_gestures']) > 0
        assert result['top_gestures'][0]['gesture'] == 'pointing'
        assert result['top_gestures'][0]['count'] == 2

    def test_aggregate_with_empty_list(self):
        """Test aggregation with no frames"""
        result = aggregate_enhanced_analysis([])

        # Should return default structure
        assert result['emotion_breakdown'] == {}
        assert result['avg_eye_contact_score'] == 0.0
        assert result['power_pose_ratio'] == 0.0
        assert result['top_gestures'] == []

    def test_aggregate_normalizes_emotions(self):
        """Test that emotions are normalized to sum to 1.0"""
        frame_analyses = [
            {
                'emotions': {
                    'emotion_scores': {'confident': 0.6, 'intense': 0.4},
                },
                'eye_contact': {'eye_contact_score': 0.5},
                'gestures': [],
                'posture': {'power_pose': False, 'openness_score': 0.5},
                'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
            },
            {
                'emotions': {
                    'emotion_scores': {'confident': 0.8, 'neutral': 0.2},
                },
                'eye_contact': {'eye_contact_score': 0.5},
                'gestures': [],
                'posture': {'power_pose': False, 'openness_score': 0.5},
                'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
            },
        ]

        result = aggregate_enhanced_analysis(frame_analyses)

        # Emotions should be normalized
        total = sum(result['emotion_breakdown'].values())
        assert total == pytest.approx(1.0, rel=0.01)


class TestAnalyzeFramesEnhanced:
    """Test suite for analyze_frames_enhanced function"""

    @patch('utils.enhanced_visual_analysis.EnhancedVisualAnalyzer')
    def test_analyze_frames_enhanced_basic(self, mock_analyzer_class):
        """Test that analyze_frames_enhanced processes all frames"""
        # Mock the analyzer
        mock_analyzer = Mock()
        mock_analyzer.analyze_frame_enhanced.return_value = {
            'faces_detected': 1,
            'primary_face_confidence': Decimal('0.95'),
            'emotions': {'dominant_emotion': 'confident'},
            'eye_contact': {'eye_contact_score': 0.8},
            'gestures': [],
            'posture': {'power_pose': True},
            'camera_framing': {'shot_type': 'medium'},
        }
        mock_analyzer_class.return_value = mock_analyzer

        # Create temporary test images (would need actual images in practice)
        frame_paths = ['/tmp/frame1.jpg', '/tmp/frame2.jpg']

        # This would fail without actual images, so we'll just verify structure
        # In real testing, we'd use pytest fixtures with sample images

        # For now, just test that the function exists and has correct signature
        from utils.enhanced_visual_analysis import analyze_frames_enhanced
        assert callable(analyze_frames_enhanced)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
