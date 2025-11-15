# Visual Effects & Filters Analysis - Design Document

## 🎬 Overview

This document outlines the visual effects and filters detection system for wrestling promo analysis. The system identifies production techniques and evaluates their effectiveness in enhancing the promo's impact.

---

## 🎯 Goals

1. **Detect** common visual filters and effects used in wrestling promos
2. **Analyze** whether effects enhance or distract from the performance
3. **Provide feedback** on production technique appropriateness
4. **Score** effects quality and their fit with character/promo type

---

## 📊 Types of Visual Effects to Detect

### **1. Color Grading & Filters**

| Effect | Description | Common Usage | Detection Method |
|--------|-------------|--------------|------------------|
| **Black & White** | Monochrome/grayscale | Serious/dramatic promos | Color saturation analysis |
| **Sepia Tone** | Vintage brown tint | Nostalgic/retro promos | Color histogram analysis |
| **High Contrast** | Enhanced darks/lights | Intense/dramatic moments | Contrast ratio calculation |
| **Color Grading** | Altered color palette | Cinematic feel (teal/orange, warm/cool) | Dominant color analysis |
| **Desaturation** | Reduced color intensity | Somber/serious tone | Saturation levels |
| **Vignette** | Darkened edges | Focus on subject | Edge brightness analysis |

### **2. Motion Effects**

| Effect | Description | Common Usage | Detection Method |
|--------|-------------|--------------|------------------|
| **Slow Motion** | Reduced playback speed | Emphasize key moments | Frame timing analysis |
| **Speed Ramping** | Variable speed changes | Dramatic emphasis | Motion vector changes |
| **Motion Blur** | Blur during movement | Action sequences | Blur detection in motion |
| **Freeze Frame** | Paused moment | Dramatic punctuation | Static frame detection |

### **3. Visual Distortion Effects**

| Effect | Description | Common Usage | Detection Method |
|--------|-------------|--------------|------------------|
| **Glitch/Static** | Digital distortion | Unstable/chaotic character | Edge detection anomalies |
| **Film Grain** | Noise texture | Vintage/gritty aesthetic | Noise level analysis |
| **Chromatic Aberration** | Color fringing | Modern/artistic look | Color channel separation |
| **Lens Distortion** | Warped perspective | Creative/unsettling feel | Edge curvature analysis |
| **Shake/Handheld** | Camera instability | Raw/documentary style | Frame-to-frame motion |

### **4. Overlay & Composite Effects**

| Effect | Description | Common Usage | Detection Method |
|--------|-------------|--------------|------------------|
| **Text Overlays** | Graphics/captions | Name plates, emphasis | Text detection (OCR) |
| **Split Screen** | Multiple frames | Dual narratives | Layout analysis |
| **Picture-in-Picture** | Secondary frame | Reaction shots | Bounding box detection |
| **Green Screen** | Composited backgrounds | Fantasy/conceptual promos | Edge artifacts, color spill |
| **Light Leaks** | Simulated lens flares | Dreamy/ethereal feel | Bright spot detection |

### **5. Transition Effects**

| Effect | Description | Common Usage | Detection Method |
|--------|-------------|--------------|------------------|
| **Jump Cuts** | Abrupt scene changes | Fast-paced editing | Scene change frequency |
| **Fades** | Gradual transitions | Smooth scene changes | Brightness transitions |
| **Wipes** | Geometric transitions | Stylized editing | Directional changes |
| **Dissolves** | Blended transitions | Dreamlike sequences | Frame blending |

---

## 🔧 Technical Implementation

### **Backend: Effect Detection Module**

**File:** `backend/video_processing/effects_detector.py`

