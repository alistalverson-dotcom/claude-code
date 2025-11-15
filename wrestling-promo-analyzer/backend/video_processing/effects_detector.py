"""
Visual Effects and Filters Detection Module

Detects and analyzes production techniques, color grading, and visual effects
in wrestling promo videos.
"""

import cv2
import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class ColorGradingAnalysis:
    """Color grading analysis results"""
    style: str  # 'black_white', 'sepia', 'color_graded', 'natural'
    dominant_colors: List[str]  # Hex color codes
    saturation_level: float  # 0-1
    contrast_ratio: float  # 0-5+
    vignette_detected: bool
    vignette_strength: float  # 0-1
    color_palette: str  # 'warm', 'cool', 'teal_orange', 'neutral'
    color_temperature: str  # 'warm', 'cool', 'neutral'


@dataclass
class FilterAnalysis:
    """Applied filters analysis"""
    film_grain: bool
    film_grain_intensity: Optional[float]  # 0-1
    lens_blur: Optional[float]  # 0-1
    chromatic_aberration: bool
    sharpening: Optional[float]  # 0-1
    overall_sharpness: float  # 0-1


@dataclass
class MotionEffectsAnalysis:
    """Motion-based effects analysis"""
    camera_shake_level: float  # 0-1
    motion_blur_present: bool
    handheld_style: bool
    stability_score: float  # 0-1, higher = more stable


@dataclass
class DistortionAnalysis:
    """Distortion effects analysis"""
    digital_noise: float  # 0-1
    lens_distortion: float  # 0-1
    compression_artifacts: bool
    artifact_severity: float  # 0-1


@dataclass
class OverlayAnalysis:
    """Overlay and composite effects"""
    text_detected: bool
    text_coverage_percentage: float  # 0-100
    graphics_present: bool
    overlay_count: int


