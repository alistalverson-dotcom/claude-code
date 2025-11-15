"""
Logic tests for visual analysis aggregation (no CV dependencies required)
"""

import sys
from pathlib import Path
from decimal import Decimal

# Test the aggregation logic independently
def aggregate_test_data(frame_analyses):
    """
    Simplified version of aggregate logic for testing
    """
    if not frame_analyses:
        return {
            'emotion_breakdown': {},
            'avg_eye_contact_score': 0.0,
            'power_pose_ratio': 0.0,
            'top_gestures': [],
            'dominant_shot_type': 'unknown',
            'avg_framing_quality': 0.0,
        }

    # Aggregate emotions
    all_emotions = {}
    for analysis in frame_analyses:
        if 'emotions' in analysis and 'emotion_scores' in analysis['emotions']:
            for emotion, score in analysis['emotions']['emotion_scores'].items():
                all_emotions[emotion] = all_emotions.get(emotion, 0) + score

    # Normalize emotions
    total = sum(all_emotions.values())
    emotion_breakdown = {}
    if total > 0:
        emotion_breakdown = {k: round(v / total, 2) for k, v in all_emotions.items()}

    # Aggregate eye contact
    eye_contact_scores = [
        a['eye_contact']['eye_contact_score']
        for a in frame_analyses
        if 'eye_contact' in a and 'eye_contact_score' in a['eye_contact']
    ]
    avg_eye_contact = sum(eye_contact_scores) / len(eye_contact_scores) if eye_contact_scores else 0.0

    # Power pose ratio
    power_poses = [
        a['posture']['power_pose']
        for a in frame_analyses
        if 'posture' in a and 'power_pose' in a['posture']
    ]
    power_pose_ratio = sum(power_poses) / len(power_poses) if power_poses else 0.0

    # Count gestures
    gesture_counts = {}
    for analysis in frame_analyses:
        if 'gestures' in analysis:
            for gesture_data in analysis['gestures']:
                if isinstance(gesture_data, dict) and 'gesture' in gesture_data:
                    gesture = gesture_data['gesture']
                    gesture_counts[gesture] = gesture_counts.get(gesture, 0) + 1

    # Top gestures
    top_gestures = [
        {
            'gesture': gesture,
            'count': count,
            'effectiveness': min(1.0, count / len(frame_analyses))
        }
        for gesture, count in sorted(gesture_counts.items(), key=lambda x: x[1], reverse=True)
    ][:5]

    # Dominant shot type
    shot_types = [
        a['camera_framing']['shot_type']
        for a in frame_analyses
        if 'camera_framing' in a and 'shot_type' in a['camera_framing']
    ]
    dominant_shot_type = max(set(shot_types), key=shot_types.count) if shot_types else 'unknown'

    # Average framing
    framing_scores = [
        a['camera_framing']['composition_score']
        for a in frame_analyses
        if 'camera_framing' in a and 'composition_score' in a['camera_framing']
    ]
    avg_framing = sum(framing_scores) / len(framing_scores) if framing_scores else 0.0

    return {
        'emotion_breakdown': emotion_breakdown,
        'avg_eye_contact_score': round(avg_eye_contact, 2),
        'power_pose_ratio': round(power_pose_ratio, 2),
        'top_gestures': top_gestures,
        'dominant_shot_type': dominant_shot_type,
        'avg_framing_quality': round(avg_framing, 2),
    }


def test_basic_aggregation():
    """Test basic aggregation logic"""
    frame_analyses = [
        {
            'emotions': {'emotion_scores': {'confident': 0.7, 'intense': 0.3}},
            'eye_contact': {'eye_contact_score': 0.8},
            'gestures': [{'gesture': 'pointing'}],
            'posture': {'power_pose': True},
            'camera_framing': {'shot_type': 'medium_close_up', 'composition_score': 0.85},
        },
        {
            'emotions': {'emotion_scores': {'confident': 0.5, 'intense': 0.5}},
            'eye_contact': {'eye_contact_score': 0.6},
            'gestures': [{'gesture': 'pointing'}],
            'posture': {'power_pose': False},
            'camera_framing': {'shot_type': 'medium_close_up', 'composition_score': 0.80},
        },
    ]

    result = aggregate_test_data(frame_analyses)

    # Validations
    assert 'emotion_breakdown' in result
    assert 'confident' in result['emotion_breakdown']
    assert 'intense' in result['emotion_breakdown']

    # Emotions should sum to ~1.0
    total_emotion = sum(result['emotion_breakdown'].values())
    assert 0.95 <= total_emotion <= 1.05, f"Emotion sum {total_emotion} not close to 1.0"

    # Eye contact average
    assert result['avg_eye_contact_score'] == 0.7  # (0.8 + 0.6) / 2

    # Power pose ratio
    assert result['power_pose_ratio'] == 0.5  # 1 out of 2

    # Gestures
    assert len(result['top_gestures']) == 1
    assert result['top_gestures'][0]['gesture'] == 'pointing'
    assert result['top_gestures'][0]['count'] == 2

    # Shot type
    assert result['dominant_shot_type'] == 'medium_close_up'

    print("✅ Basic aggregation test passed!")
    return True