```python
class VisualEffectsDetector:
    """Detects visual filters and effects in video frames"""

    def analyze_frame(self, frame) -> EffectsAnalysis:
        """Analyze a single frame for effects"""
        return {
            'color_grading': self.detect_color_grading(frame),
            'filters': self.detect_filters(frame),
            'motion_effects': self.detect_motion_effects(frame),
            'distortion': self.detect_distortion(frame),
            'overlays': self.detect_overlays(frame),
            'production_quality': self.assess_production_quality(frame)
        }

    def detect_color_grading(self, frame) -> dict:
        """Detect color grading and filters"""
        # Analyze HSV color space
        # Calculate saturation levels
        # Detect dominant color palettes
        # Identify specific filters (B&W, sepia, etc.)

    def detect_filters(self, frame) -> dict:
        """Detect applied filters"""
        # Vignette detection
        # Film grain analysis
        # Contrast ratio calculation
        # Sharpness/blur levels

    def detect_motion_effects(self, frame, prev_frame) -> dict:
        """Detect motion-based effects"""
        # Optical flow analysis
        # Motion blur detection
        # Camera shake detection
        # Speed ramping indicators

    def detect_distortion(self, frame) -> dict:
        """Detect distortion effects"""
        # Glitch/artifact detection
        # Chromatic aberration
        # Lens distortion
        # Noise level analysis

    def detect_overlays(self, frame) -> dict:
        """Detect overlays and compositing"""
        # Text detection (OCR)
        # Split screen detection
        # Green screen artifacts
        # Light leak/flare detection
```

### **Enhanced Claude Vision Prompts**

**File:** `backend/prompts/visual_effects_prompt.txt`

```
VISUAL EFFECTS & PRODUCTION TECHNIQUE ANALYSIS

Analyze the production techniques and visual effects in this wrestling promo frame:

1. COLOR GRADING & FILTERS:
   - Is the footage in color, black & white, sepia, or otherwise graded?
   - Are there specific color palettes (teal/orange, warm, cool, desaturated)?
   - Is there a vignette effect?
   - How does the color grading fit the character/promo tone?

2. VISUAL EFFECTS:
   - Any film grain, glitch effects, or distortion?
   - Text overlays, graphics, or lower thirds?
   - Light leaks, lens flares, or other optical effects?
   - Green screen/compositing (look for edge artifacts)?

3. MOTION & EDITING:
   - Signs of slow motion or speed ramping?
   - Camera shake or handheld movement?
   - Fast cutting or smooth transitions?
   - Freeze frames or dramatic pauses?

4. EFFECTIVENESS ASSESSMENT:
   - Do the effects ENHANCE the promo or DISTRACT from it?
   - Are effects appropriate for the character type (heel/face/tweener)?
   - Do effects feel professional or amateurish?
   - Are effects overused or used sparingly?

5. PRODUCTION TECHNIQUE RATING (0-100):
   - Technical quality of effects execution
   - Appropriateness for wrestling promo context
   - Enhancement of storytelling
   - Overall production sophistication

Provide specific feedback on:
- Which effects work well and why
- Which effects should be reduced/removed
- Missing effects that could enhance the promo
- Production technique recommendations
```

### **Data Models**

**File:** `backend/models/visual_effects.py`

```python
from pydantic import BaseModel, Field
from typing import List, Optional, Dict

class ColorGrading(BaseModel):
    """Color grading analysis"""
    style: str = Field(..., description="B&W, sepia, color_graded, natural")
    dominant_colors: List[str] = Field(default_factory=list)
    saturation_level: float = Field(..., ge=0, le=1)
    contrast_ratio: float = Field(..., ge=0, le=5)
    vignette_detected: bool = False
    color_palette: str = Field(..., description="warm, cool, teal_orange, neutral")

class AppliedFilters(BaseModel):
    """Detected visual filters"""
    film_grain: bool = False
    film_grain_intensity: Optional[float] = Field(None, ge=0, le=1)
    lens_blur: Optional[float] = Field(None, ge=0, le=1)
    chromatic_aberration: bool = False
    sharpening: Optional[float] = Field(None, ge=0, le=1)

class MotionEffects(BaseModel):
    """Motion-based effects"""
    slow_motion_detected: bool = False
    speed_ramping: bool = False
    camera_shake_level: float = Field(default=0, ge=0, le=1)
    motion_blur_present: bool = False
    handheld_style: bool = False

class DistortionEffects(BaseModel):
    """Distortion and glitch effects"""
    glitch_effects: bool = False
    digital_noise: float = Field(default=0, ge=0, le=1)
    lens_distortion: float = Field(default=0, ge=0, le=1)
    static_interference: bool = False

class OverlayEffects(BaseModel):
    """Overlay and composite effects"""
    text_overlays: List[str] = Field(default_factory=list)
    graphics_present: bool = False
    split_screen: bool = False
    picture_in_picture: bool = False
    green_screen_artifacts: bool = False
    light_leaks: bool = False

class EffectsAppropriateness(BaseModel):
    """Assessment of effects usage"""
    enhances_promo: bool = Field(..., description="Effects enhance vs distract")
    fits_character: bool = Field(..., description="Appropriate for character type")
    professional_quality: float = Field(..., ge=0, le=1)
    overuse_detected: bool = False
    underutilized: bool = False

class EffectsAnalysis(BaseModel):
    """Complete visual effects analysis"""
    color_grading: ColorGrading
    filters: AppliedFilters
    motion_effects: MotionEffects
    distortion_effects: DistortionEffects
    overlay_effects: OverlayEffects
    appropriateness: EffectsAppropriateness
    production_technique_score: int = Field(..., ge=0, le=100)
    effects_summary: str = Field(..., description="Brief summary of effects used")
    effectiveness_feedback: str = Field(..., description="How effects impact promo")
    recommendations: List[str] = Field(default_factory=list)

class FrameEffectsAnalysis(BaseModel):
    """Effects analysis for a single frame"""
    frame_number: int
    timestamp: str
    effects: EffectsAnalysis
```

