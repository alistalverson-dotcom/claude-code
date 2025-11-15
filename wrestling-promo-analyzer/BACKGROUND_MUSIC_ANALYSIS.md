# Background Music Analysis - Design Document

## 🎵 Overview

This document outlines the background music detection and analysis system for wrestling promo videos. The system identifies music presence, analyzes its appropriateness, and evaluates how effectively it enhances the performance.

---

## 🎯 Goals

1. **Detect** presence and characteristics of background music
2. **Separate** music from speech/dialogue
3. **Analyze** music appropriateness for character type and promo tone
4. **Evaluate** volume levels and mixing quality
5. **Provide feedback** on music selection and usage
6. **Score** music effectiveness and production quality

---

## 📊 Music Analysis Categories

### **1. Music Detection**

| Aspect | Description | Detection Method |
|--------|-------------|------------------|
| **Presence** | Is background music present? | Audio spectral analysis |
| **Duration** | What percentage of promo has music? | Continuous presence detection |
| **Start/End Points** | When does music begin/end? | Timestamp detection |
| **Consistency** | Is music continuous or intermittent? | Temporal analysis |

### **2. Music Characteristics**

| Aspect | Description | Analysis Method |
|--------|-------------|-----------------|
| **Tempo (BPM)** | Speed of the music | Beat detection |
| **Intensity** | Energy level (calm to intense) | Spectral flux, RMS energy |
| **Genre/Style** | Type of music (hip-hop, rock, cinematic, etc.) | Spectral features + AI |
| **Mood** | Emotional tone (aggressive, heroic, mysterious, etc.) | AI audio analysis |
| **Key** | Musical key (major/minor) | Pitch detection |

### **3. Mixing & Production**

| Aspect | Description | Analysis Method |
|--------|-------------|-----------------|
| **Volume Level** | Music loudness vs speech | RMS level comparison |
| **Ducking** | Does music lower during speech? | Dynamic range analysis |
| **Balance** | Music/speech balance quality | Spectral balance |
| **Audio Quality** | Professional vs amateur mix | Frequency analysis |
| **Clipping/Distortion** | Audio artifacts present? | Peak analysis |

### **4. Appropriateness for Character**

| Character Type | Effective Music Styles | Avoid |
|----------------|------------------------|-------|
| **Heel (Villain)** | Heavy rock, industrial, dark hip-hop, ominous strings, aggressive trap | Uplifting pop, cheerful music, heroic orchestral |
| **Face (Hero)** | Heroic orchestral, uplifting rock, motivational hip-hop, energetic pop | Dark/ominous tones, overly aggressive industrial |
| **Tweener (Anti-Hero)** | Edgy rock, cinematic hybrid, modern hip-hop, atmospheric electronic | Overly cheerful OR overly dark |

### **5. Promo Type Alignment**

| Promo Type | Effective Music | Characteristics |
|------------|----------------|-----------------|
| **Challenge** | Aggressive, building intensity, competitive energy | Rising tempo, strong beat |
| **Revenge** | Dark, ominous, intense, payback energy | Minor key, heavy bass |
| **Celebration** | Triumphant, uplifting, victorious | Major key, energetic |
| **Debut** | Mysterious, attention-grabbing, signature sound | Memorable hook, unique |
| **Intimidation** | Heavy, powerful, threatening | Low frequencies, intense |
| **Emotional/Storyline** | Cinematic, dramatic, dynamic range | Orchestral elements, builds |

---

## 🔧 Technical Implementation

### **Backend: Music Detection Module**

**File:** `backend/audio_processing/music_detector.py`