def test_emotion_normalization():
    """Test that emotions are normalized correctly"""
    frame_analyses = [
        {
            'emotions': {'emotion_scores': {'confident': 0.6, 'neutral': 0.4}},
            'eye_contact': {'eye_contact_score': 0.5},
            'gestures': [],
            'posture': {'power_pose': False},
            'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
        },
        {
            'emotions': {'emotion_scores': {'intense': 0.8, 'neutral': 0.2}},
            'eye_contact': {'eye_contact_score': 0.5},
            'gestures': [],
            'posture': {'power_pose': False},
            'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
        },
    ]

    result = aggregate_test_data(frame_analyses)

    # Check normalization
    total = sum(result['emotion_breakdown'].values())
    assert 0.99 <= total <= 1.01, f"Normalized sum {total} not close to 1.0"

    print("✅ Emotion normalization test passed!")
    print(f"   Emotions: {result['emotion_breakdown']}")
    print(f"   Sum: {total}")
    return True


def test_empty_input():
    """Test handling of empty input"""
    result = aggregate_test_data([])

    assert result['emotion_breakdown'] == {}
    assert result['avg_eye_contact_score'] == 0.0
    assert result['power_pose_ratio'] == 0.0
    assert result['top_gestures'] == []

    print("✅ Empty input test passed!")
    return True


def test_mixed_quality():
    """Test with varying quality data"""
    frame_analyses = [
        # Good frame
        {
            'emotions': {'emotion_scores': {'confident': 0.9}},
            'eye_contact': {'eye_contact_score': 0.95},
            'gestures': [{'gesture': 'open_palm'}],
            'posture': {'power_pose': True},
            'camera_framing': {'shot_type': 'close_up', 'composition_score': 0.95},
        },
        # Poor frame (no face detected)
        {
            'emotions': {'emotion_scores': {'neutral': 1.0}},
            'eye_contact': {'eye_contact_score': 0.0},
            'gestures': [],
            'posture': {'power_pose': False},
            'camera_framing': {'shot_type': 'wide_shot', 'composition_score': 0.4},
        },
        # Medium frame
        {
            'emotions': {'emotion_scores': {'confident': 0.5, 'neutral': 0.5}},
            'eye_contact': {'eye_contact_score': 0.6},
            'gestures': [{'gesture': 'pointing'}],
            'posture': {'power_pose': False},
            'camera_framing': {'shot_type': 'medium', 'composition_score': 0.7},
        },
    ]

    result = aggregate_test_data(frame_analyses)

    # Should handle mixed quality gracefully
    assert result['avg_eye_contact_score'] > 0.0
    assert result['avg_framing_quality'] > 0.0
    assert len(result['emotion_breakdown']) > 0

    print("✅ Mixed quality test passed!")
    print(f"   Avg eye contact: {result['avg_eye_contact_score']}")
    print(f"   Avg framing: {result['avg_framing_quality']}")
    return True


def run_all_tests():
    """Run all logic tests"""
    print("\n" + "="*60)
    print("VISUAL ANALYSIS LOGIC TESTS")
    print("="*60 + "\n")

    tests = [
        ("Basic Aggregation", test_basic_aggregation),
        ("Emotion Normalization", test_emotion_normalization),
        ("Empty Input", test_empty_input),
        ("Mixed Quality", test_mixed_quality),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        print(f"\nRunning: {name}")
        print("-" * 40)
        try:
            if test_func():
                passed += 1
        except AssertionError as e:
            print(f"❌ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ ERROR: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
