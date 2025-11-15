/**
 * User-friendly error messages and recovery suggestions
 */

export interface ErrorInfo {
  title: string
  message: string
  suggestion?: string
  actionLabel?: string
  action?: () => void
}

/**
 * Get user-friendly error information based on error type
 */
export function getErrorInfo(error: Error | string): ErrorInfo {
  const errorMessage = typeof error === 'string' ? error : error.message

  // Network errors
  if (errorMessage.includes('Failed to fetch') || errorMessage.includes('Network')) {
    return {
      title: 'Connection Problem',
      message: 'Unable to connect to the server. Please check your internet connection.',
      suggestion: 'Make sure you\'re connected to the internet and the server is running.',
      actionLabel: 'Retry',
    }
  }

  // File upload errors
  if (errorMessage.includes('Invalid file type')) {
    return {
      title: 'Invalid File Format',
      message: 'The file you selected is not a supported video format.',
      suggestion: 'Please upload a video in MP4, MOV, AVI, or MKV format.',
      actionLabel: 'Choose Another File',
    }
  }

  if (errorMessage.includes('File too large') || errorMessage.includes('413')) {
    return {
      title: 'File Too Large',
      message: 'Your video file exceeds the maximum upload size of 500MB.',
      suggestion: 'Try compressing your video or selecting a shorter clip. Most 5-minute promos should be under 200MB.',
      actionLabel: 'Choose Smaller File',
    }
  }

  // Video not found
  if (errorMessage.includes('Video not found') || errorMessage.includes('404')) {
    return {
      title: 'Video Not Found',
      message: 'The video you\'re looking for doesn\'t exist or has been deleted.',
      suggestion: 'It may have been removed or the link is incorrect.',
      actionLabel: 'Back to Videos',
    }
  }

  // Processing errors
  if (errorMessage.includes('Processing failed') || errorMessage.includes('failed')) {
    return {
      title: 'Processing Failed',
      message: 'We couldn\'t process your video. This might be due to a corrupt file or technical issue.',
      suggestion: 'Try uploading the video again. If the problem persists, try converting it to MP4 format.',
      actionLabel: 'Upload Again',
    }
  }

  if (errorMessage.includes('FFmpeg') || errorMessage.includes('ffprobe')) {
    return {
      title: 'Video Format Issue',
      message: 'We had trouble reading your video file.',
      suggestion: 'The video file may be corrupt or in an unusual format. Try converting it to standard MP4 with H.264 encoding.',
      actionLabel: 'Try Different File',
    }
  }

  if (errorMessage.includes('Whisper') || errorMessage.includes('transcription')) {
    return {
      title: 'Transcription Failed',
      message: 'We couldn\'t transcribe the audio from your video.',
      suggestion: 'Make sure your video has clear audio. Very quiet or heavily distorted audio may fail to transcribe.',
      actionLabel: 'Upload Again',
    }
  }

  if (errorMessage.includes('Claude') || errorMessage.includes('API')) {
    return {
      title: 'Analysis Temporarily Unavailable',
      message: 'Jake Morrison\'s analysis service is temporarily unavailable.',
      suggestion: 'This is usually temporary. Please try again in a few minutes.',
      actionLabel: 'Retry',
    }
  }

  // Authentication errors
  if (errorMessage.includes('401') || errorMessage.includes('Unauthorized')) {
    return {
      title: 'Authentication Required',
      message: 'You need to be logged in to perform this action.',
      suggestion: 'Please log in to continue.',
      actionLabel: 'Log In',
    }
  }

  // Rate limiting
  if (errorMessage.includes('429') || errorMessage.includes('rate limit')) {
    return {
      title: 'Too Many Requests',
      message: 'You\'ve uploaded too many videos in a short time.',
      suggestion: 'Please wait a few minutes before uploading another video.',
      actionLabel: 'View My Videos',
    }
  }

  // Server errors
  if (errorMessage.includes('500') || errorMessage.includes('Internal')) {
    return {
      title: 'Server Error',
      message: 'Something went wrong on our end.',
      suggestion: 'This is a technical issue. Please try again in a few minutes or contact support if it persists.',
      actionLabel: 'Retry',
    }
  }

  // Database errors
  if (errorMessage.includes('database') || errorMessage.includes('Database')) {
    return {
      title: 'Database Error',
      message: 'We\'re having trouble accessing the database.',
      suggestion: 'This is a temporary issue. Please try again in a moment.',
      actionLabel: 'Retry',
    }
  }

  // Generic error
  return {
    title: 'Something Went Wrong',
    message: errorMessage || 'An unexpected error occurred.',
    suggestion: 'Please try again. If the problem continues, contact support.',
    actionLabel: 'Retry',
  }
}

/**
 * Format error for display
 */
export function formatErrorMessage(error: unknown): string {
  if (error instanceof Error) {
    return error.message
  }
  if (typeof error === 'string') {
    return error
  }
  return 'An unexpected error occurred'
}

/**
 * Check if error is retryable
 */
export function isRetryableError(error: Error | string): boolean {
  const errorMessage = typeof error === 'string' ? error : error.message

  const retryableErrors = [
    'Network',
    'Failed to fetch',
    'timeout',
    '500',
    '502',
    '503',
    '504',
    'database',
    'Claude',
    'API',
  ]

  return retryableErrors.some(keyword => errorMessage.includes(keyword))
}

/**
 * Get appropriate HTTP status color
 */
export function getStatusColor(status: number): string {
  if (status >= 200 && status < 300) return 'text-green-600'
  if (status >= 300 && status < 400) return 'text-blue-600'
  if (status >= 400 && status < 500) return 'text-orange-600'
  if (status >= 500) return 'text-red-600'
  return 'text-gray-600'
}
