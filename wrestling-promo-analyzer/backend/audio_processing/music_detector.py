"""
Background Music Detection and Analysis Module

Detects and analyzes background music in wrestling promo audio, evaluating
appropriateness, mixing quality, and effectiveness.
"""

import numpy as np
import logging
from typing import Dict, Optional, Tuple, List
from dataclasses import dataclass

logger = logging.getLogger(__name__)

# Try to import audio libraries (graceful degradation if not available)
try:
    import librosa
    LIBROSA_AVAILABLE = True
except ImportError:
    logger.warning("librosa not available - music analysis will be limited")
    LIBROSA_AVAILABLE = False

try:
    from pydub import AudioSegment
    from pydub.utils import db_to_float
    PYDUB_AVAILABLE = True
except ImportError:
    logger.warning("pydub not available - volume analysis will be limited")
    PYDUB_AVAILABLE = False


@dataclass
class MusicDetection:
    """Music presence detection results"""
    music_present: bool
    confidence: float  # 0-1
    harmonic_ratio: float
    detected_tempo: Optional[float]


@dataclass
class MusicCharacteristics:
    """Music characteristics analysis"""
    tempo_bpm: Optional[int]
    tempo_category: str  # 'very_slow', 'slow', 'moderate', 'fast', 'very_fast'
    intensity_level: str  # 'calm', 'moderate', 'energetic', 'intense'
    intensity_score: float  # 0-1
    key_type: str  # 'major', 'minor', 'ambiguous'
    emotional_tone: str  # 'uplifting', 'dark', 'neutral'
    has_dynamic_builds: bool


@dataclass
class MixingQuality:
    """Audio mixing quality assessment"""
    music_level_db: float
    speech_level_db: float
    balance_ratio: float
    balance_quality: str  # 'excellent', 'good', 'fair', 'poor'
    ducking_detected: bool
    music_too_loud: bool
    music_too_quiet: bool
    clipping_detected: bool