```python
class BackgroundMusicDetector:
    """Detects and analyzes background music in audio"""

    def analyze_audio(self, audio_file) -> MusicAnalysis:
        """Analyze audio for background music"""
        return {
            'music_detection': self.detect_music_presence(audio_file),
            'music_characteristics': self.analyze_characteristics(audio_file),
            'mixing_quality': self.analyze_mixing(audio_file),
            'speech_music_separation': self.separate_sources(audio_file),
            'appropriateness': self.assess_appropriateness(audio_file)
        }

    def detect_music_presence(self, audio_file) -> dict:
        """Detect if background music is present"""
        # Analyze frequency spectrum
        # Look for sustained harmonic content
        # Detect rhythmic patterns
        # Separate from speech frequencies

    def analyze_characteristics(self, audio_file) -> dict:
        """Analyze music tempo, intensity, mood"""
        # Beat detection (tempo/BPM)
        # Energy level analysis
        # Spectral features for genre/mood
        # Key detection (major/minor)

    def analyze_mixing(self, audio_file) -> dict:
        """Analyze mixing quality and levels"""
        # Volume level analysis
        # Music vs speech balance
        # Dynamic range analysis (ducking detection)
        # Clipping/distortion detection

    def separate_sources(self, audio_file) -> dict:
        """Separate music from speech (source separation)"""
        # Use Spleeter or Demucs for separation
        # Analyze music-only track
        # Analyze speech-only track
        # Calculate separation quality

    def assess_appropriateness(self, character_type, promo_type, music_features) -> dict:
        """Assess if music fits character and promo type"""
        # Match music characteristics to character type
        # Evaluate mood alignment
        # Check tempo appropriateness
        # Score overall fit
```

### **Audio Processing Pipeline**

**Libraries:**
- **Librosa**: Audio analysis, tempo detection, spectral analysis
- **Spleeter** or **Demucs**: AI-powered source separation (music/vocals)
- **PyDub**: Audio manipulation, level detection
- **Essentia**: Music information retrieval

**Processing Steps:**

1. **Load Audio** → Read extracted audio file from video
2. **Music Detection** → Identify presence of background music
3. **Source Separation** → Separate music from speech (if music present)
4. **Feature Extraction** → Analyze tempo, intensity, mood, key
5. **Mixing Analysis** → Check volume levels, ducking, balance
6. **AI Evaluation** → Claude analyzes appropriateness for character
7. **Scoring** → Generate music effectiveness score

---

## 🎨 Music Detection Algorithms

### **1. Music Presence Detection**

```python
def detect_music_presence(audio_file):
    """Detect if background music is present"""
    import librosa
    import numpy as np

    # Load audio
    y, sr = librosa.load(audio_file, sr=22050)

    # Extract spectral features
    spectral_centroid = librosa.feature.spectral_centroid(y=y, sr=sr)
    spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)

    # Detect harmonic content (music has more harmonics)
    harmonic, percussive = librosa.effects.hpss(y)
    harmonic_ratio = np.mean(np.abs(harmonic)) / (np.mean(np.abs(y)) + 1e-6)

    # Detect rhythmic patterns (music has consistent beat)
    tempo, beats = librosa.beat.beat_track(y=y, sr=sr)

    # Music typically present if:
    # - High harmonic content (>0.3)
    # - Consistent tempo detected
    # - Rich frequency spectrum

    music_confidence = 0.0

    if harmonic_ratio > 0.3:
        music_confidence += 0.4
    if tempo > 60 and len(beats) > 10:
        music_confidence += 0.3
    if np.mean(spectral_centroid) > 2000:
        music_confidence += 0.3

    music_present = music_confidence > 0.5

    return {
        'music_present': music_present,
        'confidence': music_confidence,
        'harmonic_ratio': harmonic_ratio,
        'detected_tempo': tempo if tempo > 60 else None
    }
```

### **2. Tempo (BPM) Detection**

