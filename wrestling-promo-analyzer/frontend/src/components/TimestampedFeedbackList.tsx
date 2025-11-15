import type { TimestampedFeedback } from '../types'

interface TimestampedFeedbackListProps {
  feedback: TimestampedFeedback[]
}

export default function TimestampedFeedbackList({ feedback }: TimestampedFeedbackListProps) {
  const getTypeColor = (type: string) => {
    switch (type) {
      case 'positive':
        return 'bg-green-50 border-green-200 text-green-800'
      case 'negative':
        return 'bg-orange-50 border-orange-200 text-orange-800'
      default:
        return 'bg-blue-50 border-blue-200 text-blue-800'
    }
  }

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'positive':
        return '✓'
      case 'negative':
        return '!'
      default:
        return '→'
    }
  }

  return (
    <div className="space-y-4">
      {feedback.map((item, index) => (
        <div
          key={index}
          className={`border rounded-lg p-4 ${getTypeColor(item.type)}`}
        >
          <div className="flex items-start space-x-3">
            <div className="flex-shrink-0">
              <span className="inline-flex items-center justify-center w-8 h-8 rounded-full bg-white font-bold text-sm">
                {getTypeIcon(item.type)}
              </span>
            </div>

            <div className="flex-1">
              <div className="flex items-center space-x-2 mb-1">
                <span className="font-mono text-sm font-semibold">
                  {item.timestamp}
                </span>
                <span className="text-xs uppercase font-medium opacity-75">
                  {item.type}
                </span>
              </div>
              <p className="text-sm leading-relaxed">{item.comment}</p>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}
