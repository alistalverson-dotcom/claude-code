import React from 'react'

interface VisualFilters {
  film_grain?: boolean
  film_grain_intensity?: string
  blur_present?: boolean
  chromatic_aberration?: boolean
  overall_sharpness?: string
  effectiveness?: string
  feedback?: string
}

interface VisualEffects {
  text_overlays?: {
    present?: boolean
    placement?: string
    quality?: string
    blocks_face?: boolean
    effectiveness?: string
  }
  glitch_effects?: boolean
  light_leaks?: boolean
  compositing?: boolean
  other_effects?: string[]
  overall_effectiveness?: string
  feedback?: string
}

interface CameraWork {
  stability?: string
  style?: string
  framing_quality?: string
  effectiveness?: string
  feedback?: string
}

interface EffectsBreakdownTableProps {
  visualFilters?: VisualFilters
  visualEffects?: VisualEffects
  cameraWork?: CameraWork
}

export default function EffectsBreakdownTable({
  visualFilters,
  visualEffects,
  cameraWork
}: EffectsBreakdownTableProps) {
  // Helper to format effectiveness
  const formatEffectiveness = (eff?: string) => {
    if (!eff) return { label: 'N/A', color: 'text-gray-600' }
    switch (eff) {
      case 'excellent':
        return { label: 'Excellent ⭐⭐⭐', color: 'text-green-600' }
      case 'good':
        return { label: 'Good ⭐⭐', color: 'text-blue-600' }
      case 'fair':
        return { label: 'Fair ⭐', color: 'text-orange-600' }
      case 'poor':
        return { label: 'Poor', color: 'text-red-600' }
      default:
        return { label: eff, color: 'text-gray-600' }
    }
  }

  // Helper to format enum values
  const formatValue = (value?: string | boolean) => {
    if (value === undefined || value === null) return 'N/A'
    if (typeof value === 'boolean') return value ? '✓' : '✗'
    return value
      .toString()
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
        <span className="mr-2">🔍</span>
        Detailed Effects Breakdown
      </h4>

      <div className="overflow-x-auto">
        <table className="w-full text-sm">
          <thead>
            <tr className="border-b-2 border-gray-200">
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Effect Category</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">Status</th>
              <th className="text-center py-3 px-4 font-semibold text-gray-700">Effectiveness</th>
              <th className="text-left py-3 px-4 font-semibold text-gray-700">Details</th>
            </tr>
          </thead>
          <tbody>
            {/* Visual Filters Section */}
            {visualFilters && (
              <>
                <tr className="bg-gray-50">
                  <td colSpan={4} className="py-2 px-4 font-semibold text-gray-900">
                    🎞️ Visual Filters
                  </td>
                </tr>

                {/* Film Grain */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Film Grain</td>
                  <td className="py-3 px-4 text-center">
                    <span className={visualFilters.film_grain ? 'text-green-600' : 'text-gray-400'}>
                      {visualFilters.film_grain ? '✓' : '✗'}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center">
                    {visualFilters.film_grain && visualFilters.film_grain_intensity && (
                      <span className="text-gray-600">{formatValue(visualFilters.film_grain_intensity)}</span>
                    )}
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {visualFilters.film_grain_intensity ? `Intensity: ${formatValue(visualFilters.film_grain_intensity)}` : ''}
                  </td>
                </tr>

                {/* Chromatic Aberration */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Chromatic Aberration</td>
                  <td className="py-3 px-4 text-center">
                    <span className={visualFilters.chromatic_aberration ? 'text-green-600' : 'text-gray-400'}>
                      {formatValue(visualFilters.chromatic_aberration)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center"></td>
                  <td className="py-3 px-4 text-gray-600">
                    {visualFilters.chromatic_aberration ? 'Color fringing detected' : ''}
                  </td>
                </tr>

                {/* Overall Sharpness */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Overall Sharpness</td>
                  <td className="py-3 px-4 text-center">✓</td>
                  <td className="py-3 px-4 text-center">
                    <span className={formatEffectiveness(visualFilters.effectiveness).color}>
                      {formatEffectiveness(visualFilters.effectiveness).label}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {formatValue(visualFilters.overall_sharpness)}
                  </td>
                </tr>
              </>
            )}

            {/* Visual Effects Section */}
            {visualEffects && (
              <>
                <tr className="bg-gray-50">
                  <td colSpan={4} className="py-2 px-4 font-semibold text-gray-900">
                    ✨ Visual Effects
                  </td>
                </tr>

                {/* Text Overlays */}
                {visualEffects.text_overlays?.present && (
                  <tr className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 pl-8">Text Overlays</td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-green-600">✓</span>
                    </td>
                    <td className="py-3 px-4 text-center">
                      <span className={formatEffectiveness(visualEffects.text_overlays.effectiveness).color}>
                        {formatEffectiveness(visualEffects.text_overlays.effectiveness).label}
                      </span>
                    </td>
                    <td className="py-3 px-4 text-gray-600">
                      {visualEffects.text_overlays.placement && `Placement: ${formatValue(visualEffects.text_overlays.placement)}`}
                      {visualEffects.text_overlays.blocks_face && ' ⚠️ Blocks face'}
                    </td>
                  </tr>
                )}

                {/* Glitch Effects */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Glitch Effects</td>
                  <td className="py-3 px-4 text-center">
                    <span className={visualEffects.glitch_effects ? 'text-green-600' : 'text-gray-400'}>
                      {formatValue(visualEffects.glitch_effects)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center"></td>
                  <td className="py-3 px-4 text-gray-600">
                    {visualEffects.glitch_effects ? 'Digital distortion present' : 'Not used'}
                  </td>
                </tr>

                {/* Light Leaks */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Light Leaks</td>
                  <td className="py-3 px-4 text-center">
                    <span className={visualEffects.light_leaks ? 'text-green-600' : 'text-gray-400'}>
                      {formatValue(visualEffects.light_leaks)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center"></td>
                  <td className="py-3 px-4 text-gray-600">
                    {visualEffects.light_leaks ? 'Lens flares/light leaks detected' : 'Not used'}
                  </td>
                </tr>

                {/* Compositing */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Green Screen/Compositing</td>
                  <td className="py-3 px-4 text-center">
                    <span className={visualEffects.compositing ? 'text-green-600' : 'text-gray-400'}>
                      {formatValue(visualEffects.compositing)}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-center"></td>
                  <td className="py-3 px-4 text-gray-600">
                    {visualEffects.compositing ? 'Composite effects detected' : 'Not used'}
                  </td>
                </tr>

                {/* Other Effects */}
                {visualEffects.other_effects && visualEffects.other_effects.length > 0 && (
                  <tr className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-3 px-4 pl-8">Other Effects</td>
                    <td className="py-3 px-4 text-center">
                      <span className="text-green-600">✓</span>
                    </td>
                    <td className="py-3 px-4 text-center"></td>
                    <td className="py-3 px-4 text-gray-600">
                      {visualEffects.other_effects.join(', ')}
                    </td>
                  </tr>
                )}
              </>
            )}

            {/* Camera Work Section */}
            {cameraWork && (
              <>
                <tr className="bg-gray-50">
                  <td colSpan={4} className="py-2 px-4 font-semibold text-gray-900">
                    🎥 Camera Work
                  </td>
                </tr>

                {/* Stability */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Camera Stability</td>
                  <td className="py-3 px-4 text-center">✓</td>
                  <td className="py-3 px-4 text-center">
                    <span className={formatEffectiveness(cameraWork.effectiveness).color}>
                      {formatEffectiveness(cameraWork.effectiveness).label}
                    </span>
                  </td>
                  <td className="py-3 px-4 text-gray-600">
                    {formatValue(cameraWork.stability)}
                  </td>
                </tr>

                {/* Style */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Camera Style</td>
                  <td className="py-3 px-4 text-center">✓</td>
                  <td className="py-3 px-4 text-center"></td>
                  <td className="py-3 px-4 text-gray-600">
                    {formatValue(cameraWork.style)}
                  </td>
                </tr>

                {/* Framing Quality */}
                <tr className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4 pl-8">Framing Quality</td>
                  <td className="py-3 px-4 text-center">✓</td>
                  <td className="py-3 px-4 text-center"></td>
                  <td className="py-3 px-4 text-gray-600">
                    {formatValue(cameraWork.framing_quality)}
                  </td>
                </tr>
              </>
            )}
          </tbody>
        </table>
      </div>

      {/* Feedback Sections */}
      <div className="mt-6 space-y-3">
        {visualFilters?.feedback && (
          <div className="p-3 bg-blue-50 rounded-lg border-l-4 border-blue-500">
            <div className="text-xs text-blue-600 font-semibold mb-1">Filters Feedback</div>
            <p className="text-sm text-blue-800">{visualFilters.feedback}</p>
          </div>
        )}

        {visualEffects?.feedback && (
          <div className="p-3 bg-purple-50 rounded-lg border-l-4 border-purple-500">
            <div className="text-xs text-purple-600 font-semibold mb-1">Effects Feedback</div>
            <p className="text-sm text-purple-800">{visualEffects.feedback}</p>
          </div>
        )}

        {cameraWork?.feedback && (
          <div className="p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
            <div className="text-xs text-green-600 font-semibold mb-1">Camera Work Feedback</div>
            <p className="text-sm text-green-800">{cameraWork.feedback}</p>
          </div>
        )}
      </div>
    </div>
  )
}