```python
def detect_tempo(audio_file):
    """Detect tempo/BPM of background music"""
    import librosa

    y, sr = librosa.load(audio_file, sr=22050)

    # Extract music component (if separated)
    harmonic, _ = librosa.effects.hpss(y)

    # Detect tempo
    tempo, beats = librosa.beat.beat_track(y=harmonic, sr=sr)

    # Classify tempo
    if tempo < 60:
        tempo_category = 'very_slow'
    elif tempo < 90:
        tempo_category = 'slow'
    elif tempo < 120:
        tempo_category = 'moderate'
    elif tempo < 150:
        tempo_category = 'fast'
    else:
        tempo_category = 'very_fast'

    return {
        'bpm': int(tempo),
        'tempo_category': tempo_category,
        'beat_strength': np.mean(librosa.onset.onset_strength(y=harmonic, sr=sr))
    }
```

### **3. Intensity/Energy Analysis**

```python
def analyze_intensity(audio_file):
    """Analyze music intensity and energy"""
    import librosa
    import numpy as np

    y, sr = librosa.load(audio_file, sr=22050)
    harmonic, _ = librosa.effects.hpss(y)

    # RMS energy (loudness over time)
    rms = librosa.feature.rms(y=harmonic)[0]

    # Spectral flux (change in frequency content - indicates intensity)
    spectral_flux = librosa.onset.onset_strength(y=harmonic, sr=sr)

    # Zero crossing rate (high = more intense/aggressive)
    zcr = librosa.feature.zero_crossing_rate(harmonic)[0]

    # Calculate intensity score (0-1)
    energy_score = np.mean(rms) / (np.max(rms) + 1e-6)
    flux_score = np.mean(spectral_flux) / (np.max(spectral_flux) + 1e-6)
    zcr_score = np.mean(zcr)

    intensity = (energy_score + flux_score + zcr_score) / 3

    # Classify intensity
    if intensity < 0.3:
        intensity_level = 'calm'
    elif intensity < 0.5:
        intensity_level = 'moderate'
    elif intensity < 0.7:
        intensity_level = 'energetic'
    else:
        intensity_level = 'intense'

    return {
        'intensity_score': intensity,
        'intensity_level': intensity_level,
        'energy_profile': rms.tolist(),
        'has_builds': np.max(rms) > np.mean(rms) * 2  # Dynamic builds
    }
```

### **4. Music/Speech Volume Balance**

```python
def analyze_volume_balance(audio_file):
    """Analyze balance between music and speech"""
    # Assumes source separation has been done
    from pydub import AudioSegment

    # Load separated tracks
    music_track = AudioSegment.from_file("music_separated.wav")
    vocals_track = AudioSegment.from_file("vocals_separated.wav")

    # Calculate RMS levels
    music_rms = music_track.rms
    vocals_rms = vocals_track.rms

    # Calculate balance ratio
    if vocals_rms > 0:
        balance_ratio = music_rms / vocals_rms
    else:
        balance_ratio = float('inf')

    # Ideal ratio: 0.3 - 0.7 (music quieter than speech)
    if 0.3 <= balance_ratio <= 0.7:
        balance_quality = 'excellent'
    elif 0.2 <= balance_ratio <= 0.9:
        balance_quality = 'good'
    elif 0.1 <= balance_ratio <= 1.2:
        balance_quality = 'fair'
    else:
        balance_quality = 'poor'

    # Check for ducking (music lowers during speech)
    ducking_detected = detect_ducking(music_track, vocals_track)

    return {
        'music_level_db': music_track.dBFS,
        'speech_level_db': vocals_track.dBFS,
        'balance_ratio': balance_ratio,
        'balance_quality': balance_quality,
        'ducking_detected': ducking_detected,
        'music_too_loud': balance_ratio > 0.9,
        'music_too_quiet': balance_ratio < 0.2
    }
```

### **5. Key Detection (Major/Minor)**