class VisualEffectsDetector:
    """
    Detects visual filters and effects in video frames using computer vision.
    """

    def __init__(self):
        self.prev_frame = None
        self.frame_history = []
        self.max_history = 5

    def analyze_frame(self, frame: np.ndarray, frame_number: int = 0) -> Dict:
        """
        Analyze a single frame for visual effects and filters.

        Args:
            frame: BGR image array
            frame_number: Frame sequence number

        Returns:
            Dictionary containing all effects analysis
        """
        try:
            # Store for motion analysis
            if len(self.frame_history) >= self.max_history:
                self.frame_history.pop(0)
            self.frame_history.append(frame.copy())

            results = {
                'color_grading': self._analyze_color_grading(frame),
                'filters': self._analyze_filters(frame),
                'motion_effects': self._analyze_motion_effects(frame),
                'distortion': self._analyze_distortion(frame),
                'overlays': self._analyze_overlays(frame),
                'overall_quality': self._assess_overall_quality(frame)
            }

            self.prev_frame = frame.copy()
            return results

        except Exception as e:
            logger.error(f"Error analyzing frame {frame_number}: {e}")
            return self._get_default_analysis()

    def _analyze_color_grading(self, frame: np.ndarray) -> Dict:
        """Analyze color grading and color palette"""
        try:
            # Convert to different color spaces
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            lab = cv2.cvtColor(frame, cv2.COLOR_BGR2LAB)

            # Saturation analysis
            saturation = hsv[:, :, 1]
            avg_saturation = np.mean(saturation) / 255.0

            # Determine style
            if avg_saturation < 0.1:
                style = 'black_white'
            elif avg_saturation < 0.3:
                style = 'desaturated'
            elif self._is_sepia(frame):
                style = 'sepia'
            elif avg_saturation > 0.6:
                style = 'vivid'
            else:
                style = 'natural'

            # Dominant colors
            dominant_colors = self._get_dominant_colors(frame)

            # Contrast ratio
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            contrast_ratio = self._calculate_contrast_ratio(gray)

            # Vignette detection
            vignette_detected, vignette_strength = self._detect_vignette(gray)

            # Color temperature
            color_temp, color_palette = self._analyze_color_temperature(frame)

            return {
                'style': style,
                'dominant_colors': dominant_colors,
                'saturation_level': float(avg_saturation),
                'contrast_ratio': float(contrast_ratio),
                'vignette_detected': vignette_detected,
                'vignette_strength': float(vignette_strength),
                'color_palette': color_palette,
                'color_temperature': color_temp
            }

        except Exception as e:
            logger.error(f"Error in color grading analysis: {e}")
            return self._get_default_color_grading()

    def _analyze_filters(self, frame: np.ndarray) -> Dict:
        """Detect applied filters"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Film grain detection
            film_grain, grain_intensity = self._detect_film_grain(gray)

            # Blur detection
            blur_level = self._detect_blur(gray)

            # Chromatic aberration
            chromatic_ab = self._detect_chromatic_aberration(frame)

            # Sharpening detection
            sharpness = self._calculate_sharpness(gray)

            return {
                'film_grain': film_grain,
                'film_grain_intensity': float(grain_intensity) if film_grain else None,
                'lens_blur': float(blur_level) if blur_level > 0.1 else None,
                'chromatic_aberration': chromatic_ab,
                'sharpening': float(sharpness),
                'overall_sharpness': float(sharpness)
            }

        except Exception as e:
            logger.error(f"Error in filter analysis: {e}")
            return self._get_default_filters()

    def _analyze_motion_effects(self, frame: np.ndarray) -> Dict:
        """Analyze motion-based effects"""
        try:
            if self.prev_frame is None or self.prev_frame.shape != frame.shape:
                return {
                    'camera_shake_level': 0.0,
                    'motion_blur_present': False,
                    'handheld_style': False,
                    'stability_score': 1.0
                }

            # Camera shake detection
            shake_level = self._detect_camera_shake(frame, self.prev_frame)

            # Motion blur
            motion_blur = self._detect_motion_blur(frame)

            # Handheld style (moderate shake)
            handheld = 0.1 < shake_level < 0.5

            # Stability score
            stability = 1.0 - min(shake_level, 1.0)

            return {
                'camera_shake_level': float(shake_level),
                'motion_blur_present': motion_blur,
                'handheld_style': handheld,
                'stability_score': float(stability)
            }

        except Exception as e:
            logger.error(f"Error in motion analysis: {e}")
            return {
                'camera_shake_level': 0.0,
                'motion_blur_present': False,
                'handheld_style': False,
                'stability_score': 1.0
            }

    def _analyze_distortion(self, frame: np.ndarray) -> Dict:
        """Detect distortion effects"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Digital noise level
            noise = self._calculate_noise_level(gray)

            # Lens distortion (edge curvature)
            lens_dist = self._detect_lens_distortion(gray)

            # Compression artifacts
            artifacts = self._detect_compression_artifacts(frame)

            return {
                'digital_noise': float(noise),
                'lens_distortion': float(lens_dist),
                'compression_artifacts': artifacts,
                'artifact_severity': float(noise * 0.5 + (0.5 if artifacts else 0))
            }

        except Exception as e:
            logger.error(f"Error in distortion analysis: {e}")
            return {
                'digital_noise': 0.0,
                'lens_distortion': 0.0,
                'compression_artifacts': False,
                'artifact_severity': 0.0
            }

    def _analyze_overlays(self, frame: np.ndarray) -> Dict:
        """Detect overlays and graphics"""
        try:
            # Text detection using edge detection and contour analysis
            text_detected, coverage = self._detect_text_regions(frame)

            # Graphics detection (high contrast regions with sharp edges)
            graphics = self._detect_graphics(frame)

            # Count overlay elements
            overlay_count = (1 if text_detected else 0) + (1 if graphics else 0)

            return {
                'text_detected': text_detected,
                'text_coverage_percentage': float(coverage),
                'graphics_present': graphics,
                'overlay_count': overlay_count
            }

        except Exception as e:
            logger.error(f"Error in overlay analysis: {e}")
            return {
                'text_detected': False,
                'text_coverage_percentage': 0.0,
                'graphics_present': False,
                'overlay_count': 0
            }

    def _assess_overall_quality(self, frame: np.ndarray) -> Dict:
        """Assess overall production quality"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Resolution quality
            h, w = frame.shape[:2]
            resolution_score = min((h * w) / (1920 * 1080), 1.0)

            # Sharpness
            sharpness = self._calculate_sharpness(gray)

            # Brightness balance
            brightness_score = self._assess_brightness_balance(gray)

            # Overall quality score
            quality_score = (
                resolution_score * 0.3 +
                sharpness * 0.4 +
                brightness_score * 0.3
            )

            return {
                'resolution_score': float(resolution_score),
                'sharpness_score': float(sharpness),
                'brightness_score': float(brightness_score),
                'overall_quality_score': float(quality_score)
            }

        except Exception as e:
            logger.error(f"Error in quality assessment: {e}")
            return {
                'resolution_score': 0.5,
                'sharpness_score': 0.5,
                'brightness_score': 0.5,
                'overall_quality_score': 0.5
            }

    # ==================== Helper Methods ====================

    def _is_sepia(self, frame: np.ndarray) -> bool:
        """Check if frame has sepia tone"""
        avg_color = cv2.mean(frame)[:3]
        b, g, r = avg_color

        # Sepia has brownish tint: R > G > B
        return r > g > b and (r - b) > 30 and (g - b) > 15

    def _get_dominant_colors(self, frame: np.ndarray, n_colors: int = 5) -> List[str]:
        """Extract dominant colors as hex codes"""
        try:
            # Reshape and sample pixels
            pixels = frame.reshape(-1, 3)
            pixels = pixels[::100]  # Sample every 100th pixel for speed

            # Use quantization instead of KMeans for speed
            from sklearn.cluster import MiniBatchKMeans
            kmeans = MiniBatchKMeans(n_clusters=n_colors, random_state=42, batch_size=1000)
            kmeans.fit(pixels)

            colors = kmeans.cluster_centers_.astype(int)

            # Convert BGR to hex
            hex_colors = []
            for color in colors:
                b, g, r = color
                hex_colors.append(f"#{r:02x}{g:02x}{b:02x}")

            return hex_colors[:n_colors]

        except Exception as e:
            logger.warning(f"Error extracting dominant colors: {e}")
            return ["#808080"]  # Gray fallback

    def _calculate_contrast_ratio(self, gray: np.ndarray) -> float:
        """Calculate contrast ratio"""
        min_val = np.percentile(gray, 5)
        max_val = np.percentile(gray, 95)

        if min_val == 0:
            min_val = 1

        contrast_ratio = max_val / min_val
        return min(contrast_ratio / 255.0 * 5, 5.0)  # Normalize to 0-5 range

    def _detect_vignette(self, gray: np.ndarray) -> Tuple[bool, float]:
        """Detect vignette effect"""
        h, w = gray.shape

        # Compare center to edges
        center = gray[h//4:3*h//4, w//4:3*w//4]
        edge_top = gray[0:h//8, :]
        edge_bottom = gray[-h//8:, :]
        edge_left = gray[:, 0:w//8]
        edge_right = gray[:, -w//8:]

        center_brightness = np.mean(center)
        edge_brightness = np.mean([
            np.mean(edge_top),
            np.mean(edge_bottom),
            np.mean(edge_left),
            np.mean(edge_right)
        ])

        vignette_strength = (center_brightness - edge_brightness) / 255.0
        vignette_detected = vignette_strength > 0.15

        return vignette_detected, max(0.0, vignette_strength)

    def _analyze_color_temperature(self, frame: np.ndarray) -> Tuple[str, str]:
        """Analyze color temperature and palette"""
        avg_b, avg_g, avg_r = cv2.mean(frame)[:3]

        # Determine temperature
        if avg_r > avg_b + 20:
            temp = 'warm'
        elif avg_b > avg_r + 20:
            temp = 'cool'
        else:
            temp = 'neutral'

        # Detect teal & orange (cinematic look)
        if self._is_teal_orange(frame):
            palette = 'teal_orange'
        elif temp == 'warm':
            palette = 'warm'
        elif temp == 'cool':
            palette = 'cool'
        else:
            palette = 'neutral'

        return temp, palette

    def _is_teal_orange(self, frame: np.ndarray) -> bool:
        """Detect teal & orange color grading"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        hue = hsv[:, :, 1]

        # Teal: 80-100° in OpenCV (160-200 in 0-180 scale)
        # Orange: 10-30° in OpenCV (5-15 in 0-180 scale)
        teal_mask = cv2.inRange(hsv, (80, 50, 50), (100, 255, 255))
        orange_mask = cv2.inRange(hsv, (5, 50, 50), (15, 255, 255))

        teal_percentage = np.sum(teal_mask > 0) / teal_mask.size
        orange_percentage = np.sum(orange_mask > 0) / orange_mask.size

        return teal_percentage > 0.1 and orange_percentage > 0.1

    def _detect_film_grain(self, gray: np.ndarray) -> Tuple[bool, float]:
        """Detect film grain / noise texture"""
        # Calculate high-frequency noise
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        noise_variance = laplacian.var()

        # Normalize (typical grain variance: 100-1000)
        grain_intensity = min(noise_variance / 1000.0, 1.0)
        grain_present = noise_variance > 100

        return grain_present, grain_intensity

    def _detect_blur(self, gray: np.ndarray) -> float:
        """Detect blur level using Laplacian variance"""
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Lower variance = more blur
        # Normalize: <100 = very blurry, >500 = sharp
        blur_score = 1.0 - min(laplacian_var / 500.0, 1.0)
        return blur_score

    def _detect_chromatic_aberration(self, frame: np.ndarray) -> bool:
        """Detect chromatic aberration (color fringing)"""
        # Split channels
        b, g, r = cv2.split(frame)

        # Check for channel misalignment at edges
        edges_b = cv2.Canny(b, 100, 200)
        edges_r = cv2.Canny(r, 100, 200)

        # XOR to find differences
        diff = cv2.bitwise_xor(edges_b, edges_r)
        aberration_percentage = np.sum(diff > 0) / diff.size

        return aberration_percentage > 0.05

    def _calculate_sharpness(self, gray: np.ndarray) -> float:
        """Calculate image sharpness"""
        laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()

        # Normalize to 0-1 (500+ is sharp)
        sharpness = min(laplacian_var / 500.0, 1.0)
        return sharpness

    def _detect_camera_shake(self, frame: np.ndarray, prev_frame: np.ndarray) -> float:
        """Detect camera shake level"""
        try:
            # Convert to grayscale
            gray1 = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
            gray2 = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Calculate optical flow
            flow = cv2.calcOpticalFlowFarneback(
                gray1, gray2, None, 0.5, 3, 15, 3, 5, 1.2, 0
            )

            # Calculate average motion magnitude
            magnitude = np.sqrt(flow[..., 0]**2 + flow[..., 1]**2)
            avg_motion = np.mean(magnitude)

            # Normalize (0-10 pixels is typical, >10 is shake)
            shake_level = min(avg_motion / 10.0, 1.0)
            return shake_level

        except Exception as e:
            logger.warning(f"Error detecting camera shake: {e}")
            return 0.0

    def _detect_motion_blur(self, frame: np.ndarray) -> bool:
        """Detect motion blur"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Motion blur creates directional blur
        # Use edge detection in different directions
        edges_h = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=3)
        edges_v = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=3)

        h_strength = np.mean(np.abs(edges_h))
        v_strength = np.mean(np.abs(edges_v))

        # If one direction significantly weaker = directional blur
        ratio = min(h_strength, v_strength) / max(h_strength, v_strength, 1)

        return ratio < 0.5

    def _calculate_noise_level(self, gray: np.ndarray) -> float:
        """Calculate digital noise level"""
        # Use difference from median-filtered image
        median = cv2.medianBlur(gray, 5)
        noise = cv2.absdiff(gray, median)

        noise_level = np.mean(noise) / 255.0
        return min(noise_level * 10, 1.0)  # Amplify and normalize

    def _detect_lens_distortion(self, gray: np.ndarray) -> float:
        """Detect lens distortion (barrel/pincushion)"""
        # Detect straight lines and check for curvature
        edges = cv2.Canny(gray, 50, 150)
        lines = cv2.HoughLinesP(edges, 1, np.pi/180, 100, minLineLength=100, maxLineGap=10)

        if lines is None or len(lines) < 5:
            return 0.0

        # Simplified: assume minimal distortion for now
        # Full implementation would analyze line curvature
        return 0.0

    def _detect_compression_artifacts(self, frame: np.ndarray) -> bool:
        """Detect compression artifacts (blocking)"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Look for 8x8 block patterns (JPEG/H.264)
        # Calculate gradient variance in 8x8 blocks
        h, w = gray.shape
        block_size = 8

        variances = []
        for i in range(0, h - block_size, block_size):
            for j in range(0, w - block_size, block_size):
                block = gray[i:i+block_size, j:j+block_size]
                variances.append(np.var(block))

        # High variance in block boundaries = artifacts
        variance_range = np.max(variances) - np.min(variances)
        return variance_range > 1000

    def _detect_text_regions(self, frame: np.ndarray) -> Tuple[bool, float]:
        """Detect text overlay regions"""
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Use MSER (Maximally Stable Extremal Regions) for text
        mser = cv2.MSER_create()
        regions, _ = mser.detectRegions(gray)

        # Text regions have specific characteristics
        text_regions = 0
        total_area = gray.shape[0] * gray.shape[1]
        text_area = 0

        for region in regions:
            if len(region) > 10:  # Filter tiny regions
                text_regions += 1
                text_area += len(region)

        text_detected = text_regions > 5
        coverage = (text_area / total_area) * 100

        return text_detected, min(coverage, 100.0)

    def _detect_graphics(self, frame: np.ndarray) -> bool:
        """Detect graphics overlays"""
        # Graphics typically have sharp edges and solid colors
        edges = cv2.Canny(frame, 100, 200)
        edge_density = np.sum(edges > 0) / edges.size

        # High edge density with low texture = graphics
        return edge_density > 0.15

    def _assess_brightness_balance(self, gray: np.ndarray) -> float:
        """Assess brightness distribution balance"""
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist / hist.sum()  # Normalize

        # Good balance: histogram spread across range
        # Poor balance: clustered at one end
        weighted_sum = sum(i * hist[i][0] for i in range(256))
        ideal_mean = 127

        # Calculate how close to ideal distribution
        deviation = abs(weighted_sum - ideal_mean) / 127
        balance_score = 1.0 - deviation

        return max(0.0, balance_score)

    def _get_default_analysis(self) -> Dict:
        """Return default analysis when errors occur"""
        return {
            'color_grading': self._get_default_color_grading(),
            'filters': self._get_default_filters(),
            'motion_effects': {
                'camera_shake_level': 0.0,
                'motion_blur_present': False,
                'handheld_style': False,
                'stability_score': 1.0
            },
            'distortion': {
                'digital_noise': 0.0,
                'lens_distortion': 0.0,
                'compression_artifacts': False,
                'artifact_severity': 0.0
            },
            'overlays': {
                'text_detected': False,
                'text_coverage_percentage': 0.0,
                'graphics_present': False,
                'overlay_count': 0
            },
            'overall_quality': {
                'resolution_score': 0.5,
                'sharpness_score': 0.5,
                'brightness_score': 0.5,
                'overall_quality_score': 0.5
            }
        }

    def _get_default_color_grading(self) -> Dict:
        """Default color grading analysis"""
        return {
            'style': 'natural',
            'dominant_colors': ['#808080'],
            'saturation_level': 0.5,
            'contrast_ratio': 1.0,
            'vignette_detected': False,
            'vignette_strength': 0.0,
            'color_palette': 'neutral',
            'color_temperature': 'neutral'
        }

    def _get_default_filters(self) -> Dict:
        """Default filter analysis"""
        return {
            'film_grain': False,
            'film_grain_intensity': None,
            'lens_blur': None,
            'chromatic_aberration': False,
            'sharpening': 0.5,
            'overall_sharpness': 0.5
        }


