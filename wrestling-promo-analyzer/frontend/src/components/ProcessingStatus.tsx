/**
 * Enhanced processing status component with step-by-step progress
 */

interface ProcessingStep {
  id: string
  label: string
  activeLabel: string
  status: 'pending' | 'active' | 'completed' | 'error'
  estimatedTime?: string
}

interface ProcessingStatusProps {
  videoStatus: 'uploaded' | 'processing' | 'completed' | 'failed'
  currentStep?: number
  errorMessage?: string
}

export default function ProcessingStatus({
  videoStatus,
  currentStep = 0,
  errorMessage
}: ProcessingStatusProps) {

  // Define processing steps
  const steps: ProcessingStep[] = [
    {
      id: 'upload',
      label: 'Video uploaded',
      activeLabel: 'Uploading video',
      status: videoStatus === 'uploaded' || videoStatus === 'processing' || videoStatus === 'completed'
        ? 'completed'
        : 'pending',
      estimatedTime: '~5s'
    },
    {
      id: 'metadata',
      label: 'Metadata extracted',
      activeLabel: 'Extracting metadata',
      status: videoStatus === 'processing' && currentStep === 1
        ? 'active'
        : videoStatus === 'completed' || (videoStatus === 'processing' && currentStep > 1)
        ? 'completed'
        : videoStatus === 'failed'
        ? 'error'
        : 'pending',
      estimatedTime: '~3s'
    },
    {
      id: 'audio',
      label: 'Audio extracted',
      activeLabel: 'Extracting audio',
      status: videoStatus === 'processing' && currentStep === 2
        ? 'active'
        : videoStatus === 'completed' || (videoStatus === 'processing' && currentStep > 2)
        ? 'completed'
        : videoStatus === 'failed' && currentStep >= 2
        ? 'error'
        : 'pending',
      estimatedTime: '~10s'
    },
    {
      id: 'transcription',
      label: 'Transcription completed',
      activeLabel: 'Transcribing audio with Whisper AI',
      status: videoStatus === 'processing' && currentStep === 3
        ? 'active'
        : videoStatus === 'completed' || (videoStatus === 'processing' && currentStep > 3)
        ? 'completed'
        : videoStatus === 'failed' && currentStep >= 3
        ? 'error'
        : 'pending',
      estimatedTime: '~30s'
    },
    {
      id: 'analysis',
      label: 'Jake Morrison analysis completed',
      activeLabel: 'Jake Morrison is analyzing your promo',
      status: videoStatus === 'processing' && currentStep === 4
        ? 'active'
        : videoStatus === 'completed'
        ? 'completed'
        : videoStatus === 'failed' && currentStep >= 4
        ? 'error'
        : 'pending',
      estimatedTime: '~20s'
    },
  ]

  const getStepIcon = (step: ProcessingStep) => {
    switch (step.status) {
      case 'completed':
        return (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-green-500 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        )
      case 'active':
        return (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500 flex items-center justify-center">
            <div className="w-3 h-3 rounded-full bg-white animate-ping"></div>
          </div>
        )
      case 'error':
        return (
          <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-500 flex items-center justify-center">
            <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        )
      default:
        return (
          <div className="flex-shrink-0 w-8 h-8 rounded-full border-2 border-gray-300"></div>
        )
    }
  }

  const getStepColor = (step: ProcessingStep) => {
    switch (step.status) {
      case 'completed':
        return 'text-gray-900'
      case 'active':
        return 'text-blue-600 font-semibold'
      case 'error':
        return 'text-red-600'
      default:
        return 'text-gray-500'
    }
  }

  // Calculate progress percentage
  const completedSteps = steps.filter(s => s.status === 'completed').length
  const progressPercentage = (completedSteps / steps.length) * 100

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <div className="text-center mb-8">
        {videoStatus === 'uploaded' && (
          <>
            <div className="text-6xl mb-4">📤</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Video Uploaded Successfully
            </h3>
            <p className="text-gray-600">
              Processing will begin shortly...
            </p>
          </>
        )}

        {videoStatus === 'processing' && (
          <>
            <div className="text-6xl mb-4 animate-bounce">⚙️</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Processing Your Promo
            </h3>
            <p className="text-gray-600 mb-4">
              Jake is analyzing your promo. This usually takes less than 2 minutes.
            </p>

            {/* Progress Bar */}
            <div className="max-w-md mx-auto mb-6">
              <div className="flex justify-between text-sm text-gray-600 mb-2">
                <span>Progress</span>
                <span>{Math.round(progressPercentage)}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="h-3 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 transition-all duration-500 ease-out"
                  style={{ width: `${progressPercentage}%` }}
                />
              </div>
            </div>
          </>
        )}

        {videoStatus === 'failed' && (
          <>
            <div className="text-6xl mb-4">❌</div>
            <h3 className="text-2xl font-bold text-gray-900 mb-2">
              Processing Failed
            </h3>
            <p className="text-gray-600 mb-4">
              {errorMessage || 'Something went wrong while processing your video.'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Try Again
            </button>
          </>
        )}
      </div>

      {/* Processing Steps */}
      <div className="max-w-2xl mx-auto space-y-4">
        {steps.map((step, index) => (
          <div key={step.id} className="flex items-start space-x-4">
            {getStepIcon(step)}

            <div className="flex-1 min-w-0">
              <div className="flex items-center justify-between">
                <p className={`text-base ${getStepColor(step)}`}>
                  {step.status === 'active' ? step.activeLabel : step.label}
                </p>
                {step.estimatedTime && step.status === 'active' && (
                  <span className="text-xs text-gray-500 ml-2">{step.estimatedTime}</span>
                )}
              </div>

              {/* Show loading animation for active step */}
              {step.status === 'active' && (
                <div className="mt-2 flex items-center space-x-2">
                  <div className="flex space-x-1">
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              )}

              {/* Show error details for failed step */}
              {step.status === 'error' && errorMessage && (
                <div className="mt-2 text-sm text-red-600 bg-red-50 p-3 rounded border border-red-200">
                  {errorMessage}
                </div>
              )}
            </div>

            {/* Connector line to next step */}
            {index < steps.length - 1 && (
              <div className={`absolute left-4 ml-4 mt-8 h-8 w-0.5 ${
                step.status === 'completed' ? 'bg-green-300' : 'bg-gray-200'
              }`} style={{ marginTop: '2rem' }}></div>
            )}
          </div>
        ))}
      </div>

      {/* Estimated time remaining */}
      {videoStatus === 'processing' && (
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-500">
            Most videos complete in under 2 minutes
          </p>
        </div>
      )}
    </div>
  )
}
