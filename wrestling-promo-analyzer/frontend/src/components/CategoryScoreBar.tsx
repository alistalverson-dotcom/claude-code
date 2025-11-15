import { getScoreColor } from '../services/api'

interface CategoryScoreBarProps {
  name: string
  score: number
  description: string
}

export default function CategoryScoreBar({ name, score, description }: CategoryScoreBarProps) {
  return (
    <div>
      <div className="flex justify-between items-center mb-2">
        <div>
          <h4 className="font-semibold text-gray-900">{name}</h4>
          <p className="text-sm text-gray-600">{description}</p>
        </div>
        <span className={`text-2xl font-bold ${getScoreColor(score)}`}>
          {score}
        </span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div
          className={`h-3 rounded-full transition-all duration-500 ${
            score >= 90
              ? 'bg-green-500'
              : score >= 80
              ? 'bg-blue-500'
              : score >= 70
              ? 'bg-yellow-500'
              : score >= 60
              ? 'bg-orange-500'
              : 'bg-red-500'
          }`}
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  )
}
