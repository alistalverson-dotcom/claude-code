"""
Utility modules for Wrestling Promo Analyzer
"""

from .cost_tracking import calculate_cost, get_cost_summary, get_model_pricing_info
from .logging_config import setup_logging, get_logger, log_api_request, log_task_event
from .frame_extraction import extract_and_analyze_frames, cleanup_frames, FrameExtractor
from .visual_analysis import analyze_frames, get_key_frame_analysis_summary, VisualAnalyzer
from .enhanced_visual_analysis import (
    analyze_frames_enhanced,
    aggregate_enhanced_analysis,
    EnhancedVisualAnalyzer,
)
from .multimodal_claude import (
    MultimodalClaudeClient,
    select_frames_for_api,
    estimate_vision_cost,
    build_multimodal_prompt,
)

__all__ = [
    # Cost tracking
    "calculate_cost",
    "get_cost_summary",
    "get_model_pricing_info",
    # Logging
    "setup_logging",
    "get_logger",
    "log_api_request",
    "log_task_event",
    # Frame extraction
    "extract_and_analyze_frames",
    "cleanup_frames",
    "FrameExtractor",
    # Visual analysis
    "analyze_frames",
    "get_key_frame_analysis_summary",
    "VisualAnalyzer",
    # Enhanced visual analysis
    "analyze_frames_enhanced",
    "aggregate_enhanced_analysis",
    "EnhancedVisualAnalyzer",
    # Multimodal Claude
    "MultimodalClaudeClient",
    "select_frames_for_api",
    "estimate_vision_cost",
    "build_multimodal_prompt",
]
