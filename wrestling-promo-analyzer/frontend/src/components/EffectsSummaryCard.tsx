import React from 'react'

interface EffectsAnalysis {
  production_technique_score?: number
  effects_summary?: string
  effectiveness_feedback?: string
  recommendations?: string[]
  effects_working_well?: string[]
  effects_to_reduce?: string[]
  effects_to_add?: string[]
}

interface EffectsSummaryCardProps {
  effectsAnalysis?: EffectsAnalysis
}

export default function EffectsSummaryCard({ effectsAnalysis }: EffectsSummaryCardProps) {
  if (!effectsAnalysis) {
    return null
  }

  const {
    production_technique_score,
    effects_summary,
    effectiveness_feedback,
    effects_working_well,
    effects_to_reduce,
    effects_to_add,
    recommendations
  } = effectsAnalysis

  // Determine score color
  const getScoreColor = (score?: number) => {
    if (!score) return 'text-gray-600 border-gray-200'
    if (score >= 80) return 'text-green-600 border-green-200 bg-green-50'
    if (score >= 60) return 'text-blue-600 border-blue-200 bg-blue-50'
    if (score >= 40) return 'text-orange-600 border-orange-200 bg-orange-50'
    return 'text-red-600 border-red-200 bg-red-50'
  }

  const getScoreLabel = (score?: number) => {
    if (!score) return 'N/A'
    if (score >= 80) return 'Excellent'
    if (score >= 60) return 'Good'
    if (score >= 40) return 'Fair'
    return 'Needs Work'
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-bold text-gray-900">
          🎬 Production Techniques & Visual Effects
        </h3>

        {production_technique_score !== undefined && (
          <div className={`border-2 rounded-lg px-6 py-3 ${getScoreColor(production_technique_score)}`}>
            <div className="text-3xl font-bold">{production_technique_score}/100</div>
            <div className="text-sm font-semibold">{getScoreLabel(production_technique_score)}</div>
          </div>
        )}
      </div>

      {/* Effects Summary */}
      {effects_summary && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
            <span className="mr-2">📊</span>
            Effects Overview
          </h4>
          <p className="text-gray-700 leading-relaxed">{effects_summary}</p>
        </div>
      )}

      {/* Effectiveness Feedback */}
      {effectiveness_feedback && (
        <div className="mb-6 p-4 bg-blue-50 rounded-lg border-l-4 border-blue-500">
          <h4 className="font-semibold text-blue-900 mb-2 flex items-center">
            <span className="mr-2">💬</span>
            Impact Analysis
          </h4>
          <p className="text-blue-800 leading-relaxed">{effectiveness_feedback}</p>
        </div>
      )}

      {/* Two-column layout for strengths/weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Effects Working Well */}
        {effects_working_well && effects_working_well.length > 0 && (
          <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
            <h4 className="font-semibold text-green-900 mb-3 flex items-center">
              <span className="mr-2">✅</span>
              Working Well
            </h4>
            <ul className="space-y-2">
              {effects_working_well.map((effect, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-green-600 mr-2 mt-1">•</span>
                  <span className="text-green-800 text-sm">{effect}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Effects to Reduce */}
        {effects_to_reduce && effects_to_reduce.length > 0 && (
          <div className="bg-orange-50 rounded-lg p-4 border-2 border-orange-200">
            <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
              <span className="mr-2">⚠️</span>
              Could Improve
            </h4>
            <ul className="space-y-2">
              {effects_to_reduce.map((effect, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-orange-600 mr-2 mt-1">•</span>
                  <span className="text-orange-800 text-sm">{effect}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Effects to Add */}
      {effects_to_add && effects_to_add.length > 0 && (
        <div className="mb-6 bg-purple-50 rounded-lg p-4 border-2 border-purple-200">
          <h4 className="font-semibold text-purple-900 mb-3 flex items-center">
            <span className="mr-2">💡</span>
            Suggested Additions
          </h4>
          <ul className="space-y-2">
            {effects_to_add.map((effect, index) => (
              <li key={index} className="flex items-start">
                <span className="text-purple-600 mr-2 mt-1">+</span>
                <span className="text-purple-800 text-sm">{effect}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="bg-indigo-50 rounded-lg p-4 border-2 border-indigo-200">
          <h4 className="font-semibold text-indigo-900 mb-3 flex items-center">
            <span className="mr-2">🎯</span>
            Production Recommendations
          </h4>
          <ul className="space-y-2">
            {recommendations.map((rec, index) => (
              <li key={index} className="flex items-start">
                <span className="text-indigo-600 mr-2 mt-1 font-bold">{index + 1}.</span>
                <span className="text-indigo-800 text-sm">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
