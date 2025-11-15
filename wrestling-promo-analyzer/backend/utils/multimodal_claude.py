"""
Multimodal Claude Integration for Visual Analysis

Handles sending both text and images to Claude Vision API.
Implements image encoding, compression, and cost-optimized frame selection.
"""

import base64
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from PIL import Image
import io
import logging

from anthropic import Anthropic

logger = logging.getLogger(__name__)


class MultimodalClaudeError(Exception):
    """Error during multimodal Claude API call"""
    pass


class MultimodalClaudeClient:
    """
    Client for Claude Vision API with multimodal capabilities

    Handles:
    - Image encoding to base64
    - Image compression for cost optimization
    - Multimodal prompt construction
    - API calls with both text and images
    """

    def __init__(self, api_key: str, model: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize multimodal Claude client

        Args:
            api_key: Anthropic API key
            model: Claude model to use (must support vision)
        """
        self.client = Anthropic(api_key=api_key)
        self.model = model

        # Vision-capable models
        self.vision_models = {
            "claude-3-5-sonnet-20241022",
            "claude-3-opus-20240229",
            "claude-3-sonnet-20240229",
            "claude-3-haiku-20240307",
        }

        if model not in self.vision_models:
            logger.warning(f"Model {model} may not support vision. Vision-capable models: {self.vision_models}")

    def encode_image(
        self,
        image_path: str,
        max_size: Tuple[int, int] = (1568, 1568),
        quality: int = 85
    ) -> Tuple[str, str, int]:
        """
        Encode image to base64 with optional compression

        Claude Vision API recommendations:
        - Max dimension: 1568px (larger images are resized)
        - Format: JPEG, PNG, GIF, WebP
        - Max size: 5MB per image

        Args:
            image_path: Path to image file
            max_size: Maximum (width, height) - resize if larger
            quality: JPEG quality (1-100, lower = smaller file)

        Returns:
            Tuple of (base64_data, media_type, file_size_bytes)
        """
        try:
            # Open image
            img = Image.open(image_path)

            # Get original format
            original_format = img.format
            media_type = f"image/{original_format.lower()}" if original_format else "image/jpeg"

            # Convert RGBA to RGB if needed (for JPEG)
            if img.mode == 'RGBA':
                # Create white background
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # Use alpha channel as mask
                img = background

            # Resize if too large
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                logger.info(f"Resizing image from {img.size} to fit {max_size}")
                img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # Convert to bytes
            buffer = io.BytesIO()

            # Save as JPEG for better compression
            img.save(buffer, format='JPEG', quality=quality, optimize=True)
            buffer.seek(0)

            # Encode to base64
            image_data = base64.standard_b64encode(buffer.getvalue()).decode('utf-8')
            file_size = len(buffer.getvalue())

            logger.info(f"Encoded image: {file_size} bytes ({file_size / 1024:.1f}KB)")

            return image_data, "image/jpeg", file_size

        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            raise MultimodalClaudeError(f"Failed to encode image: {e}")

    def create_multimodal_content(
        self,
        text: str,
        image_paths: List[str],
        image_positions: Optional[List[int]] = None
    ) -> List[Dict[str, Any]]:
        """
        Create multimodal content blocks for Claude API

        Args:
            text: Text content
            image_paths: List of image file paths
            image_positions: Optional list of positions where images should be inserted
                           If None, images are placed after text

        Returns:
            List of content blocks in Claude format:
            [
                {"type": "text", "text": "..."},
                {"type": "image", "source": {"type": "base64", "media_type": "...", "data": "..."}},
                ...
            ]
        """
        content_blocks = []

        # If no specific positions, add text first, then all images
        if image_positions is None:
            # Add text block
            content_blocks.append({
                "type": "text",
                "text": text
            })

            # Add all images
            for image_path in image_paths:
                try:
                    image_data, media_type, file_size = self.encode_image(image_path)

                    content_blocks.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": media_type,
                            "data": image_data,
                        }
                    })
                except Exception as e:
                    logger.error(f"Skipping image {image_path}: {e}")
                    continue

        else:
            # Interleave text and images at specific positions
            # This is more complex - for now, use simple approach
            # TODO: Implement if needed for specific use cases
            raise NotImplementedError("Custom image positions not yet implemented")

        return content_blocks

    def analyze_with_vision(
        self,
        system_prompt: str,
        user_text: str,
        frame_paths: List[str],
        max_tokens: int = 4096,
        temperature: float = 1.0,
    ) -> Dict[str, Any]:
        """
        Send multimodal request to Claude with both text and images

        Args:
            system_prompt: System prompt (text only)
            user_text: User message text
            frame_paths: List of frame image paths to include
            max_tokens: Maximum tokens in response
            temperature: Sampling temperature

        Returns:
            Dictionary with:
            {
                "response_text": "...",
                "usage": {
                    "input_tokens": 1000,
                    "output_tokens": 500,
                },
                "model": "...",
                "images_sent": 5,
            }
        """
        logger.info(f"Sending multimodal request: {len(frame_paths)} images")

        # Create multimodal content
        content = self.create_multimodal_content(user_text, frame_paths)

        # Log content structure
        image_count = sum(1 for block in content if block["type"] == "image")
        logger.info(f"Content blocks: {len(content)} total, {image_count} images")

        # Make API call
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                temperature=temperature,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": content
                    }
                ]
            )

            # Extract response text
            response_text = ""
            for block in response.content:
                if hasattr(block, 'text'):
                    response_text += block.text

            # Return structured result
            result = {
                "response_text": response_text,
                "usage": {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                "model": response.model,
                "images_sent": image_count,
                "stop_reason": response.stop_reason,
            }

            logger.info(
                f"✅ Claude Vision API call successful: "
                f"{response.usage.input_tokens} in + {response.usage.output_tokens} out tokens"
            )

            return result

        except Exception as e:
            logger.error(f"Claude Vision API call failed: {e}")
            raise MultimodalClaudeError(f"API call failed: {e}")


def select_frames_for_api(
    frames: List[Dict],
    target_count: int = 10,
    max_count: int = 15
) -> List[Dict]:
    """
    Select frames to send to Claude Vision API

    Strategy:
    1. Filter to key frames only
    2. If too many, select top N by importance
    3. Ensure temporal distribution

    Args:
        frames: List of frame dictionaries with is_key_frame and importance_score
        target_count: Target number of frames
        max_count: Maximum frames (hard limit due to API constraints)

    Returns:
        List of selected frames, sorted by timestamp
    """
    # Filter to key frames
    key_frames = [f for f in frames if f.get("is_key_frame", False)]

    if not key_frames:
        logger.warning("No key frames found, selecting all frames")
        key_frames = frames

    # If too many, select top by importance
    if len(key_frames) > max_count:
        logger.info(f"Reducing {len(key_frames)} key frames to {max_count}")
        key_frames = sorted(
            key_frames,
            key=lambda f: float(f.get("importance_score", 0)),
            reverse=True
        )[:max_count]

    # If still too many for target, further reduce
    if len(key_frames) > target_count:
        logger.info(f"Further reducing to target of {target_count} frames")
        key_frames = sorted(
            key_frames,
            key=lambda f: float(f.get("importance_score", 0)),
            reverse=True
        )[:target_count]

    # Sort by timestamp for chronological presentation
    key_frames = sorted(key_frames, key=lambda f: float(f["timestamp_seconds"]))

    logger.info(f"Selected {len(key_frames)} frames for API")
    return key_frames


def estimate_vision_cost(
    num_images: int,
    avg_image_size_kb: int = 100,
    text_tokens: int = 2000,
    output_tokens: int = 2000,
    model: str = "claude-3-5-sonnet-20241022"
) -> float:
    """
    Estimate cost of multimodal Claude API call

    Claude Vision pricing:
    - Images are counted as tokens based on size
    - Approximate: 1 image ≈ 1000-2000 tokens (depends on size/resolution)
    - Text tokens: Standard pricing

    Args:
        num_images: Number of images
        avg_image_size_kb: Average image size in KB
        text_tokens: Estimated text tokens in prompt
        output_tokens: Estimated output tokens
        model: Claude model

    Returns:
        Estimated cost in USD
    """
    from utils.cost_tracking import calculate_cost

    # Estimate image tokens
    # Rough approximation: ~10 tokens per KB of image
    # A 100KB JPEG ≈ 1000 tokens
    image_tokens_per_image = avg_image_size_kb * 10
    total_image_tokens = num_images * image_tokens_per_image

    # Total input tokens
    total_input_tokens = text_tokens + total_image_tokens

    # Calculate cost
    cost = calculate_cost(total_input_tokens, output_tokens, model)

    logger.info(
        f"Cost estimate: {num_images} images (~{total_image_tokens} tokens) + "
        f"{text_tokens} text tokens = ${cost:.4f}"
    )

    return float(cost)


def build_multimodal_prompt(
    transcript: str,
    video_metadata: Dict,
    frame_timestamps: List[float],
    num_frames: int,
    enhanced_visual_summary: Optional[Dict] = None
) -> str:
    """
    Build enhanced prompt for multimodal analysis

    Args:
        transcript: Full transcript text
        video_metadata: Video metadata (title, duration, etc.)
        frame_timestamps: List of frame timestamps being sent
        num_frames: Number of frames included
        enhanced_visual_summary: Optional enhanced visual analysis summary with emotions, gestures, etc.

    Returns:
        Formatted prompt string
    """
    # Format timestamps
    timestamp_list = ", ".join([f"{ts:.1f}s" for ts in frame_timestamps])

    # Build enhanced visual context if available
    visual_context = ""
    if enhanced_visual_summary:
        emotion_breakdown = enhanced_visual_summary.get("emotion_breakdown", {})
        top_gestures = enhanced_visual_summary.get("top_gestures", [])
        eye_contact = enhanced_visual_summary.get("avg_eye_contact_score", 0)
        power_pose_ratio = enhanced_visual_summary.get("power_pose_ratio", 0)
        shot_type = enhanced_visual_summary.get("dominant_shot_type", "unknown")
        framing_quality = enhanced_visual_summary.get("avg_framing_quality", 0)

        # Format emotion breakdown
        if emotion_breakdown:
            emotions_text = ", ".join([f"{k}: {v*100:.0f}%" for k, v in emotion_breakdown.items()])
            visual_context += f"\n- Detected Emotions: {emotions_text}"

        # Format gestures
        if top_gestures:
            gestures_text = ", ".join([f"{g['gesture']} ({g['count']}x)" for g in top_gestures[:3]])
            visual_context += f"\n- Key Gestures: {gestures_text}"

        # Add other metrics
        visual_context += f"\n- Average Eye Contact Score: {eye_contact:.2f}/1.0"
        visual_context += f"\n- Power Pose Ratio: {power_pose_ratio*100:.0f}%"
        visual_context += f"\n- Dominant Shot Type: {shot_type}"
        visual_context += f"\n- Camera Framing Quality: {framing_quality:.2f}/1.0"

    prompt = f"""Analyze this wrestling promo using BOTH the transcript AND the {num_frames} video frames provided.

**PROMO INFORMATION:**
- Title: {video_metadata.get('promo_title', 'Untitled')}
- Duration: {video_metadata.get('duration_seconds', 0):.1f} seconds
- Character Type: {video_metadata.get('character_type', 'Not specified')}
- Promo Type: {video_metadata.get('promo_type', 'Not specified')}
- Context: {video_metadata.get('promo_context', 'None provided')}

**TRANSCRIPT:**
{transcript}

**VISUAL ANALYSIS:**
I'm providing {num_frames} key frames from critical moments in the promo at these timestamps:
{timestamp_list}

Each frame is shown below in chronological order.

**PRE-ANALYSIS VISUAL METRICS:**
The frames have been pre-analyzed for visual features. Use these insights to inform your analysis:{visual_context if visual_context else ""}

**YOUR TASK:**
Analyze BOTH what the wrestler says (transcript) AND how they present themselves (visual frames).

Provide detailed analysis with:

1. **Overall Score (0-100)** and **Overall Grade (A+ to D)**

2. **Category Scores (0-100)** for:
   - Psychology: Storytelling, emotional connection, character depth
   - Character Work: Consistency, authenticity, uniqueness
   - Delivery: Voice control, pacing, emphasis
   - Story Structure: Beginning, middle, end, narrative flow
   - Crowd Connection: Relatability, engagement, reaction potential
   - Originality: Creativity, fresh ideas, avoiding clichés
   - **Facial Expressions**: Emotion conveyance, authenticity, eye contact
   - **Body Language**: Posture, gestures, physical presence
   - **Visual Presence**: Camera work, charisma, overall presentation

3. **Summary** (2-3 paragraphs): Overall assessment combining verbal and visual analysis

4. **Strengths** (3-5 bullet points): What works well (both verbal and visual)

5. **Weaknesses** (3-5 bullet points): Areas for improvement (both verbal and visual)

6. **Timestamped Feedback**: Specific moments with analysis
   Format: [{{"timestamp": "00:15", "comment": "...", "type": "positive/negative", "visual_element": "eye_contact/gesture/expression/etc"}}]
   - Reference specific frames when giving visual feedback
   - Note when body language matches or contradicts the words
   - Highlight powerful visual moments

7. **Specific Recommendations** (3-5 actionable items): How to improve, including visual performance tips

8. **Visual Analysis Summary**:
   - Emotion breakdown: Percentages of different emotions detected (confident, intense, neutral, etc.)
   - Top gestures: Most effective gestures used
   - Production quality: Lighting, framing, background assessment

Format your response as JSON with this structure:
{{
  "overall_score": 85,
  "overall_grade": "A-",
  "category_scores": {{
    "psychology": 88,
    "character_work": 82,
    "delivery": 90,
    "story_structure": 80,
    "crowd_connection": 85,
    "originality": 75,
    "facial_expressions": 87,
    "body_language": 90,
    "visual_presence": 88
  }},
  "summary": "...",
  "strengths": ["...", "...", "..."],
  "weaknesses": ["...", "...", "..."],
  "timestamped_feedback": [
    {{"timestamp": "00:15", "comment": "...", "type": "positive", "visual_element": "eye_contact"}},
    {{"timestamp": "01:23", "comment": "...", "type": "negative", "visual_element": "posture"}}
  ],
  "specific_recommendations": ["...", "...", "..."],
  "visual_analysis": {{
    "emotion_breakdown": {{"confident": 0.6, "intense": 0.3, "neutral": 0.1}},
    "top_gestures": [
      {{"gesture": "pointing", "count": 5, "effectiveness": 0.85}},
      {{"gesture": "open_hands", "count": 3, "effectiveness": 0.90}}
    ],
    "production_quality": {{
      "lighting": 0.85,
      "framing": 0.90,
      "background": 0.80
    }}
  }}
}}
"""

    return prompt
