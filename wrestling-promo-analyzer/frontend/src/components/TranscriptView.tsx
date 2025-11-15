import { useState } from 'react'
import { formatDuration } from '../services/api'
import type { TranscriptResponse } from '../types'

interface TranscriptViewProps {
  transcript: TranscriptResponse
}

export default function TranscriptView({ transcript }: TranscriptViewProps) {
  const [viewMode, setViewMode] = useState<'full' | 'segments'>('full')

  return (
    <div>
      {/* View Toggle */}
      <div className="flex items-center space-x-4 mb-6">
        <button
          onClick={() => setViewMode('full')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            viewMode === 'full'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Full Text
        </button>
        <button
          onClick={() => setViewMode('segments')}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            viewMode === 'segments'
              ? 'bg-purple-600 text-white'
              : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
          }`}
        >
          Timestamped Segments
        </button>

        <div className="ml-auto text-sm text-gray-600">
          {transcript.word_count} words • {transcript.language.toUpperCase()}
        </div>
      </div>

      {/* Full Text View */}
      {viewMode === 'full' && (
        <div className="bg-gray-50 rounded-lg p-6">
          <p className="text-gray-800 leading-relaxed whitespace-pre-wrap">
            {transcript.full_text}
          </p>
        </div>
      )}

      {/* Segments View */}
      {viewMode === 'segments' && (
        <div className="space-y-3">
          {transcript.segments.map((segment, index) => (
            <div
              key={index}
              className="bg-gray-50 rounded-lg p-4 hover:bg-gray-100 transition-colors"
            >
              <div className="flex items-start space-x-4">
                <div className="flex-shrink-0">
                  <span className="inline-block bg-purple-100 text-purple-700 px-3 py-1 rounded-full text-xs font-mono font-semibold">
                    {formatDuration(segment.start)}
                  </span>
                </div>
                <p className="flex-1 text-gray-800 leading-relaxed">
                  {segment.text}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
