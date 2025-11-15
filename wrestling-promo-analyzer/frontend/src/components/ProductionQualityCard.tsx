import type { ProductionQuality } from '../types'

interface ProductionQualityCardProps {
  productionDetails: ProductionQuality;
}

interface QualityMetric {
  label: string;
  value: number;
  icon: string;
}

export default function ProductionQualityCard({ productionDetails }: ProductionQualityCardProps) {
  const metrics: QualityMetric[] = []

  if (productionDetails.lighting !== undefined) {
    metrics.push({
      label: 'Lighting',
      value: productionDetails.lighting,
      icon: '💡',
    })
  }

  if (productionDetails.framing !== undefined) {
    metrics.push({
      label: 'Framing',
      value: productionDetails.framing,
      icon: '🎞️',
    })
  }

  if (productionDetails.background !== undefined) {
    metrics.push({
      label: 'Background',
      value: productionDetails.background,
      icon: '🖼️',
    })
  }

  if (metrics.length === 0) {
    return (
      <div className="text-gray-500 text-sm italic">
        No production quality data available
      </div>
    )
  }

  const getScoreColor = (score: number) => {
    const percentage = score * 100
    if (percentage >= 80) return 'text-green-600'
    if (percentage >= 60) return 'text-blue-600'
    if (percentage >= 40) return 'text-orange-600'
    return 'text-red-600'
  }

  const getScoreLabel = (score: number) => {
    const percentage = score * 100
    if (percentage >= 90) return 'Excellent'
    if (percentage >= 75) return 'Good'
    if (percentage >= 60) return 'Fair'
    if (percentage >= 40) return 'Needs Improvement'
    return 'Poor'
  }

  return (
    <div className="space-y-4">
      {metrics.map(({ label, value, icon }) => {
        const percentage = Math.round(value * 100)
        const scoreLabel = getScoreLabel(value)
        const scoreColor = getScoreColor(value)

        return (
          <div key={label} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg">
            <div className="flex items-center space-x-3">
              <span className="text-2xl">{icon}</span>
              <div>
                <p className="font-medium text-gray-900">{label}</p>
                <p className={`text-sm font-semibold ${scoreColor}`}>
                  {scoreLabel}
                </p>
              </div>
            </div>

            <div className="text-right">
              <div className={`text-2xl font-bold ${scoreColor}`}>
                {percentage}%
              </div>
            </div>
          </div>
        )
      })}

      {/* Overall quality if available */}
      {productionDetails.overall !== undefined && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex items-center justify-between">
            <span className="font-semibold text-gray-700">Overall Quality</span>
            <span className={`text-xl font-bold ${getScoreColor(productionDetails.overall)}`}>
              {Math.round(productionDetails.overall * 100)}%
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