def aggregate_effects_analysis(frame_analyses: List[Dict]) -> Dict:
    """
    Aggregate effects analysis across multiple frames.

    Args:
        frame_analyses: List of per-frame analysis dictionaries

    Returns:
        Aggregated effects analysis
    """
    if not frame_analyses:
        return VisualEffectsDetector()._get_default_analysis()

    # Aggregate color grading
    styles = [fa['color_grading']['style'] for fa in frame_analyses]
    most_common_style = max(set(styles), key=styles.count)

    avg_saturation = np.mean([fa['color_grading']['saturation_level'] for fa in frame_analyses])
    avg_contrast = np.mean([fa['color_grading']['contrast_ratio'] for fa in frame_analyses])

    vignette_count = sum(1 for fa in frame_analyses if fa['color_grading']['vignette_detected'])
    vignette_detected = vignette_count > len(frame_analyses) / 2

    # Aggregate filters
    film_grain_count = sum(1 for fa in frame_analyses if fa['filters']['film_grain'])
    film_grain = film_grain_count > len(frame_analyses) / 2

    # Aggregate motion
    avg_shake = np.mean([fa['motion_effects']['camera_shake_level'] for fa in frame_analyses])
    handheld_count = sum(1 for fa in frame_analyses if fa['motion_effects']['handheld_style'])
    handheld = handheld_count > len(frame_analyses) / 2

    # Aggregate overlays
    text_count = sum(1 for fa in frame_analyses if fa['overlays']['text_detected'])
    text_detected = text_count > len(frame_analyses) / 3  # Present in at least 1/3 of frames

    return {
        'color_grading_style': most_common_style,
        'avg_saturation': float(avg_saturation),
        'avg_contrast': float(avg_contrast),
        'vignette_used': vignette_detected,
        'film_grain_used': film_grain,
        'avg_camera_shake': float(avg_shake),
        'handheld_style': handheld,
        'text_overlays_present': text_detected,
        'frame_count': len(frame_analyses)
    }
