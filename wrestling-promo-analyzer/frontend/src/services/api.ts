/**
 * API Client for Wrestling Promo Analyzer
 * Handles all HTTP requests to the backend
 */

import type {
  VideoUploadResponse,
  VideoDetailResponse,
  VideoListItem,
  JudgeResponse,
  HealthCheckResponse,
  VideoUploadForm,
} from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

class ApiError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    public detail: string
  ) {
    super(`API Error ${status}: ${detail}`);
    this.name = 'ApiError';
  }
}

/**
 * Handle API response and errors
 */
async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    let detail = response.statusText;
    try {
      const errorData = await response.json();
      detail = errorData.detail || detail;
    } catch {
      // If response is not JSON, use statusText
    }
    throw new ApiError(response.status, response.statusText, detail);
  }

  // Handle 204 No Content
  if (response.status === 204) {
    return null as T;
  }

  return response.json();
}

/**
 * Upload a video file for analysis
 */
export async function uploadVideo(
  formData: VideoUploadForm,
  onProgress?: (progress: number) => void
): Promise<VideoUploadResponse> {
  const form = new FormData();
  form.append('file', formData.file);

  if (formData.promo_title) {
    form.append('promo_title', formData.promo_title);
  }
  if (formData.promo_type) {
    form.append('promo_type', formData.promo_type);
  }
  if (formData.character_type) {
    form.append('character_type', formData.character_type);
  }
  if (formData.promo_context) {
    form.append('promo_context', formData.promo_context);
  }
  if (formData.judge_slug) {
    form.append('judge_slug', formData.judge_slug);
  }

  // Create XMLHttpRequest for upload progress tracking
  return new Promise((resolve, reject) => {
    const xhr = new XMLHttpRequest();

    xhr.upload.addEventListener('progress', (e) => {
      if (e.lengthComputable && onProgress) {
        const progress = (e.loaded / e.total) * 100;
        onProgress(progress);
      }
    });

    xhr.addEventListener('load', () => {
      if (xhr.status >= 200 && xhr.status < 300) {
        try {
          const data = JSON.parse(xhr.responseText);
          resolve(data);
        } catch (error) {
          reject(new Error('Failed to parse response'));
        }
      } else {
        let detail = xhr.statusText;
        try {
          const errorData = JSON.parse(xhr.responseText);
          detail = errorData.detail || detail;
        } catch {
          // Use statusText if response is not JSON
        }
        reject(new ApiError(xhr.status, xhr.statusText, detail));
      }
    });

    xhr.addEventListener('error', () => {
      reject(new Error('Network error during upload'));
    });

    xhr.open('POST', `${API_BASE_URL}/api/v1/videos/upload`);
    xhr.send(form);
  });
}

/**
 * Get video details by ID
 */
export async function getVideo(videoId: string): Promise<VideoDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/videos/${videoId}`);
  return handleResponse<VideoDetailResponse>(response);
}

/**
 * List all videos with optional filtering
 */
export async function listVideos(params?: {
  skip?: number;
  limit?: number;
  status?: string;
}): Promise<VideoListItem[]> {
  const queryParams = new URLSearchParams();

  if (params?.skip !== undefined) {
    queryParams.append('skip', params.skip.toString());
  }
  if (params?.limit !== undefined) {
    queryParams.append('limit', params.limit.toString());
  }
  if (params?.status) {
    queryParams.append('status', params.status);
  }

  const url = `${API_BASE_URL}/api/v1/videos${
    queryParams.toString() ? `?${queryParams.toString()}` : ''
  }`;

  const response = await fetch(url);
  return handleResponse<VideoListItem[]>(response);
}

/**
 * Delete a video
 */
export async function deleteVideo(videoId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/videos/${videoId}`, {
    method: 'DELETE',
  });
  return handleResponse<void>(response);
}

/**
 * List all judges
 */
export async function listJudges(activeOnly: boolean = true): Promise<JudgeResponse[]> {
  const url = `${API_BASE_URL}/api/v1/judges${activeOnly ? '?active_only=true' : ''}`;
  const response = await fetch(url);
  return handleResponse<JudgeResponse[]>(response);
}

/**
 * Get judge by slug
 */
export async function getJudge(slug: string): Promise<JudgeResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/judges/${slug}`);
  return handleResponse<JudgeResponse>(response);
}

/**
 * Health check
 */
export async function healthCheck(): Promise<HealthCheckResponse> {
  const response = await fetch(`${API_BASE_URL}/health`);
  return handleResponse<HealthCheckResponse>(response);
}

/**
 * Poll video status until processing is complete
 */
export async function pollVideoStatus(
  videoId: string,
  onUpdate?: (video: VideoDetailResponse) => void,
  interval: number = 2000,
  maxAttempts: number = 300 // 10 minutes at 2s intervals
): Promise<VideoDetailResponse> {
  let attempts = 0;

  return new Promise((resolve, reject) => {
    const poll = async () => {
      try {
        const video = await getVideo(videoId);

        if (onUpdate) {
          onUpdate(video);
        }

        if (video.status === 'completed' || video.status === 'failed') {
          resolve(video);
          return;
        }

        attempts++;
        if (attempts >= maxAttempts) {
          reject(new Error('Polling timeout: Video processing took too long'));
          return;
        }

        setTimeout(poll, interval);
      } catch (error) {
        reject(error);
      }
    };

    poll();
  });
}

/**
 * Format file size in human-readable format
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Format duration in MM:SS format
 */
export function formatDuration(seconds: number): string {
  const mins = Math.floor(seconds / 60);
  const secs = Math.floor(seconds % 60);
  return `${mins}:${secs.toString().padStart(2, '0')}`;
}

/**
 * Get grade color for styling
 */
export function getGradeColor(grade: string): string {
  const gradeMap: { [key: string]: string } = {
    'A+': 'text-green-600',
    A: 'text-green-600',
    'A-': 'text-green-500',
    'B+': 'text-blue-600',
    B: 'text-blue-500',
    'B-': 'text-blue-400',
    'C+': 'text-yellow-600',
    C: 'text-yellow-500',
    'C-': 'text-yellow-400',
    D: 'text-orange-500',
    F: 'text-red-600',
  };

  return gradeMap[grade] || 'text-gray-600';
}

/**
 * Get score color for category scores
 */
export function getScoreColor(score: number): string {
  if (score >= 90) return 'text-green-600';
  if (score >= 80) return 'text-blue-600';
  if (score >= 70) return 'text-yellow-600';
  if (score >= 60) return 'text-orange-500';
  return 'text-red-600';
}

export { ApiError };
