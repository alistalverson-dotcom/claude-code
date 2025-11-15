"""
Integration tests for visual analysis pipeline
Tests the actual code paths without requiring real video files
"""

import pytest
from decimal import Decimal
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.enhanced_visual_analysis import aggregate_enhanced_analysis


class TestVisualAnalysisIntegration:
    """Integration tests for visual analysis workflow"""

    def test_aggregate_enhanced_analysis_with_realistic_data(self):
        """Test aggregation with realistic analysis data"""
        # Simulate output from 10 frames of analysis
        frame_analyses = [
            {
                'faces_detected': 1,
                'primary_face_confidence': Decimal('0.95'),
                'emotions': {
                    'dominant_emotion': 'confident',
                    'emotion_scores': {
                        'confident': 0.7,
                        'intense': 0.2,
                        'neutral': 0.1,
                    },
                    'emotional_consistency': 0.7,
                },
                'eye_contact': {
                    'eye_contact_score': 0.8,
                    'gaze_direction': 'camera',
                    'eye_contact_quality': 'strong',
                },
                'gestures': [
                    {'gesture': 'pointing', 'handedness': 'Right'},
                ],
                'posture': {
                    'posture_type': 'open',
                    'power_pose': True,
                    'openness_score': 0.85,
                    'shoulder_alignment': 'level',
                    'body_angle': 'forward',
                },
                'camera_framing': {
                    'shot_type': 'medium_close_up',
                    'framing_quality': 'excellent',
                    'rule_of_thirds': True,
                    'headroom': 'good',
                    'composition_score': 0.90,
                },
            }
            for _ in range(10)
        ]

        # Add some variation
        frame_analyses[3]['emotions']['emotion_scores'] = {
            'confident': 0.4,
            'intense': 0.6,
        }
        frame_analyses[3]['gestures'] = [
            {'gesture': 'fist', 'handedness': 'Right'},
        ]
        frame_analyses[5]['posture']['power_pose'] = False
        frame_analyses[7]['eye_contact']['eye_contact_score'] = 0.5

        # Run aggregation
        result = aggregate_enhanced_analysis(frame_analyses)

        # Validate structure
        assert 'emotion_breakdown' in result
        assert 'avg_eye_contact_score' in result
        assert 'power_pose_ratio' in result
        assert 'top_gestures' in result
        assert 'dominant_shot_type' in result
        assert 'avg_framing_quality' in result

        # Validate values
        assert isinstance(result['emotion_breakdown'], dict)
        assert 'confident' in result['emotion_breakdown']
        assert 'intense' in result['emotion_breakdown']

        # Emotions should sum to ~1.0
        total_emotion = sum(result['emotion_breakdown'].values())
        assert 0.95 <= total_emotion <= 1.05

        # Eye contact should be averaged
        assert 0.0 <= result['avg_eye_contact_score'] <= 1.0
        assert result['avg_eye_contact_score'] > 0.5  # Most frames had good eye contact

        # Power pose ratio
        assert 0.0 <= result['power_pose_ratio'] <= 1.0
        assert result['power_pose_ratio'] == 0.9  # 9 out of 10 frames

        # Gestures
        assert len(result['top_gestures']) > 0
        assert result['top_gestures'][0]['gesture'] == 'pointing'
        assert result['top_gestures'][0]['count'] == 9

        # Shot type
        assert result['dominant_shot_type'] == 'medium_close_up'

        # Framing quality
        assert 0.0 <= result['avg_framing_quality'] <= 1.0

        print("\n✅ Aggregation test passed!")
        print(f"   Emotion breakdown: {result['emotion_breakdown']}")
        print(f"   Eye contact: {result['avg_eye_contact_score']:.2f}")
        print(f"   Power poses: {result['power_pose_ratio']:.0%}")
        print(f"   Top gesture: {result['top_gestures'][0]['gesture']} ({result['top_gestures'][0]['count']}x)")

    def test_aggregate_with_mixed_quality_data(self):
        """Test aggregation with varying quality frames"""
        frame_analyses = [
            # Good quality frame
            {
                'faces_detected': 1,
                'emotions': {'emotion_scores': {'confident': 0.8}},
                'eye_contact': {'eye_contact_score': 0.9},
                'gestures': [{'gesture': 'open_palm'}],
                'posture': {'power_pose': True, 'openness_score': 0.9},
                'camera_framing': {'shot_type': 'close_up', 'composition_score': 0.95},
            },
            # Poor quality frame
            {
                'faces_detected': 0,
                'emotions': {'emotion_scores': {'neutral': 1.0}},
                'eye_contact': {'eye_contact_score': 0.0},
                'gestures': [],
                'posture': {'power_pose': False, 'openness_score': 0.3},
                'camera_framing': {'shot_type': 'wide_shot', 'composition_score': 0.4},
            },
            # Medium quality frame
            {
                'faces_detected': 1,
                'emotions': {'emotion_scores': {'confident': 0.5, 'neutral': 0.5}},
                'eye_contact': {'eye_contact_score': 0.6},
                'gestures': [{'gesture': 'pointing'}],
                'posture': {'power_pose': False, 'openness_score': 0.6},
                'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
            },
        ]

        result = aggregate_enhanced_analysis(frame_analyses)

        # Should handle mixed quality
        assert result is not None
        assert 'emotion_breakdown' in result
        assert 'avg_eye_contact_score' in result

        # Average should be reasonable
        assert 0.0 <= result['avg_eye_contact_score'] <= 1.0

        print("\n✅ Mixed quality test passed!")
        print(f"   Average eye contact: {result['avg_eye_contact_score']:.2f}")
        print(f"   Emotions detected: {len(result['emotion_breakdown'])}")

    def test_aggregate_handles_empty_gestures(self):
        """Test that aggregation handles frames with no gestures"""
        frame_analyses = [
            {
                'faces_detected': 1,
                'emotions': {'emotion_scores': {'neutral': 1.0}},
                'eye_contact': {'eye_contact_score': 0.5},
                'gestures': [],  # No gestures
                'posture': {'power_pose': False, 'openness_score': 0.5},
                'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
            }
            for _ in range(5)
        ]

        result = aggregate_enhanced_analysis(frame_analyses)

        # Should return empty gestures list
        assert result['top_gestures'] == []

        print("\n✅ Empty gestures test passed!")

    def test_aggregate_emotion_normalization(self):
        """Test that emotion scores are properly normalized"""
        frame_analyses = [
            {
                'faces_detected': 1,
                'emotions': {
                    'emotion_scores': {
                        'confident': 0.6,
                        'intense': 0.3,
                        'neutral': 0.1,
                    }
                },
                'eye_contact': {'eye_contact_score': 0.5},
                'gestures': [],
                'posture': {'power_pose': False, 'openness_score': 0.5},
                'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
            },
            {
                'faces_detected': 1,
                'emotions': {
                    'emotion_scores': {
                        'confident': 0.2,
                        'intense': 0.7,
                        'focused': 0.1,
                    }
                },
                'eye_contact': {'eye_contact_score': 0.5},
                'gestures': [],
                'posture': {'power_pose': False, 'openness_score': 0.5},
                'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
            },
        ]

        result = aggregate_enhanced_analysis(frame_analyses)

        # Sum of all emotion percentages should be ~1.0
        total = sum(result['emotion_breakdown'].values())
        assert 0.99 <= total <= 1.01

        # All individual emotions should be between 0 and 1
        for emotion, value in result['emotion_breakdown'].items():
            assert 0.0 <= value <= 1.0

        print("\n✅ Emotion normalization test passed!")
        print(f"   Total emotion sum: {total:.3f}")
        print(f"   Emotions: {result['emotion_breakdown']}")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
