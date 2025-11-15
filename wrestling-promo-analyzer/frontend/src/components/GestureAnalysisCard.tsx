import type { Gesture } from '../types'

interface GestureAnalysisCardProps {
  gestures: Gesture[];
}

const GESTURE_ICONS: { [key: string]: string } = {
  pointing: '☝️',
  open_palm: '✋',
  fist: '✊',
  peace_sign: '✌️',
  thumbs_up: '👍',
  hand_raise: '🙋',
}

const GESTURE_LABELS: { [key: string]: string } = {
  pointing: 'Pointing',
  open_palm: 'Open Palm',
  fist: 'Fist',
  peace_sign: 'Peace Sign',
  thumbs_up: 'Thumbs Up',
  hand_raise: 'Hand Raise',
}

export default function GestureAnalysisCard({ gestures }: GestureAnalysisCardProps) {
  if (!gestures || gestures.length === 0) {
    return (
      <div className="text-gray-500 text-sm italic">
        No gesture data available
      </div>
    )
  }

  return (
    <div className="space-y-3">
      {gestures.map((gesture, index) => {
        const effectiveness = Math.round(gesture.effectiveness * 100)
        const effectivenessColor =
          effectiveness >= 80
            ? 'text-green-600 bg-green-50'
            : effectiveness >= 60
            ? 'text-blue-600 bg-blue-50'
            : 'text-orange-600 bg-orange-50'

        return (
          <div
            key={index}
            className="flex items-center justify-between p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
          >
            <div className="flex items-center space-x-3">
              <span className="text-2xl">
                {GESTURE_ICONS[gesture.gesture] || '👋'}
              </span>
              <div>
                <p className="font-medium text-gray-900">
                  {GESTURE_LABELS[gesture.gesture] || gesture.gesture.replace('_', ' ')}
                </p>
                <p className="text-sm text-gray-600">
                  Used {gesture.count} time{gesture.count !== 1 ? 's' : ''}
                </p>
              </div>
            </div>

            <div className={`px-3 py-1 rounded-full text-sm font-semibold ${effectivenessColor}`}>
              {effectiveness}% effective
            </div>
          </div>
        )
      })}
    </div>
  )
}