```python
def detect_musical_key(audio_file):
    """Detect if music is in major or minor key"""
    import librosa
    import numpy as np

    y, sr = librosa.load(audio_file, sr=22050)
    harmonic, _ = librosa.effects.hpss(y)

    # Chromagram (pitch classes)
    chroma = librosa.feature.chroma_cqt(y=harmonic, sr=sr)

    # Average chromagram over time
    chroma_mean = np.mean(chroma, axis=1)

    # Major keys have stronger 1st, 3rd (major 3rd), and 5th
    # Minor keys have stronger 1st, 3rd (minor 3rd), and 5th

    # Simplified major/minor detection
    major_thirds = [0, 4, 7]  # C, E, G for C major
    minor_thirds = [0, 3, 7]  # C, Eb, G for C minor

    major_strength = sum(chroma_mean[i] for i in major_thirds)
    minor_strength = sum(chroma_mean[i] for i in minor_thirds)

    if major_strength > minor_strength * 1.1:
        key_type = 'major'
        emotional_tone = 'uplifting'
    elif minor_strength > major_strength * 1.1:
        key_type = 'minor'
        emotional_tone = 'dark'
    else:
        key_type = 'ambiguous'
        emotional_tone = 'neutral'

    return {
        'key_type': key_type,
        'emotional_tone': emotional_tone,
        'major_strength': major_strength,
        'minor_strength': minor_strength
    }
```

---

## 🎤 Enhanced Claude Audio Analysis Prompts

**File:** `backend/prompts/background_music_prompt.txt`

```
BACKGROUND MUSIC ANALYSIS

Analyze the background music in this wrestling promo audio:

AUDIO FEATURES DETECTED:
- Music Present: {music_present}
- Tempo: {bpm} BPM ({tempo_category})
- Intensity: {intensity_level}
- Key: {key_type} ({emotional_tone})
- Music/Speech Balance: {balance_quality}
- Ducking: {ducking_detected}

CHARACTER CONTEXT:
- Character Type: {character_type} (Heel/Face/Tweener)
- Promo Type: {promo_type}

ANALYZE:

1. MUSIC APPROPRIATENESS:
   - Does the music style fit the character type?
   - Is the tempo appropriate for the promo's energy?
   - Does the mood (major/minor key) match the character alignment?
   - Is the intensity level appropriate?

2. MIXING QUALITY:
   - Is the music volume balanced with speech?
   - Does music duck (lower) during important speech moments?
   - Is the music too loud, too quiet, or just right?
   - Any audio quality issues (distortion, clipping)?

3. EFFECTIVENESS:
   - Does the music ENHANCE the promo or DISTRACT from it?
   - Does it amplify the emotional impact?
   - Is the music choice memorable or generic?
   - Does it help establish character identity?

4. CHARACTER-SPECIFIC EVALUATION:
   For HEEL characters:
   - Heavy, aggressive, dark music is effective
   - Minor keys and ominous tones work well
   - Avoid uplifting or cheerful music

   For FACE characters:
   - Heroic, uplifting, energetic music is effective
   - Major keys and motivational tones work well
   - Avoid overly dark or aggressive music

   For TWEENER characters:
   - Edgy, modern, versatile music is effective
   - Balance between aggressive and accessible
   - Avoid extremes (too cheerful or too dark)

5. RECOMMENDATIONS:
   - What's working well with the music choice?
   - What should be changed (tempo, volume, style)?
   - Suggestions for better music selection?
   - Mixing/production recommendations?

PROVIDE ANALYSIS IN THIS FORMAT:

{
  "music_effectiveness": {
    "overall_score": 0-100,
    "fits_character": true|false,
    "fits_promo_type": true|false,
    "enhances_performance": true|false,
    "effectiveness_level": "excellent|good|fair|poor"
  },
  "music_style_assessment": {
    "style_description": "Heavy industrial rock with aggressive energy",
    "tempo_appropriateness": "excellent|good|fair|poor",
    "intensity_match": "excellent|good|fair|poor",
    "mood_alignment": "excellent|good|fair|poor",
    "feedback": "Detailed feedback on music choice..."
  },
  "mixing_assessment": {
    "volume_balance": "excellent|good|fair|poor",
    "ducking_quality": "excellent|good|fair|poor",
    "overall_mix_quality": "excellent|good|fair|poor",
    "issues": ["List any mixing problems"],
    "feedback": "Detailed feedback on mixing..."
  },
  "strengths": [
    "List what's working well with the music"
  ],
  "weaknesses": [
    "List what's not working or could be improved"
  ],
  "recommendations": [
    "Specific, actionable recommendations for music/mixing"
  ],
  "example_music_suggestions": [
    "Suggest specific music styles or examples that would work better"
  ],
  "overall_feedback": "2-3 sentence summary of music effectiveness..."
}
```

