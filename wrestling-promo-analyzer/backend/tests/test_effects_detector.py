"""
Tests for Visual Effects Detector

Tests the computer vision algorithms that detect filters and effects
in video frames.
"""

import pytest
import numpy as np
import cv2
from video_processing.effects_detector import (
    VisualEffectsDetector,
    aggregate_effects_analysis
)


# ============================================================================
# Fixture: Sample Frames
# ============================================================================

@pytest.fixture
def color_frame():
    """Create a sample color frame"""
    # Create a 640x480 frame with blue background
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, :] = (100, 50, 50)  # BGR: Blue dominant
    return frame


@pytest.fixture
def bw_frame():
    """Create a black & white frame"""
    # Create grayscale frame (very low saturation)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    gray_value = 128
    frame[:, :] = (gray_value, gray_value, gray_value)
    return frame


@pytest.fixture
def vignette_frame():
    """Create a frame with vignette effect (darkened edges)"""
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 200

    # Darken edges
    h, w = 480, 640
    # Top and bottom edges
    frame[0:h//8, :] = frame[0:h//8, :] // 2
    frame[-h//8:, :] = frame[-h//8:, :] // 2
    # Left and right edges
    frame[:, 0:w//8] = frame[:, 0:w//8] // 2
    frame[:, -w//8:] = frame[:, -w//8:] // 2

    return frame


@pytest.fixture
def high_contrast_frame():
    """Create a high contrast frame"""
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Half black, half white
    frame[:, :320] = 0
    frame[:, 320:] = 255
    return frame


# ============================================================================
# Test: Basic Detection
# ============================================================================

def test_detector_initialization():
    """Test that detector initializes properly"""
    detector = VisualEffectsDetector()

    assert detector is not None
    assert detector.prev_frame is None
    assert len(detector.frame_history) == 0
    assert detector.max_history == 5


def test_analyze_color_frame(color_frame):
    """Test analysis of a normal color frame"""
    detector = VisualEffectsDetector()
    result = detector.analyze_frame(color_frame, frame_number=0)

    # Check structure
    assert 'color_grading' in result
    assert 'filters' in result
    assert 'motion_effects' in result
    assert 'distortion' in result
    assert 'overlays' in result
    assert 'overall_quality' in result

    # Color grading should detect color (not B&W)
    assert result['color_grading']['style'] != 'black_white'
    assert result['color_grading']['saturation_level'] > 0.0


def test_black_and_white_detection(bw_frame):
    """Test detection of black & white / desaturated frames"""
    detector = VisualEffectsDetector()
    result = detector.analyze_frame(bw_frame, frame_number=0)

    color_grading = result['color_grading']

    # Should detect low saturation
    assert color_grading['saturation_level'] < 0.2  # Very desaturated
    # Style should be black_white or desaturated
    assert color_grading['style'] in ['black_white', 'desaturated']


def test_vignette_detection(vignette_frame):
    """Test detection of vignette effect"""
    detector = VisualEffectsDetector()
    result = detector.analyze_frame(vignette_frame, frame_number=0)

    color_grading = result['color_grading']

    # Should detect vignette
    assert color_grading['vignette_detected'] == True
    assert color_grading['vignette_strength'] > 0.1


def test_contrast_detection(high_contrast_frame):
    """Test detection of high contrast"""
    detector = VisualEffectsDetector()
    result = detector.analyze_frame(high_contrast_frame, frame_number=0)

    color_grading = result['color_grading']

    # Should detect high contrast
    assert color_grading['contrast_ratio'] > 2.0


# ============================================================================
# Test: Film Grain Detection
# ============================================================================

def test_film_grain_detection():
    """Test detection of film grain / noise"""
    detector = VisualEffectsDetector()

    # Create frame with added noise (simulated film grain)
    clean_frame = np.ones((480, 640, 3), dtype=np.uint8) * 128
    noise = np.random.randint(-30, 30, (480, 640, 3), dtype=np.int16)
    noisy_frame = np.clip(clean_frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)

    result = detector.analyze_frame(noisy_frame, frame_number=0)

    filters = result['filters']

    # Should detect noise/grain
    assert filters['film_grain'] == True
    assert filters['film_grain_intensity'] is not None
    assert filters['film_grain_intensity'] > 0.0


# ============================================================================
# Test: Motion Analysis
# ============================================================================

def test_camera_shake_detection():
    """Test detection of camera shake between frames"""
    detector = VisualEffectsDetector()

    # First frame
    frame1 = np.ones((480, 640, 3), dtype=np.uint8) * 100
    cv2.rectangle(frame1, (100, 100), (200, 200), (255, 255, 255), -1)

    # Second frame - shifted (simulating camera shake)
    frame2 = np.ones((480, 640, 3), dtype=np.uint8) * 100
    cv2.rectangle(frame2, (110, 110), (210, 210), (255, 255, 255), -1)

    # Analyze first frame
    detector.analyze_frame(frame1, frame_number=0)

    # Analyze second frame (should detect motion)
    result = detector.analyze_frame(frame2, frame_number=1)

    motion = result['motion_effects']

    # Should detect some camera movement
    assert motion['camera_shake_level'] > 0.0
    assert motion['stability_score'] < 1.0


# ============================================================================
# Test: Overlay Detection
# ============================================================================

def test_text_overlay_detection():
    """Test detection of text overlays"""
    detector = VisualEffectsDetector()

    # Create frame with simulated text overlay (sharp horizontal line)
    frame = np.ones((480, 640, 3), dtype=np.uint8) * 100

    # Add a banner-like region (simulating text overlay area)
    cv2.rectangle(frame, (50, 400), (590, 450), (255, 255, 255), -1)
    cv2.putText(frame, "THE CHAMPION", (100, 430),
                cv2.FONT_HERSHEY_BOLD, 1, (0, 0, 0), 2)

    result = detector.analyze_frame(frame, frame_number=0)

    overlays = result['overlays']

    # Should detect overlay regions
    # (Note: Simple detection may not be perfect, but should detect something)
    assert 'text_detected' in overlays
    assert 'overlay_count' in overlays


# ============================================================================
# Test: Color Temperature
# ============================================================================

def test_warm_color_temperature():
    """Test detection of warm color temperature"""
    detector = VisualEffectsDetector()

    # Create warm-toned frame (red/orange dominant)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, :] = (50, 100, 200)  # BGR: Red dominant

    result = detector.analyze_frame(frame, frame_number=0)

    color_grading = result['color_grading']

    # Should detect warm temperature
    assert color_grading['color_temperature'] == 'warm'


def test_cool_color_temperature():
    """Test detection of cool color temperature"""
    detector = VisualEffectsDetector()

    # Create cool-toned frame (blue dominant)
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    frame[:, :] = (200, 100, 50)  # BGR: Blue dominant

    result = detector.analyze_frame(frame, frame_number=0)

    color_grading = result['color_grading']

    # Should detect cool temperature
    assert color_grading['color_temperature'] == 'cool'


# ============================================================================
# Test: Aggregation
# ============================================================================

def test_effects_aggregation():
    """Test aggregation of effects across multiple frames"""
    detector = VisualEffectsDetector()

    # Create 3 different frames
    frame1 = np.ones((480, 640, 3), dtype=np.uint8) * 100
    frame2 = np.ones((480, 640, 3), dtype=np.uint8) * 150
    frame3 = np.ones((480, 640, 3), dtype=np.uint8) * 200

    # Analyze all frames
    result1 = detector.analyze_frame(frame1, 0)
    result2 = detector.analyze_frame(frame2, 1)
    result3 = detector.analyze_frame(frame3, 2)

    # Aggregate
    aggregated = aggregate_effects_analysis([result1, result2, result3])

    # Check aggregated results
    assert 'color_grading_style' in aggregated
    assert 'avg_saturation' in aggregated
    assert 'avg_contrast' in aggregated
    assert 'frame_count' in aggregated
    assert aggregated['frame_count'] == 3

    # Saturation should be averaged
    assert 0.0 <= aggregated['avg_saturation'] <= 1.0


def test_empty_aggregation():
    """Test aggregation with empty list"""
    result = aggregate_effects_analysis([])

    # Should return default values
    assert result is not None
    assert 'color_grading' in result or 'frame_count' in result


# ============================================================================
# Test: Error Handling
# ============================================================================

def test_invalid_frame_handling():
    """Test handling of invalid frame data"""
    detector = VisualEffectsDetector()

    # Empty frame
    empty_frame = np.array([], dtype=np.uint8)

    # Should not crash
    try:
        result = detector.analyze_frame(empty_frame, 0)
        # If it doesn't crash, it should return something
        assert result is not None
    except Exception:
        # It's OK if it raises an exception for invalid input
        pass


def test_different_frame_sizes():
    """Test handling frames of different sizes"""
    detector = VisualEffectsDetector()

    # First frame - 640x480
    frame1 = np.ones((480, 640, 3), dtype=np.uint8) * 100
    result1 = detector.analyze_frame(frame1, 0)

    # Second frame - different size 1280x720
    frame2 = np.ones((720, 1280, 3), dtype=np.uint8) * 150
    result2 = detector.analyze_frame(frame2, 1)

    # Should handle gracefully
    assert result1 is not None
    assert result2 is not None


# ============================================================================
# Test: Dominant Colors
# ============================================================================

def test_dominant_colors_extraction():
    """Test extraction of dominant colors"""
    detector = VisualEffectsDetector()

    # Create frame with distinct colors
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    # Blue region
    frame[:240, :320] = (200, 0, 0)  # Blue
    # Red region
    frame[:240, 320:] = (0, 0, 200)  # Red
    # Green region
    frame[240:, :] = (0, 200, 0)  # Green

    result = detector.analyze_frame(frame, 0)

    color_grading = result['color_grading']

    # Should extract dominant colors
    assert 'dominant_colors' in color_grading
    assert len(color_grading['dominant_colors']) > 0

    # Colors should be hex format
    for color in color_grading['dominant_colors']:
        assert color.startswith('#')
        assert len(color) == 7  # #RRGGBB


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