---

## 🎨 UI Components

### **1. Effects Summary Card**

**File:** `frontend/src/components/EffectsSummaryCard.tsx`

Visual appearance:
```
┌────────────────────────────────────────────┐
│ 🎬 Production Techniques                  │
│                                            │
│ Effects Score: 78/100                      │
│                                            │
│ ✅ Working Well:                           │
│ • High contrast color grading              │
│ • Professional lighting                    │
│ • Subtle film grain for texture            │
│                                            │
│ ⚠️  Could Improve:                         │
│ • Reduce glitch effects (overused)        │
│ • Text overlays blocking face             │
│                                            │
│ 💡 Recommendations:                        │
│ • Add subtle vignette for focus           │
│ • Consider warmer color grade             │
└────────────────────────────────────────────┘
```

### **2. Color Grading Visualization**

```
┌────────────────────────────────────────────┐
│ 🎨 Color Grading Analysis                 │
│                                            │
│ Style: Cinematic Color Graded              │
│ Palette: Teal & Orange                     │
│                                            │
│ [Color swatches showing dominant colors]   │
│                                            │
│ Saturation: ████████░░ 85%                │
│ Contrast:   ██████████ 95%                │
│                                            │
│ ✓ High contrast enhances intensity        │
│ ✓ Color palette fits heel character       │
└────────────────────────────────────────────┘
```

### **3. Effects Timeline**

```
┌────────────────────────────────────────────┐
│ 📊 Effects Usage Timeline                 │
│                                            │
│ 0:00 ──────────────────────────── 3:00    │
│      ████          ████                    │
│      B&W Filter    Text Overlay            │
│                                            │
│           ████████████                     │
│           Film Grain Throughout            │
│                                            │
│                        ██                  │
│                        Glitch              │
└────────────────────────────────────────────┘
```

### **4. Effects Breakdown Table**

```
┌────────────────────────────────────────────┐
│ 🔍 Detailed Effects Breakdown             │
│                                            │
│ Effect Type      | Used | Effectiveness   │
│─────────────────────────────────────────── │
│ Color Grading    │  ✓   │ Excellent ⭐⭐⭐  │
│ Film Grain       │  ✓   │ Good ⭐⭐        │
│ Text Overlays    │  ✓   │ Fair ⭐         │
│ Glitch Effects   │  ✓   │ Overused ⚠️     │
│ Slow Motion      │  ✗   │ Not Used        │
│ Vignette         │  ✗   │ Recommended 💡  │
└────────────────────────────────────────────┘
```

---

## 📈 Scoring Integration

### **Production Technique Score (0-100)**

Components:
1. **Technical Quality (40%)** - How well effects are executed
2. **Appropriateness (30%)** - Fit with character/promo type
3. **Enhancement (20%)** - Whether effects improve storytelling
4. **Balance (10%)** - Not overused or underutilized

Formula:
```python
production_score = (
    technical_quality * 0.4 +
    appropriateness * 0.3 +
    enhancement * 0.2 +
    balance * 0.1
)
```

### **Integration with Overall Score**

Effects analysis impacts:
- **Production Quality** category (direct)
- **Visual Presence** category (indirect)
- **Overall Score** weighting (5-10% influence)

---

## 🎭 Character-Specific Recommendations

### **Heel (Villain) Characters**