---

## 🎨 UI Components

### **1. Music Analysis Card**

**File:** `frontend/src/components/MusicAnalysisCard.tsx`

Visual appearance:
```
┌────────────────────────────────────────────┐
│ 🎵 Background Music Analysis              │
│                                            │
│ Music Effectiveness: 82/100                │
│                                            │
│ ✅ Working Well:                           │
│ • Tempo matches promo intensity           │
│ • Dark minor key fits heel character      │
│ • Professional mixing with ducking        │
│                                            │
│ ⚠️  Could Improve:                         │
│ • Music slightly too loud at 00:45        │
│ • Consider lowering by 2-3 dB             │
│                                            │
│ 💡 Recommendations:                        │
│ • Maintain current music style            │
│ • Add subtle fade-in at start             │
│ • Lower volume during intense moments     │
└────────────────────────────────────────────┘
```

### **2. Music Characteristics Display**

```
┌────────────────────────────────────────────┐
│ 🎼 Music Characteristics                  │
│                                            │
│ Style: Heavy Industrial Rock               │
│ Tempo: 125 BPM (Fast)                      │
│ Intensity: Intense ████████░░ 85%         │
│ Key: Minor (Dark/Ominous)                  │
│ Duration: 100% (Continuous)                │
│                                            │
│ ✓ Fits Heel Character                     │
│ ✓ Appropriate for Challenge Promo         │
└────────────────────────────────────────────┘
```

### **3. Mixing Quality Visualization**

```
┌────────────────────────────────────────────┐
│ 🎚️ Mixing Quality                         │
│                                            │
│ Music Level:  ████████░░ -12 dB           │
│ Speech Level: ██████████ -6 dB            │
│                                            │
│ Balance: Good ✓                            │
│ Ratio: 0.5 (Music quieter than speech)    │
│                                            │
│ ✓ Ducking detected - Music lowers during  │
│   speech for clarity                       │
│                                            │
│ Audio Quality: Professional               │
│ No clipping or distortion detected        │
└────────────────────────────────────────────┘
```

### **4. Music Timeline**

```
┌────────────────────────────────────────────┐
│ 📊 Music Timeline                         │
│                                            │
│ 0:00 ──────────────────────────── 3:00    │
│      ██████████████████████████            │
│      Music: Continuous                     │
│                                            │
│      0:00 - Intro (Low intensity)         │
│      0:30 - Build (Medium intensity)      │
│      1:15 - Peak (High intensity)         │
│      2:30 - Sustain (High intensity)      │
└────────────────────────────────────────────┘
```

---

## 📈 Music Effectiveness Scoring

### **Music Score (0-100)**

Components:
1. **Character Fit (35%)** - Does music match character type?
2. **Mixing Quality (25%)** - Professional balance and ducking?
3. **Appropriateness (20%)** - Fits promo type and tone?
4. **Enhancement (20%)** - Improves performance vs distracts?

Formula:
```python
music_score = (
    character_fit * 0.35 +
    mixing_quality * 0.25 +
    appropriateness * 0.20 +
    enhancement * 0.20
)
```

### **Integration with Overall Score**

Music analysis impacts:
- **Delivery** category (indirect - music affects pacing)
- **Overall Production Quality** (direct)
- **Overall Score** weighting (3-5% influence)

---

## 🎭 Character-Specific Music Guidelines

### **Heel (Villain) Characters**

