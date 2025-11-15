/**
 * TypeScript type definitions for Wrestling Promo Analyzer
 * Matches backend Pydantic schemas
 */

export interface VideoUploadResponse {
  video_id: string;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  status: string;
  message: string;
  created_at: string;
}

export interface VideoListItem {
  video_id: string;
  original_filename: string;
  promo_title: string | null;
  status: string;
  duration_seconds: number | null;
  created_at: string;
}

export interface TranscriptSegment {
  start: number;
  end: number;
  text: string;
}

export interface TranscriptResponse {
  id: string;
  video_id: string;
  full_text: string;
  segments: TranscriptSegment[];
  language: string;
  word_count: number | null;
  created_at: string;
}

export interface CategoryScores {
  psychology: number;
  character_work: number;
  delivery: number;
  story_structure: number;
  crowd_connection: number;
  originality: number;
  // Visual scores (multimodal analysis)
  facial_expressions?: number;
  body_language?: number;
  visual_presence?: number;
}

export interface TimestampedFeedback {
  timestamp: string;
  comment: string;
  type: 'positive' | 'negative' | 'neutral';
  visual_element?: string; // e.g., "eye_contact", "gesture", "expression"
}

// Visual Analysis Types
export interface EmotionBreakdown {
  [emotion: string]: number; // e.g., {"confident": 0.6, "intense": 0.3}
}

export interface Gesture {
  gesture: string;
  count: number;
  effectiveness: number;
}

export interface ProductionQuality {
  lighting?: number;
  framing?: number;
  background?: number;
  overall?: number;
}

// Visual Effects Analysis Types (NEW)
export interface ColorGradingAnalysis {
  style?: string;
  color_palette?: string;
  color_temperature?: string;
  dominant_colors?: string[];
  saturation_level?: number;
  contrast_ratio?: number;
  vignette_detected?: boolean;
  vignette_strength?: number;
  effectiveness?: string;
  feedback?: string;
}

export interface VisualFiltersAnalysis {
  film_grain?: boolean;
  film_grain_intensity?: string;
  blur_present?: boolean;
  chromatic_aberration?: boolean;
  overall_sharpness?: string;
  effectiveness?: string;
  feedback?: string;
}

export interface VisualEffectsAnalysis {
  text_overlays?: {
    present?: boolean;
    placement?: string;
    quality?: string;
    blocks_face?: boolean;
    effectiveness?: string;
  };
  glitch_effects?: boolean;
  light_leaks?: boolean;
  compositing?: boolean;
  other_effects?: string[];
  overall_effectiveness?: string;
  feedback?: string;
}

export interface CameraWorkAnalysis {
  stability?: string;
  style?: string;
  framing_quality?: string;
  effectiveness?: string;
  feedback?: string;
}

export interface EffectsAnalysis {
  color_grading?: ColorGradingAnalysis;
  filters?: VisualFiltersAnalysis;
  visual_effects?: VisualEffectsAnalysis;
  camera_work?: CameraWorkAnalysis;
  production_technique_score?: number;
  effects_summary?: string;
  effectiveness_feedback?: string;
  effects_working_well?: string[];
  effects_to_reduce?: string[];
  effects_to_add?: string[];
  recommendations?: string[];
}

export interface VisualAnalysisData {
  emotion_breakdown?: EmotionBreakdown;
  top_gestures?: Gesture[];
  production_quality?: ProductionQuality;
  effects_analysis?: EffectsAnalysis; // NEW
}

export interface VisualAnalysisResponse {
  id: string;
  analysis_id: string;
  facial_expression_score: number | null;
  body_language_score: number | null;
  visual_presence_score: number | null;
  production_quality_score: number | null;
  emotion_breakdown: EmotionBreakdown | null;
  gesture_analysis: Gesture[] | null;
  visual_feedback: TimestampedFeedback[] | null;
  production_details: ProductionQuality | null;
  created_at: string;
}

export interface AnalysisResponse {
  analysis_id: string;
  judge_name: string;
  overall_score: number;
  overall_grade: string | null;
  category_scores: CategoryScores;
  summary: string;
  strengths: string[];
  weaknesses: string[];
  timestamped_feedback: TimestampedFeedback[];
  specific_recommendations: string[];
  processing_time_seconds: number | null;
  token_count: number | null;
  created_at: string;
  // Visual analysis (multimodal)
  visual_analysis?: VisualAnalysisData;
  visual_analysis_details?: VisualAnalysisResponse;
}

export interface VideoDetailResponse {
  video_id: string;
  filename: string;
  original_filename: string;
  file_size_bytes: number;
  mime_type: string;

  // Metadata
  duration_seconds: number | null;
  width: number | null;
  height: number | null;
  codec: string | null;
  fps: number | null;

  // Status
  status: string;

  // Promo metadata
  promo_title: string | null;
  promo_type: string | null;
  character_type: string | null;
  promo_context: string | null;

  // Timestamps
  created_at: string;
  processing_started_at: string | null;
  processing_completed_at: string | null;

  // Related data
  transcript: TranscriptResponse | null;
  analyses: AnalysisResponse[];
}

export interface JudgeResponse {
  id: string;
  name: string;
  slug: string;
  personality_type: string;
  description: string;
  evaluation_focus: string;
  is_active: boolean;
}

export interface HealthCheckResponse {
  status: string;
  timestamp: string;
  database: string;
  redis: string;
  celery: string;
}

export interface ErrorResponse {
  detail: string;
  error_code?: string;
  timestamp: string;
}

// Helper type for upload form
export interface VideoUploadForm {
  file: File;
  promo_title?: string;
  promo_type?: string;
  character_type?: string;
  promo_context?: string;
}

// Processing status enum
export enum ProcessingStatus {
  UPLOADED = 'uploaded',
  PROCESSING = 'processing',
  COMPLETED = 'completed',
  FAILED = 'failed',
}

// Character types
export const CHARACTER_TYPES = [
  { value: 'heel', label: 'Heel (Bad Guy)' },
  { value: 'face', label: 'Face (Good Guy)' },
  { value: 'tweener', label: 'Tweener (In Between)' },
] as const;

// Promo types
export const PROMO_TYPES = [
  { value: 'heel_promo', label: 'Heel Promo' },
  { value: 'face_promo', label: 'Face Promo' },
  { value: 'challenge', label: 'Challenge' },
  { value: 'revenge', label: 'Revenge' },
  { value: 'celebration', label: 'Celebration' },
  { value: 'debut', label: 'Debut' },
  { value: 'retirement', label: 'Retirement' },
] as const;