class BackgroundMusicDetector:
    """
    Detects and analyzes background music in audio files.
    """

    def __init__(self):
        self.sample_rate = 22050  # Standard for music analysis

    def analyze_audio(self, audio_file: str, character_type: str = None,
                     promo_type: str = None) -> Dict:
        """
        Analyze audio file for background music.

        Args:
            audio_file: Path to audio file
            character_type: Optional character type (heel/face/tweener)
            promo_type: Optional promo type (challenge/revenge/etc)

        Returns:
            Dictionary containing all music analysis
        """
        try:
            results = {
                'music_detected': False,
                'music_present_percentage': 0,
                'music_characteristics': None,
                'mixing_quality': None,
                'appropriateness': None
            }

            if not LIBROSA_AVAILABLE:
                logger.warning("Music analysis requires librosa")
                return results

            # Detect music presence
            detection = self._detect_music_presence(audio_file)
            results['music_detected'] = detection.music_present
            results['music_detection'] = {
                'confidence': float(detection.confidence),
                'harmonic_ratio': float(detection.harmonic_ratio),
                'detected_tempo': detection.detected_tempo
            }

            if not detection.music_present:
                return results

            # Analyze music characteristics
            results['music_present_percentage'] = 100  # Simplified
            results['music_characteristics'] = self._analyze_characteristics(audio_file)

            # Analyze mixing quality
            results['mixing_quality'] = self._analyze_mixing(audio_file)

            # Assess appropriateness if character/promo type provided
            if character_type or promo_type:
                results['appropriateness'] = self._assess_appropriateness(
                    character_type,
                    promo_type,
                    results['music_characteristics']
                )

            return results

        except Exception as e:
            logger.error(f"Error analyzing audio: {e}")
            return self._get_default_analysis()

    def _detect_music_presence(self, audio_file: str) -> MusicDetection:
        """Detect if background music is present"""
        try:
            # Load audio
            y, sr = librosa.load(audio_file, sr=self.sample_rate, duration=30)

            # Separate harmonic and percussive components
            harmonic, percussive = librosa.effects.hpss(y)

            # Calculate harmonic ratio (music has more harmonic content)
            harmonic_energy = np.mean(np.abs(harmonic))
            total_energy = np.mean(np.abs(y)) + 1e-6
            harmonic_ratio = harmonic_energy / total_energy

            # Detect tempo and beats
            tempo = None
            try:
                tempo_val, beats = librosa.beat.beat_track(y=y, sr=sr)
                tempo = float(tempo_val)
            except Exception as e:
                logger.debug(f"Tempo detection failed: {e}")
                tempo = None

            # Calculate spectral features
            spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
            avg_centroid = np.mean(spectral_centroid)

            # Determine music confidence
            confidence = 0.0

            # High harmonic content suggests music
            if harmonic_ratio > 0.3:
                confidence += 0.4
            elif harmonic_ratio > 0.2:
                confidence += 0.2

            # Consistent tempo suggests music
            if tempo and tempo > 60 and len(beats) > 10:
                confidence += 0.3

            # Rich frequency spectrum suggests music
            if avg_centroid > 2000:
                confidence += 0.3
            elif avg_centroid > 1500:
                confidence += 0.2

            music_present = confidence > 0.5

            return MusicDetection(
                music_present=music_present,
                confidence=confidence,
                harmonic_ratio=harmonic_ratio,
                detected_tempo=tempo if tempo and tempo > 60 else None
            )

        except Exception as e:
            logger.error(f"Error detecting music presence: {e}")
            return MusicDetection(
                music_present=False,
                confidence=0.0,
                harmonic_ratio=0.0,
                detected_tempo=None
            )

    def _analyze_characteristics(self, audio_file: str) -> Dict:
        """Analyze music tempo, intensity, and mood"""
        try:
            # Load audio
            y, sr = librosa.load(audio_file, sr=self.sample_rate)

            # Extract harmonic component (music)
            harmonic, _ = librosa.effects.hpss(y)

            # Tempo detection
            tempo_bpm = None
            tempo_category = 'unknown'
            try:
                tempo_val, beats = librosa.beat.beat_track(y=harmonic, sr=sr)
                tempo_bpm = int(tempo_val)

                # Categorize tempo
                if tempo_bpm < 60:
                    tempo_category = 'very_slow'
                elif tempo_bpm < 90:
                    tempo_category = 'slow'
                elif tempo_bpm < 120:
                    tempo_category = 'moderate'
                elif tempo_bpm < 150:
                    tempo_category = 'fast'
                else:
                    tempo_category = 'very_fast'
            except Exception as e:
                logger.debug(f"Tempo analysis failed: {e}")

            # Intensity/Energy analysis
            intensity_data = self._analyze_intensity(harmonic, sr)

            # Key detection (major/minor)
            key_data = self._detect_key(harmonic, sr)

            return {
                'tempo_bpm': tempo_bpm,
                'tempo_category': tempo_category,
                'intensity_level': intensity_data['intensity_level'],
                'intensity_score': intensity_data['intensity_score'],
                'key_type': key_data['key_type'],
                'emotional_tone': key_data['emotional_tone'],
                'has_dynamic_builds': intensity_data['has_builds']
            }

        except Exception as e:
            logger.error(f"Error analyzing characteristics: {e}")
            return {
                'tempo_bpm': None,
                'tempo_category': 'unknown',
                'intensity_level': 'moderate',
                'intensity_score': 0.5,
                'key_type': 'ambiguous',
                'emotional_tone': 'neutral',
                'has_dynamic_builds': False
            }

    def _analyze_intensity(self, audio: np.ndarray, sr: int) -> Dict:
        """Analyze music intensity and energy"""
        try:
            # RMS energy (loudness over time)
            rms = librosa.feature.rms(y=audio)[0]

            # Spectral flux (change in frequency - indicates intensity)
            spectral_flux = librosa.onset.onset_strength(y=audio, sr=sr)

            # Zero crossing rate (high = more aggressive)
            zcr = librosa.feature.zero_crossing_rate(audio)[0]

            # Calculate intensity score (0-1)
            max_rms = np.max(rms)
            energy_score = np.mean(rms) / (max_rms + 1e-6) if max_rms > 0 else 0

            max_flux = np.max(spectral_flux)
            flux_score = np.mean(spectral_flux) / (max_flux + 1e-6) if max_flux > 0 else 0

            zcr_score = np.mean(zcr)

            intensity = float((energy_score + flux_score + zcr_score) / 3)

            # Classify intensity
            if intensity < 0.3:
                intensity_level = 'calm'
            elif intensity < 0.5:
                intensity_level = 'moderate'
            elif intensity < 0.7:
                intensity_level = 'energetic'
            else:
                intensity_level = 'intense'

            # Check for dynamic builds
            mean_rms = np.mean(rms)
            has_builds = max_rms > mean_rms * 2

            return {
                'intensity_score': intensity,
                'intensity_level': intensity_level,
                'has_builds': has_builds
            }

        except Exception as e:
            logger.error(f"Error analyzing intensity: {e}")
            return {
                'intensity_score': 0.5,
                'intensity_level': 'moderate',
                'has_builds': False
            }

    def _detect_key(self, audio: np.ndarray, sr: int) -> Dict:
        """Detect if music is in major or minor key"""
        try:
            # Chromagram (pitch classes)
            chroma = librosa.feature.chroma_cqt(y=audio, sr=sr)

            # Average over time
            chroma_mean = np.mean(chroma, axis=1)

            # Simplified major/minor detection
            # Major: stronger presence in 0, 4, 7 (major triad)
            # Minor: stronger presence in 0, 3, 7 (minor triad)

            major_strength = float(chroma_mean[0] + chroma_mean[4] + chroma_mean[7])
            minor_strength = float(chroma_mean[0] + chroma_mean[3] + chroma_mean[7])

            if major_strength > minor_strength * 1.15:
                key_type = 'major'
                emotional_tone = 'uplifting'
            elif minor_strength > major_strength * 1.15:
                key_type = 'minor'
                emotional_tone = 'dark'
            else:
                key_type = 'ambiguous'
                emotional_tone = 'neutral'

            return {
                'key_type': key_type,
                'emotional_tone': emotional_tone
            }

        except Exception as e:
            logger.error(f"Error detecting key: {e}")
            return {
                'key_type': 'ambiguous',
                'emotional_tone': 'neutral'
            }

    def _analyze_mixing(self, audio_file: str) -> Dict:
        """Analyze mixing quality and volume levels"""
        try:
            # Load audio
            y, sr = librosa.load(audio_file, sr=self.sample_rate)

            # Separate harmonic (music) and percussive components
            # Note: This is a simplification - proper separation would use Spleeter
            harmonic, _ = librosa.effects.hpss(y)

            # Calculate RMS levels (approximation)
            music_rms = np.sqrt(np.mean(harmonic**2))
            overall_rms = np.sqrt(np.mean(y**2))

            # Convert to dB (approximate)
            music_db = float(20 * np.log10(music_rms + 1e-6))
            overall_db = float(20 * np.log10(overall_rms + 1e-6))

            # Estimate balance ratio
            # In proper implementation, would use separated vocals/music tracks
            balance_ratio = music_rms / (overall_rms + 1e-6)

            # Assess balance quality
            # Ideal: music quieter than speech (ratio 0.3-0.7)
            if 0.3 <= balance_ratio <= 0.7:
                balance_quality = 'excellent'
            elif 0.2 <= balance_ratio <= 0.9:
                balance_quality = 'good'
            elif 0.1 <= balance_ratio <= 1.2:
                balance_quality = 'fair'
            else:
                balance_quality = 'poor'

            # Simple ducking detection (look for dynamic range variation)
            rms_time = librosa.feature.rms(y=y)[0]
            dynamic_range = np.max(rms_time) / (np.mean(rms_time) + 1e-6)
            ducking_detected = dynamic_range > 2.0

            # Check for clipping
            clipping_detected = np.max(np.abs(y)) > 0.99

            return {
                'music_level_db': music_db,
                'speech_level_db': overall_db,
                'balance_ratio': float(balance_ratio),
                'balance_quality': balance_quality,
                'ducking_detected': ducking_detected,
                'music_too_loud': balance_ratio > 0.9,
                'music_too_quiet': balance_ratio < 0.2,
                'clipping_detected': clipping_detected
            }

        except Exception as e:
            logger.error(f"Error analyzing mixing: {e}")
            return {
                'music_level_db': -12.0,
                'speech_level_db': -6.0,
                'balance_ratio': 0.5,
                'balance_quality': 'good',
                'ducking_detected': False,
                'music_too_loud': False,
                'music_too_quiet': False,
                'clipping_detected': False
            }

    def _assess_appropriateness(self, character_type: Optional[str],
                               promo_type: Optional[str],
                               music_chars: Dict) -> Dict:
        """Assess if music is appropriate for character and promo type"""
        try:
            fits_character = None
            fits_promo = None

            # Character-based appropriateness
            if character_type:
                character_lower = character_type.lower()

                if character_lower == 'heel':
                    # Heel characters: prefer intense, dark music
                    intensity_match = music_chars.get('intensity_level') in ['energetic', 'intense']
                    key_match = music_chars.get('key_type') in ['minor', 'ambiguous']
                    fits_character = intensity_match and key_match

                elif character_lower == 'face':
                    # Face characters: prefer uplifting, energetic music
                    intensity_match = music_chars.get('intensity_level') in ['moderate', 'energetic']
                    key_match = music_chars.get('key_type') in ['major', 'ambiguous']
                    fits_character = intensity_match or key_match

                elif character_lower == 'tweener':
                    # Tweener: versatile, but avoid extremes
                    intensity = music_chars.get('intensity_level')
                    fits_character = intensity not in ['calm', 'very_slow']

            # Promo type-based appropriateness
            if promo_type:
                promo_lower = promo_type.lower()
                intensity = music_chars.get('intensity_level')
                tempo = music_chars.get('tempo_category')

                if 'challenge' in promo_lower or 'revenge' in promo_lower:
                    # High energy promos
                    fits_promo = intensity in ['energetic', 'intense']
                elif 'celebration' in promo_lower:
                    # Uplifting promos
                    fits_promo = music_chars.get('emotional_tone') == 'uplifting'
                elif 'debut' in promo_lower:
                    # Memorable, attention-grabbing
                    fits_promo = intensity != 'calm'
                else:
                    fits_promo = True  # Neutral assessment

            return {
                'fits_character': fits_character,
                'fits_promo_type': fits_promo,
                'character_type': character_type,
                'promo_type': promo_type
            }

        except Exception as e:
            logger.error(f"Error assessing appropriateness: {e}")
            return {
                'fits_character': None,
                'fits_promo_type': None,
                'character_type': character_type,
                'promo_type': promo_type
            }

    def _get_default_analysis(self) -> Dict:
        """Return default analysis when errors occur"""
        return {
            'music_detected': False,
            'music_present_percentage': 0,
            'music_detection': {
                'confidence': 0.0,
                'harmonic_ratio': 0.0,
                'detected_tempo': None
            },
            'music_characteristics': None,
            'mixing_quality': None,
            'appropriateness': None
        }


