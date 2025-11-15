/**
 * Error Display Component
 * Shows user-friendly error messages with suggestions and actions
 */

import { getErrorInfo } from '../utils/errorMessages'

interface ErrorDisplayProps {
  error: Error | string
  onRetry?: () => void
  onDismiss?: () => void
  className?: string
}

export default function ErrorDisplay({
  error,
  onRetry,
  onDismiss,
  className = ''
}: ErrorDisplayProps) {
  const errorInfo = getErrorInfo(error)

  const handleAction = () => {
    if (errorInfo.action) {
      errorInfo.action()
    } else if (onRetry) {
      onRetry()
    }
  }

  return (
    <div className={`bg-red-50 border-l-4 border-red-500 rounded-lg p-6 ${className}`}>
      <div className="flex items-start">
        <div className="flex-shrink-0">
          <svg
            className="h-6 w-6 text-red-500"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
        </div>

        <div className="ml-4 flex-1">
          <h3 className="text-lg font-semibold text-red-800 mb-2">
            {errorInfo.title}
          </h3>

          <p className="text-red-700 mb-3">
            {errorInfo.message}
          </p>

          {errorInfo.suggestion && (
            <div className="bg-red-100 border border-red-200 rounded-lg p-3 mb-4">
              <p className="text-sm text-red-800">
                <span className="font-semibold">💡 Suggestion: </span>
                {errorInfo.suggestion}
              </p>
            </div>
          )}

          <div className="flex items-center space-x-3">
            {(onRetry || errorInfo.action) && (
              <button
                onClick={handleAction}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors font-medium text-sm"
              >
                {errorInfo.actionLabel || 'Retry'}
              </button>
            )}

            {onDismiss && (
              <button
                onClick={onDismiss}
                className="px-4 py-2 bg-white border border-red-300 text-red-700 rounded-lg hover:bg-red-50 transition-colors font-medium text-sm"
              >
                Dismiss
              </button>
            )}
          </div>
        </div>

        {onDismiss && (
          <button
            onClick={onDismiss}
            className="flex-shrink-0 ml-4 text-red-400 hover:text-red-600 transition-colors"
          >
            <svg className="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
              <path
                fillRule="evenodd"
                d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z"
                clipRule="evenodd"
              />
            </svg>
          </button>
        )}
      </div>
    </div>
  )
}

/**
 * Compact error display for inline use
 */
export function ErrorDisplayCompact({ error, onRetry }: ErrorDisplayProps) {
  const errorInfo = getErrorInfo(error)

  return (
    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <svg className="h-5 w-5 text-red-500" fill="currentColor" viewBox="0 0 20 20">
            <path
              fillRule="evenodd"
              d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
              clipRule="evenodd"
            />
          </svg>
          <div>
            <p className="text-sm font-medium text-red-800">{errorInfo.title}</p>
            <p className="text-xs text-red-600">{errorInfo.message}</p>
          </div>
        </div>

        {onRetry && (
          <button
            onClick={onRetry}
            className="text-sm text-red-600 hover:text-red-800 font-medium"
          >
            {errorInfo.actionLabel || 'Retry'}
          </button>
        )}
      </div>
    </div>
  )
}
