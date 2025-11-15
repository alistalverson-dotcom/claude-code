interface MetricCardProps {
  label: string;
  value: number;
  icon: string;
  description?: string;
  format?: 'score' | 'percentage';
}

function MetricCard({ label, value, icon, description, format = 'score' }: MetricCardProps) {
  const displayValue = format === 'percentage' ? `${Math.round(value * 100)}%` : `${value}/100`

  // Color based on score/percentage
  const getColor = () => {
    const scoreValue = format === 'percentage' ? value * 100 : value
    if (scoreValue >= 80) return 'text-green-600 border-green-200 bg-green-50'
    if (scoreValue >= 60) return 'text-blue-600 border-blue-200 bg-blue-50'
    if (scoreValue >= 40) return 'text-orange-600 border-orange-200 bg-orange-50'
    return 'text-red-600 border-red-200 bg-red-50'
  }

  return (
    <div className={`border-2 rounded-lg p-4 transition-all hover:shadow-md ${getColor()}`}>
      <div className="flex items-center justify-between mb-2">
        <span className="text-3xl">{icon}</span>
        <span className="text-2xl font-bold">{displayValue}</span>
      </div>
      <h4 className="font-semibold text-sm mb-1">{label}</h4>
      {description && (
        <p className="text-xs opacity-75">{description}</p>
      )}
    </div>
  )
}

interface VisualPerformanceMetricsProps {
  facialExpression?: number;
  bodyLanguage?: number;
  visualPresence?: number;
  productionQuality?: number;
}

export default function VisualPerformanceMetrics({
  facialExpression,
  bodyLanguage,
  visualPresence,
  productionQuality,
}: VisualPerformanceMetricsProps) {
  const hasVisualData = facialExpression || bodyLanguage || visualPresence || productionQuality

  if (!hasVisualData) {
    return (
      <div className="text-center py-8 text-gray-500">
        <p className="text-lg">📹</p>
        <p className="mt-2">Visual analysis not available</p>
        <p className="text-sm mt-1">This video was analyzed using transcript only</p>
      </div>
    )
  }

  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
      {facialExpression !== undefined && (
        <MetricCard
          label="Facial Expressions"
          value={facialExpression}
          icon="😊"
          description="Emotion conveyance & authenticity"
        />
      )}

      {bodyLanguage !== undefined && (
        <MetricCard
          label="Body Language"
          value={bodyLanguage}
          icon="🤸"
          description="Posture & gestures"
        />
      )}

      {visualPresence !== undefined && (
        <MetricCard
          label="Visual Presence"
          value={visualPresence}
          icon="⭐"
          description="On-camera charisma"
        />
      )}

      {productionQuality !== undefined && (
        <MetricCard
          label="Production Quality"
          value={productionQuality}
          icon="🎬"
          description="Lighting & framing"
        />
      )}
    </div>
  )
}