**Effective Music:**
- Heavy rock, metal, industrial
- Dark hip-hop, aggressive trap
- Ominous orchestral, horror soundscape
- Minor keys, low frequencies
- Aggressive tempo (120-140 BPM)

**Avoid:**
- Uplifting pop, cheerful music
- Heroic orchestral
- Major key upbeat tracks

**Examples:**
- WWE: "The Game" (Triple H) - Heavy rock
- AEW: "Judas" (Chris Jericho) - Hard rock
- WWE: "Cult of Personality" (CM Punk as heel) - Aggressive

### **Face (Hero) Characters**

**Effective Music:**
- Heroic orchestral, epic cinematic
- Uplifting rock, motivational anthems
- Energetic pop-rock
- Major keys, inspiring melodies
- Moderate to fast tempo (110-135 BPM)

**Avoid:**
- Dark, ominous tones
- Overly aggressive industrial
- Minor key depressing music

**Examples:**
- WWE: "You Can't See Me" (John Cena) - Uplifting hip-hop
- WWE: "Real American" (Hulk Hogan) - Heroic rock
- AEW: "Wild Thing" (Jon Moxley as face) - Rock anthem

### **Tweener (Anti-Hero) Characters**

**Effective Music:**
- Edgy modern rock
- Alternative hip-hop
- Cinematic hybrid orchestral
- Atmospheric electronic
- Versatile tempo (100-130 BPM)

**Avoid:**
- Overly cheerful/poppy
- Overly dark/ominous
- Generic production music

**Examples:**
- WWE: "Voices" (Randy Orton) - Edgy rock
- WWE: "Metalingus" (Edge) - Alternative metal
- AEW: "Battle Cry" (Kenny Omega) - Cinematic

---

## 🔬 Source Separation Technology

### **Spleeter (Recommended)**

```python
from spleeter.separator import Separator

def separate_music_from_speech(audio_file):
    """Use Spleeter to separate music and vocals"""
    # Initialize separator (2 stems: vocals + accompaniment)
    separator = Separator('spleeter:2stems')

    # Perform separation
    separator.separate_to_file(
        audio_file,
        destination='output/',
        codec='wav'
    )

    # Returns:
    # - vocals.wav (speech/singing)
    # - accompaniment.wav (music/instruments)

    return {
        'vocals_file': 'output/vocals.wav',
        'music_file': 'output/accompaniment.wav'
    }
```

**Alternative: Demucs** (Higher quality, slower)

---

## 📊 Example Analysis Output

```json
{
  "music_analysis": {
    "music_detected": true,
    "music_present_percentage": 100,
    "music_characteristics": {
      "tempo_bpm": 125,
      "tempo_category": "fast",
      "intensity_level": "intense",
      "intensity_score": 0.82,
      "key_type": "minor",
      "emotional_tone": "dark",
      "has_dynamic_builds": true
    },
    "mixing_quality": {
      "music_level_db": -12.5,
      "speech_level_db": -6.2,
      "balance_ratio": 0.48,
      "balance_quality": "excellent",
      "ducking_detected": true,
      "music_too_loud": false,
      "music_too_quiet": false,
      "clipping_detected": false
    },
    "music_effectiveness": {
      "overall_score": 82,
      "fits_character": true,
      "fits_promo_type": true,
      "enhances_performance": true,
      "effectiveness_level": "excellent"
    },
    "music_style_assessment": {
      "style_description": "Heavy industrial rock with aggressive percussion and dark synthesizers",
      "tempo_appropriateness": "excellent",
      "intensity_match": "excellent",
      "mood_alignment": "excellent",
      "feedback": "The music perfectly complements the heel character's intimidating presence. The fast tempo (125 BPM) matches the promo's aggressive energy, and the minor key creates a menacing atmosphere ideal for a villain character."
    },
    "mixing_assessment": {
      "volume_balance": "excellent",
      "ducking_quality": "excellent",
      "overall_mix_quality": "excellent",
      "issues": [],
      "feedback": "Professional-quality mixing. Music is properly balanced at -12 dB while speech sits at -6 dB, creating excellent clarity. The ducking effect lowers music during key speech moments, ensuring dialogue is never obscured."
    },
    "strengths": [
      "Perfect tempo match for aggressive challenge promo",
      "Minor key reinforces heel character darkness",
      "Professional mixing with proper ducking",
      "Music builds intensity during key moments",
      "No audio quality issues (clipping, distortion)"
    ],
    "weaknesses": [
      "Music slightly overpowers speech at 00:45 mark",
      "Could benefit from subtle fade-in at start"
    ],
    "recommendations": [
      "Lower music volume by 2-3 dB at 00:45 during climax",
      "Add 1-2 second fade-in at beginning for smoother start",
      "Consider adding brief music pause at 01:30 for dramatic effect",
      "Current music style is excellent - maintain for future promos"
    ],
    "example_music_suggestions": [
      "Continue using heavy industrial rock for heel promos",
      "Consider darker electronic elements for added menace",
      "Explore aggressive trap beats for modern heel aesthetic"
    ],
    "overall_feedback": "The background music is highly effective, perfectly matching the heel character's aggressive persona with its fast tempo, minor key, and intense energy. Professional mixing ensures speech clarity while maintaining musical impact. Minor adjustments to volume at peak moments would achieve perfection."
  }
}
```