**Effective Techniques:**
- Dark/desaturated color grading
- High contrast
- Glitch effects (moderate)
- Film grain for gritty feel
- Cool color temperatures
- Vignettes for intensity

**Avoid:**
- Overly bright/colorful
- Excessive light leaks
- Soft focus/dream effects

### **Face (Hero) Characters**

**Effective Techniques:**
- Natural/vibrant colors
- Balanced contrast
- Clean production
- Warm color temperatures
- Minimal distortion
- Professional graphics

**Avoid:**
- Overly dark/grim
- Heavy glitch effects
- Excessive filters

### **Tweener (Anti-Hero) Characters**

**Effective Techniques:**
- Mixed warm/cool tones
- Moderate contrast
- Strategic filter use
- Cinematic color grading
- Balanced effects

**Avoid:**
- Overly polished (too face-like)
- Overly chaotic (too heel-like)

---

## 🔬 Detection Algorithms

### **1. Black & White Detection**

```python
def detect_black_and_white(frame):
    """Detect if frame is B&W or desaturated"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    saturation = hsv[:, :, 1]
    avg_saturation = np.mean(saturation) / 255.0

    if avg_saturation < 0.1:
        return {'is_bw': True, 'confidence': 1.0}
    elif avg_saturation < 0.3:
        return {'is_desaturated': True, 'saturation': avg_saturation}
    else:
        return {'is_color': True, 'saturation': avg_saturation}
```

### **2. Film Grain Detection**

```python
def detect_film_grain(frame):
    """Detect presence and intensity of film grain"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calculate noise level using Laplacian variance
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    noise_level = laplacian.var()

    # High-frequency noise indicates grain
    film_grain_present = noise_level > GRAIN_THRESHOLD
    intensity = min(noise_level / MAX_GRAIN, 1.0)

    return {
        'present': film_grain_present,
        'intensity': intensity
    }
```

### **3. Color Grading Detection**

```python
def detect_color_grading(frame):
    """Detect color grading style and palette"""
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Get dominant colors
    pixels = frame.reshape(-1, 3)
    kmeans = KMeans(n_clusters=5)
    kmeans.fit(pixels)
    dominant_colors = kmeans.cluster_centers_

    # Analyze color temperature
    avg_b, avg_g, avg_r = cv2.mean(frame)[:3]
    color_temp = 'warm' if avg_r > avg_b + 20 else 'cool' if avg_b > avg_r + 20 else 'neutral'

    # Detect teal & orange
    teal_orange = detect_teal_orange_look(dominant_colors)

    return {
        'dominant_colors': dominant_colors.tolist(),
        'color_temperature': color_temp,
        'teal_orange_grading': teal_orange,
        'saturation': np.mean(hsv[:, :, 1]) / 255.0,
        'value': np.mean(hsv[:, :, 2]) / 255.0
    }
```

### **4. Vignette Detection**

```python
def detect_vignette(frame):
    """Detect vignette effect (darkened edges)"""
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    h, w = gray.shape

    # Compare center brightness to edges
    center_region = gray[h//4:3*h//4, w//4:3*w//4]
    edge_region = np.concatenate([
        gray[0:h//8, :].flatten(),
        gray[-h//8:, :].flatten(),
        gray[:, 0:w//8].flatten(),
        gray[:, -w//8:].flatten()
    ])

    center_brightness = np.mean(center_region)
    edge_brightness = np.mean(edge_region)

    vignette_strength = (center_brightness - edge_brightness) / 255.0

    return {
        'detected': vignette_strength > 0.15,
        'strength': max(0, vignette_strength)
    }
```

### **5. Text Overlay Detection**

```python
def detect_text_overlays(frame):
    """Detect text overlays using OCR"""
    import pytesseract

    # Run OCR on frame
    text = pytesseract.image_to_string(frame)

    # Get text bounding boxes
    data = pytesseract.image_to_data(frame, output_type=pytesseract.Output.DICT)

    text_regions = []
    for i, word in enumerate(data['text']):
        if word.strip():
            text_regions.append({
                'text': word,
                'bbox': (data['left'][i], data['top'][i],
                        data['width'][i], data['height'][i]),
                'confidence': data['conf'][i]
            })

    return {
        'detected': len(text_regions) > 0,
        'text_count': len(text_regions),
        'text_regions': text_regions
    }
```

---

## 📊 Example Analysis Output

