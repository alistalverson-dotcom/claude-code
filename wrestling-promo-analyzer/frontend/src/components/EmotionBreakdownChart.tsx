import type { EmotionBreakdown } from '../types'

interface EmotionBreakdownChartProps {
  emotionBreakdown: EmotionBreakdown;
}

const EMOTION_COLORS: { [key: string]: string } = {
  confident: 'bg-blue-500',
  intense: 'bg-red-500',
  focused: 'bg-purple-500',
  energetic: 'bg-orange-500',
  neutral: 'bg-gray-400',
}

const EMOTION_ICONS: { [key: string]: string } = {
  confident: '💪',
  intense: '🔥',
  focused: '🎯',
  energetic: '⚡',
  neutral: '😐',
}

export default function EmotionBreakdownChart({ emotionBreakdown }: EmotionBreakdownChartProps) {
  // Convert breakdown to sorted array
  const emotions = Object.entries(emotionBreakdown)
    .map(([emotion, value]) => ({
      emotion,
      value,
      percentage: Math.round(value * 100),
    }))
    .sort((a, b) => b.value - a.value)

  const maxValue = Math.max(...emotions.map(e => e.value))

  return (
    <div className="space-y-4">
      {emotions.map(({ emotion, value, percentage }) => (
        <div key={emotion} className="space-y-2">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-lg">{EMOTION_ICONS[emotion] || '😊'}</span>
              <span className="font-medium text-gray-700 capitalize">
                {emotion.replace('_', ' ')}
              </span>
            </div>
            <span className="text-sm font-semibold text-gray-600">
              {percentage}%
            </span>
          </div>

          {/* Progress bar */}
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-full rounded-full transition-all duration-500 ${
                EMOTION_COLORS[emotion] || 'bg-indigo-500'
              }`}
              style={{ width: `${percentage}%` }}
            />
          </div>
        </div>
      ))}

      {/* Visual legend */}
      {emotions.length === 0 && (
        <p className="text-gray-500 text-sm italic">
          No emotion data available
        </p>
      )}
    </div>
  )
}
