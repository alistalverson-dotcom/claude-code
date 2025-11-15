import React from 'react'
import type { MusicAnalysis } from '../types'

interface MusicAnalysisCardProps {
  musicAnalysis?: MusicAnalysis
}

export default function MusicAnalysisCard({ musicAnalysis }: MusicAnalysisCardProps) {
  if (!musicAnalysis || !musicAnalysis.music_detected) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
        <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
          <span className="mr-3">🎵</span>
          Background Music Analysis
        </h3>
        <div className="text-center py-8 text-gray-500">
          <p className="text-lg">🔇</p>
          <p className="mt-2">No background music detected</p>
          <p className="text-sm mt-1">This promo uses speech only</p>
        </div>
      </div>
    )
  }

  const {
    music_effectiveness,
    music_characteristics,
    mixing_quality,
    strengths,
    weaknesses,
    recommendations,
    alternative_music_suggestions,
    overall_music_feedback
  } = musicAnalysis

  // Get score color
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

  const formatValue = (value?: string | boolean) => {
    if (value === undefined || value === null) return 'N/A'
    if (typeof value === 'boolean') return value ? 'Yes' : 'No'
    return value
      .toString()
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ')
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <h3 className="text-2xl font-bold text-gray-900 flex items-center">
          <span className="mr-3">🎵</span>
          Background Music Analysis
        </h3>

        {music_effectiveness?.overall_score !== undefined && (
          <div className={`border-2 rounded-lg px-6 py-3 ${getScoreColor(music_effectiveness.overall_score)}`}>
            <div className="text-3xl font-bold">{music_effectiveness.overall_score}/100</div>
            <div className="text-sm font-semibold">{getScoreLabel(music_effectiveness.overall_score)}</div>
          </div>
        )}
      </div>

      {/* Overall Feedback */}
      {overall_music_feedback && (
        <div className="mb-6 p-4 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2 flex items-center">
            <span className="mr-2">💬</span>
            Overall Assessment
          </h4>
          <p className="text-gray-700 leading-relaxed">{overall_music_feedback}</p>
        </div>
      )}

      {/* Music Characteristics */}
      {music_characteristics && (
        <div className="mb-6 bg-purple-50 rounded-lg p-4 border-2 border-purple-200">
          <h4 className="font-semibold text-purple-900 mb-3 flex items-center">
            <span className="mr-2">🎼</span>
            Music Characteristics
          </h4>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {music_characteristics.tempo_bpm && (
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-purple-600 mb-1">Tempo</div>
                <div className="text-sm font-semibold text-gray-900">
                  {music_characteristics.tempo_bpm} BPM
                </div>
                <div className="text-xs text-gray-600">
                  {formatValue(music_characteristics.tempo_category)}
                </div>
              </div>
            )}

            {music_characteristics.intensity_level && (
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-purple-600 mb-1">Intensity</div>
                <div className="text-sm font-semibold text-gray-900">
                  {formatValue(music_characteristics.intensity_level)}
                </div>
                {music_characteristics.intensity_score !== undefined && (
                  <div className="text-xs text-gray-600">
                    {Math.round(music_characteristics.intensity_score * 100)}%
                  </div>
                )}
              </div>
            )}

            {music_characteristics.key_type && (
              <div className="bg-white rounded-lg p-3">
                <div className="text-xs text-purple-600 mb-1">Key</div>
                <div className="text-sm font-semibold text-gray-900">
                  {formatValue(music_characteristics.key_type)}
                </div>
                <div className="text-xs text-gray-600">
                  {formatValue(music_characteristics.emotional_tone)}
                </div>
              </div>
            )}
          </div>

          {music_characteristics.has_dynamic_builds && (
            <div className="mt-3 flex items-center text-sm text-purple-800">
              <span className="mr-2">✓</span>
              <span>Dynamic builds detected - Music intensifies at key moments</span>
            </div>
          )}
        </div>
      )}

      {/* Mixing Quality */}
      {mixing_quality && (
        <div className="mb-6 bg-blue-50 rounded-lg p-4 border-2 border-blue-200">
          <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
            <span className="mr-2">🎚️</span>
            Mixing Quality
          </h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-white rounded-lg p-3">
              <div className="text-xs text-blue-600 mb-2">Volume Balance</div>
              <div className="text-sm font-semibold text-gray-900 mb-1">
                {formatValue(mixing_quality.balance_quality)}
              </div>
              {mixing_quality.balance_ratio !== undefined && (
                <div className="text-xs text-gray-600">
                  Ratio: {mixing_quality.balance_ratio.toFixed(2)}
                  {mixing_quality.music_too_loud && ' ⚠️ Music too loud'}
                  {mixing_quality.music_too_quiet && ' ⚠️ Music too quiet'}
                </div>
              )}
            </div>

            <div className="bg-white rounded-lg p-3">
              <div className="text-xs text-blue-600 mb-2">Ducking</div>
              <div className="text-sm font-semibold text-gray-900">
                {mixing_quality.ducking_detected ? '✓ Detected' : '✗ Not Detected'}
              </div>
              <div className="text-xs text-gray-600">
                {mixing_quality.ducking_detected
                  ? 'Music lowers during speech'
                  : 'No ducking detected'}
              </div>
            </div>
          </div>

          {mixing_quality.clipping_detected && (
            <div className="mt-3 p-2 bg-red-100 border border-red-300 rounded text-sm text-red-800">
              <span className="font-semibold">⚠️ Audio Issue:</span> Clipping/distortion detected
            </div>
          )}
        </div>
      )}

      {/* Character/Promo Fit */}
      {music_effectiveness && (
        <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
          <div className={`rounded-lg p-4 border-2 ${
            music_effectiveness.fits_character
              ? 'bg-green-50 border-green-200'
              : 'bg-orange-50 border-orange-200'
          }`}>
            <div className="flex items-center mb-2">
              <span className="text-2xl mr-2">
                {music_effectiveness.fits_character ? '✓' : '✗'}
              </span>
              <span className="font-semibold">Character Alignment</span>
            </div>
            <p className="text-sm">
              {music_effectiveness.fits_character
                ? 'Music style matches character type'
                : 'Music style conflicts with character'}
            </p>
          </div>

          <div className={`rounded-lg p-4 border-2 ${
            music_effectiveness.enhances_performance
              ? 'bg-green-50 border-green-200'
              : 'bg-orange-50 border-orange-200'
          }`}>
            <div className="flex items-center mb-2">
              <span className="text-2xl mr-2">
                {music_effectiveness.enhances_performance ? '✓' : '✗'}
              </span>
              <span className="font-semibold">Performance Enhancement</span>
            </div>
            <p className="text-sm">
              {music_effectiveness.enhances_performance
                ? 'Music amplifies emotional impact'
                : 'Music distracts from performance'}
            </p>
          </div>
        </div>
      )}

      {/* Strengths & Weaknesses */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
        {/* Strengths */}
        {strengths && strengths.length > 0 && (
          <div className="bg-green-50 rounded-lg p-4 border-2 border-green-200">
            <h4 className="font-semibold text-green-900 mb-3 flex items-center">
              <span className="mr-2">✅</span>
              What's Working
            </h4>
            <ul className="space-y-2">
              {strengths.map((strength, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-green-600 mr-2 mt-1">•</span>
                  <span className="text-green-800 text-sm">{strength}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {/* Weaknesses */}
        {weaknesses && weaknesses.length > 0 && (
          <div className="bg-orange-50 rounded-lg p-4 border-2 border-orange-200">
            <h4 className="font-semibold text-orange-900 mb-3 flex items-center">
              <span className="mr-2">⚠️</span>
              Areas to Improve
            </h4>
            <ul className="space-y-2">
              {weaknesses.map((weakness, index) => (
                <li key={index} className="flex items-start">
                  <span className="text-orange-600 mr-2 mt-1">•</span>
                  <span className="text-orange-800 text-sm">{weakness}</span>
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Recommendations */}
      {recommendations && recommendations.length > 0 && (
        <div className="mb-6 bg-indigo-50 rounded-lg p-4 border-2 border-indigo-200">
          <h4 className="font-semibold text-indigo-900 mb-3 flex items-center">
            <span className="mr-2">🎯</span>
            Music Recommendations
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

      {/* Alternative Music Suggestions */}
      {alternative_music_suggestions && alternative_music_suggestions.length > 0 && (
        <div className="bg-purple-50 rounded-lg p-4 border-2 border-purple-200">
          <h4 className="font-semibold text-purple-900 mb-3 flex items-center">
            <span className="mr-2">💡</span>
            Alternative Music Styles
          </h4>
          <ul className="space-y-2">
            {alternative_music_suggestions.map((suggestion, index) => (
              <li key={index} className="flex items-start">
                <span className="text-purple-600 mr-2 mt-1">♪</span>
                <span className="text-purple-800 text-sm">{suggestion}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