```json
{
  "effects_analysis": {
    "color_grading": {
      "style": "cinematic_color_graded",
      "dominant_colors": ["#1a3d5c", "#d4740f", "#2a2a2a"],
      "saturation_level": 0.75,
      "contrast_ratio": 2.8,
      "vignette_detected": true,
      "color_palette": "teal_orange"
    },
    "filters": {
      "film_grain": true,
      "film_grain_intensity": 0.35,
      "lens_blur": null,
      "chromatic_aberration": false,
      "sharpening": 0.6
    },
    "motion_effects": {
      "slow_motion_detected": false,
      "speed_ramping": false,
      "camera_shake_level": 0.2,
      "motion_blur_present": false,
      "handheld_style": true
    },
    "distortion_effects": {
      "glitch_effects": true,
      "digital_noise": 0.4,
      "lens_distortion": 0.1,
      "static_interference": false
    },
    "overlay_effects": {
      "text_overlays": ["THE CHAMPION", "PAYBACK"],
      "graphics_present": true,
      "split_screen": false,
      "picture_in_picture": false,
      "green_screen_artifacts": false,
      "light_leaks": false
    },
    "appropriateness": {
      "enhances_promo": true,
      "fits_character": true,
      "professional_quality": 0.85,
      "overuse_detected": true,
      "underutilized": false
    },
    "production_technique_score": 78,
    "effects_summary": "Cinematic teal/orange grading with film grain and moderate glitch effects. Handheld camera style with professional color work.",
    "effectiveness_feedback": "The color grading and film grain create a gritty, cinematic feel that perfectly fits the heel character. However, glitch effects are slightly overused (appearing 8 times in 3 minutes) and can become distracting. Text overlays are well-timed but occasionally block facial expressions.",
    "recommendations": [
      "Reduce glitch effect frequency to 2-3 times per promo for maximum impact",
      "Position text overlays lower to avoid blocking face during key moments",
      "Consider adding subtle slow-motion on power moves for emphasis",
      "Current color grading is excellent - maintain this style"
    ]
  }
}
```

---

## 🚀 Implementation Phases

### **Phase 1: Core Detection (Week 1)**
- ✅ Color grading detection
- ✅ Basic filter detection (B&W, sepia, saturation)
- ✅ Vignette detection
- ✅ Contrast/brightness analysis

### **Phase 2: Advanced Effects (Week 2)**
- ⏳ Film grain detection
- ⏳ Motion effect detection
- ⏳ Text overlay detection (OCR)
- ⏳ Glitch/distortion detection

### **Phase 3: AI Analysis (Week 3)**
- ⏳ Enhanced Claude prompts for effects critique
- ⏳ Appropriateness scoring
- ⏳ Character-specific recommendations
- ⏳ Production technique rating

### **Phase 4: UI Integration (Week 4)**
- ⏳ Effects summary card component
- ⏳ Color grading visualization
- ⏳ Effects timeline
- ⏳ Detailed breakdown table

### **Phase 5: Testing & Refinement (Week 5)**
- ⏳ Test with various promo styles
- ⏳ Validate detection accuracy
- ⏳ Refine scoring algorithms
- ⏳ User feedback integration

---

## 📚 References & Inspiration

### **Wrestling Promo Production Styles**
- **Cinematic Promos** (e.g., "Firefly Fun House") - Heavy effects, color grading, compositing
- **Documentary Style** (e.g., CM Punk pipebombs) - Minimal effects, raw handheld
- **Broadcast Standard** (e.g., traditional backstage) - Professional but understated
- **Music Video Style** (e.g., entrance videos) - Heavy editing, transitions, effects

### **Color Grading in Wrestling**
- Heel characters: Desaturated, cool tones, high contrast
- Face characters: Vibrant, warm tones, balanced
- Supernatural characters: Extreme effects, heavy color work
- Reality-based: Minimal grading, natural look

---

## 🎯 Success Metrics

1. **Detection Accuracy** - 85%+ correct identification of effects
2. **Appropriateness Scoring** - Correlates with user feedback
3. **Actionable Recommendations** - Users find suggestions helpful
4. **Performance Impact** - <10% increase in processing time
5. **User Satisfaction** - Positive feedback on production insights

---

**This feature elevates the Wrestling Promo Analyzer from basic visual analysis to comprehensive production technique evaluation!** 🎬✨
