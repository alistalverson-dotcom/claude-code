import React from 'react'

interface ColorGrading {
  style?: string
  color_palette?: string
  color_temperature?: string
  dominant_colors?: string[]
  saturation_level?: number
  contrast_ratio?: number
  vignette_detected?: boolean
  vignette_strength?: number
  effectiveness?: string
  feedback?: string
}

interface ColorGradingVisualizationProps {
  colorGrading?: ColorGrading
}

export default function ColorGradingVisualization({ colorGrading }: ColorGradingVisualizationProps) {
  if (!colorGrading) {
    return null
  }

  const {
    style,
    color_palette,
    color_temperature,
    dominant_colors,
    saturation_level,
    contrast_ratio,
    vignette_detected,
    vignette_strength,
    effectiveness,
    feedback
  } = colorGrading

  // Format style name
  const formatStyleName = (style?: string) => {
    if (!style) return 'Natural'
    return style
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  // Get effectiveness color
  const getEffectivenessColor = (eff?: string) => {
    switch (eff) {
      case 'excellent': return 'text-green-600 bg-green-50'
      case 'good': return 'text-blue-600 bg-blue-50'
      case 'fair': return 'text-orange-600 bg-orange-50'
      case 'poor': return 'text-red-600 bg-red-50'
      default: return 'text-gray-600 bg-gray-50'
    }
  }

  // Get progress bar color
  const getProgressColor = (value: number) => {
    if (value >= 0.8) return 'bg-green-500'
    if (value >= 0.6) return 'bg-blue-500'
    if (value >= 0.4) return 'bg-orange-500'
    return 'bg-red-500'
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      {/* Header */}
      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span className="mr-2">🎨</span>
        Color Grading Analysis
      </h4>

      {/* Style and Palette */}
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500 mb-1">Grading Style</div>
          <div className="text-sm font-semibold text-gray-900">{formatStyleName(style)}</div>
        </div>

        <div className="bg-gray-50 rounded-lg p-3">
          <div className="text-xs text-gray-500 mb-1">Color Palette</div>
          <div className="text-sm font-semibold text-gray-900">{formatStyleName(color_palette)}</div>
        </div>

        {color_temperature && (
          <div className="bg-gray-50 rounded-lg p-3">
            <div className="text-xs text-gray-500 mb-1">Temperature</div>
            <div className="text-sm font-semibold text-gray-900">{formatStyleName(color_temperature)}</div>
          </div>
        )}

        {effectiveness && (
          <div className={`rounded-lg p-3 ${getEffectivenessColor(effectiveness)}`}>
            <div className="text-xs opacity-75 mb-1">Effectiveness</div>
            <div className="text-sm font-semibold">{formatStyleName(effectiveness)}</div>
          </div>
        )}
      </div>

      {/* Dominant Colors */}
      {dominant_colors && dominant_colors.length > 0 && (
        <div className="mb-4">
          <div className="text-xs text-gray-500 mb-2">Dominant Colors</div>
          <div className="flex gap-2">
            {dominant_colors.slice(0, 5).map((color, index) => (
              <div key={index} className="flex-1">
                <div
                  className="h-12 rounded-md border-2 border-gray-200 shadow-sm"
                  style={{ backgroundColor: color }}
                  title={color}
                />
                <div className="text-xs text-center text-gray-500 mt-1 font-mono">
                  {color}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Saturation Level */}
      {saturation_level !== undefined && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-gray-500">Saturation</span>
            <span className="text-xs font-semibold text-gray-700">{Math.round(saturation_level * 100)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${getProgressColor(saturation_level)}`}
              style={{ width: `${saturation_level * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Contrast Ratio */}
      {contrast_ratio !== undefined && (
        <div className="mb-4">
          <div className="flex justify-between items-center mb-2">
            <span className="text-xs text-gray-500">Contrast</span>
            <span className="text-xs font-semibold text-gray-700">
              {contrast_ratio.toFixed(1)}/5.0
            </span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${getProgressColor(contrast_ratio / 5.0)}`}
              style={{ width: `${(contrast_ratio / 5.0) * 100}%` }}
            />
          </div>
        </div>
      )}

      {/* Vignette */}
      {vignette_detected && (
        <div className="mb-4 p-3 bg-purple-50 rounded-lg border border-purple-200">
          <div className="flex justify-between items-center">
            <div className="flex items-center">
              <span className="mr-2">🔦</span>
              <span className="text-sm font-semibold text-purple-900">Vignette Effect</span>
            </div>
            {vignette_strength !== undefined && (
              <span className="text-xs text-purple-700">
                {Math.round(vignette_strength * 100)}% intensity
              </span>
            )}
          </div>
        </div>
      )}

      {/* Feedback */}
      {feedback && (
        <div className="mt-4 p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
          <p className="text-sm text-blue-800 leading-relaxed">{feedback}</p>
        </div>
      )}
    </div>
  )
}