---

## 🚀 Implementation Phases

### **Phase 1: Detection & Basic Analysis (Week 1)**
- ✅ Music presence detection
- ✅ Tempo/BPM detection
- ✅ Intensity/energy analysis
- ✅ Volume level detection

### **Phase 2: Advanced Analysis (Week 2)**
- ⏳ Source separation (Spleeter integration)
- ⏳ Key detection (major/minor)
- ⏳ Music/speech balance analysis
- ⏳ Ducking detection

### **Phase 3: AI Evaluation (Week 3)**
- ⏳ Enhanced Claude prompts for music critique
- ⏳ Character-specific recommendations
- ⏳ Promo type alignment scoring
- ⏳ Music effectiveness rating

### **Phase 4: UI Integration (Week 4)**
- ⏳ Music analysis card component
- ⏳ Characteristics display
- ⏳ Mixing quality visualization
- ⏳ Music timeline

### **Phase 5: Testing & Refinement (Week 5)**
- ⏳ Test with various music styles
- ⏳ Validate detection accuracy
- ⏳ Refine scoring algorithms
- ⏳ User feedback integration

---

## 📚 Dependencies

### **Python Libraries:**
```
librosa>=0.10.0        # Audio analysis
spleeter>=2.3.0        # Source separation
pydub>=0.25.0          # Audio manipulation
numpy>=1.24.0          # Numerical operations
essentia>=2.1b6        # Music information retrieval
```

### **System Requirements:**
- FFmpeg (for audio extraction)
- Sufficient RAM for source separation (4GB+)
- GPU recommended for Spleeter (optional)

---

## 🎯 Success Metrics

1. **Detection Accuracy** - 90%+ correct music presence detection
2. **Tempo Accuracy** - Within ±5 BPM of actual tempo
3. **Balance Assessment** - Correlates with professional mixing standards
4. **Appropriateness Scoring** - User feedback validates recommendations
5. **Performance** - Music analysis adds <15 seconds to processing time

---

## 💡 Future Enhancements

- **Music Recommendation Engine** - Suggest specific tracks
- **Royalty-Free Music Database** - Integrate with free music libraries
- **Beat Matching** - Suggest editing cuts on beat
- **Music Licensing Check** - Detect copyrighted music
- **Custom Music Upload** - Allow users to test different tracks
- **Music Mood Heatmap** - Show intensity changes over time

---

**This feature elevates the Wrestling Promo Analyzer to provide complete production feedback covering performance, visuals, AND audio!** 🎵✨