def aggregate_music_analysis(analyses: List[Dict]) -> Dict:
    """
    Aggregate music analysis across multiple segments.

    Args:
        analyses: List of music analysis dictionaries

    Returns:
        Aggregated music analysis
    """
    if not analyses:
        return {}

    # Check if music is consistently present
    music_present_count = sum(1 for a in analyses if a.get('music_detected'))
    music_present_percentage = (music_present_count / len(analyses)) * 100

    # If music is rarely present, return negative result
    if music_present_percentage < 50:
        return {
            'music_detected': False,
            'music_present_percentage': music_present_percentage
        }

    # Aggregate characteristics (from analyses where music was detected)
    music_analyses = [a for a in analyses if a.get('music_detected')]

    if not music_analyses:
        return {
            'music_detected': False,
            'music_present_percentage': 0
        }

    # Get most common characteristics
    tempos = [a['music_characteristics']['tempo_bpm']
             for a in music_analyses
             if a.get('music_characteristics') and a['music_characteristics'].get('tempo_bpm')]

    avg_tempo = int(np.mean(tempos)) if tempos else None

    return {
        'music_detected': True,
        'music_present_percentage': music_present_percentage,
        'avg_tempo_bpm': avg_tempo,
        'segment_count': len(analyses),
        'music_segment_count': len(music_analyses)
    }
