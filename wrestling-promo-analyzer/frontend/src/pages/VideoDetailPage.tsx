import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getVideo, pollVideoStatus, formatDuration, getGradeColor, getScoreColor } from '../services/api'
import type { VideoDetailResponse, AnalysisResponse } from '../types'
import CategoryScoreBar from '../components/CategoryScoreBar'
import TimestampedFeedbackList from '../components/TimestampedFeedbackList'
import TranscriptView from '../components/TranscriptView'

export default function VideoDetailPage() {
  const { videoId } = useParams<{ videoId: string }>()
  const [video, setVideo] = useState<VideoDetailResponse | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [polling, setPolling] = useState(false)

  useEffect(() => {
    if (videoId) {
      loadVideo(videoId)
    }
  }, [videoId])

  const loadVideo = async (id: string) => {
    try {
      setLoading(true)
      setError(null)
      const data = await getVideo(id)
      setVideo(data)

      // If processing, start polling
      if (data.status === 'processing' || data.status === 'uploaded') {
        startPolling(id)
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load video')
    } finally {
      setLoading(false)
    }
  }

  const startPolling = async (id: string) => {
    if (polling) return

    setPolling(true)
    try {
      await pollVideoStatus(
        id,
        (updatedVideo) => {
          setVideo(updatedVideo)
        },
        3000 // Poll every 3 seconds
      )
    } catch (err) {
      console.error('Polling error:', err)
    } finally {
      setPolling(false)
    }
  }

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto text-center py-12">
        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600"></div>
        <p className="mt-4 text-gray-600">Loading video...</p>
      </div>
    )
  }

  if (error || !video) {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-red-50 border border-red-200 text-red-800 px-6 py-4 rounded-lg">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error || 'Video not found'}</p>
          <Link to="/videos" className="text-sm underline mt-2 inline-block">
            Back to videos
          </Link>
        </div>
      </div>
    )
  }

  const analysis = video.analyses && video.analyses.length > 0 ? video.analyses[0] : null

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-6">
        <Link to="/videos" className="text-purple-600 hover:text-purple-700 font-medium mb-4 inline-block">
          ← Back to videos
        </Link>
        <h2 className="text-4xl font-bold text-gray-900 mb-2">
          {video.promo_title || video.original_filename}
        </h2>
        <p className="text-gray-600">{video.original_filename}</p>
      </div>

      {/* Processing Status */}
      {video.status !== 'completed' && (
        <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
          <div className="text-center">
            {video.status === 'uploaded' && (
              <>
                <div className="text-6xl mb-4">📤</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Video Uploaded
                </h3>
                <p className="text-gray-600">
                  Processing will begin shortly...
                </p>
              </>
            )}

            {video.status === 'processing' && (
              <>
                <div className="text-6xl mb-4 animate-pulse">⏳</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Processing Your Promo
                </h3>
                <p className="text-gray-600 mb-6">
                  Jake is analyzing your promo. This usually takes less than 2 minutes.
                </p>

                {/* Processing Steps */}
                <div className="max-w-md mx-auto space-y-3">
                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-white text-xs">
                      ✓
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-sm font-medium text-gray-900">Video uploaded</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center">
                      <div className="w-2 h-2 rounded-full bg-white animate-ping"></div>
                    </div>
                    <div className="flex-1 text-left">
                      <p className="text-sm font-medium text-gray-900">Extracting audio & transcribing</p>
                    </div>
                  </div>

                  <div className="flex items-center space-x-3">
                    <div className="flex-shrink-0 w-6 h-6 rounded-full border-2 border-gray-300"></div>
                    <div className="flex-1 text-left">
                      <p className="text-sm text-gray-600">Jake Morrison analysis</p>
                    </div>
                  </div>
                </div>
              </>
            )}

            {video.status === 'failed' && (
              <>
                <div className="text-6xl mb-4">❌</div>
                <h3 className="text-2xl font-bold text-gray-900 mb-2">
                  Processing Failed
                </h3>
                <p className="text-gray-600">
                  Something went wrong. Please try uploading again.
                </p>
              </>
            )}
          </div>
        </div>
      )}

      {/* Analysis Results */}
      {video.status === 'completed' && analysis && (
        <>
          {/* Overall Score Card */}
          <div className="bg-gradient-to-r from-purple-600 to-indigo-600 rounded-lg shadow-lg p-8 text-white mb-8">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold mb-2 opacity-90">
                  Jake Morrison's Verdict
                </h3>
                <p className="text-4xl font-bold">{analysis.overall_score}/100</p>
                {analysis.overall_grade && (
                  <p className="text-2xl font-semibold mt-2 opacity-90">
                    Grade: {analysis.overall_grade}
                  </p>
                )}
              </div>
              <div className="text-6xl">🎭</div>
            </div>
          </div>

          {/* Summary */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-4">Summary</h3>
            <div className="prose prose-lg max-w-none text-gray-700 whitespace-pre-line">
              {analysis.summary}
            </div>
          </div>

          {/* Category Scores */}
          <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
            <h3 className="text-2xl font-bold text-gray-900 mb-6">
              Category Breakdown
            </h3>
            <div className="space-y-4">
              <CategoryScoreBar
                name="Psychology"
                score={analysis.category_scores.psychology}
                description="Understanding of the mental game and storytelling"
              />
              <CategoryScoreBar
                name="Character Work"
                score={analysis.category_scores.character_work}
                description="Authenticity and distinctiveness of persona"
              />
              <CategoryScoreBar
                name="Delivery"
                score={analysis.category_scores.delivery}
                description="Voice projection, pacing, and emotional range"
              />
              <CategoryScoreBar
                name="Story Structure"
                score={analysis.category_scores.story_structure}
                description="Beginning, middle, end with logical progression"
              />
              <CategoryScoreBar
                name="Crowd Connection"
                score={analysis.category_scores.crowd_connection}
                description="Ability to work with a live audience"
              />
              <CategoryScoreBar
                name="Originality"
                score={analysis.category_scores.originality}
                description="Fresh takes and creative perspective"
              />
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid grid-cols-2 gap-8 mb-8">
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h3 className="text-2xl font-bold text-green-600 mb-4 flex items-center">
                <span className="mr-2">💪</span>
                Strengths
              </h3>
              <ul className="space-y-3">
                {analysis.strengths.map((strength, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-green-500 mr-2 mt-1">✓</span>
                    <span className="text-gray-700">{strength}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white rounded-lg shadow-lg p-8">
              <h3 className="text-2xl font-bold text-orange-600 mb-4 flex items-center">
                <span className="mr-2">🎯</span>
                Areas to Improve
              </h3>
              <ul className="space-y-3">
                {analysis.weaknesses.map((weakness, index) => (
                  <li key={index} className="flex items-start">
                    <span className="text-orange-500 mr-2 mt-1">→</span>
                    <span className="text-gray-700">{weakness}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Timestamped Feedback */}
          {analysis.timestamped_feedback && analysis.timestamped_feedback.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                Timestamped Feedback
              </h3>
              <TimestampedFeedbackList feedback={analysis.timestamped_feedback} />
            </div>
          )}

          {/* Recommendations */}
          {analysis.specific_recommendations && analysis.specific_recommendations.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4 flex items-center">
                <span className="mr-2">🚀</span>
                Action Items
              </h3>
              <ol className="space-y-3 list-decimal list-inside">
                {analysis.specific_recommendations.map((rec, index) => (
                  <li key={index} className="text-gray-700 pl-2">
                    {rec}
                  </li>
                ))}
              </ol>
            </div>
          )}

          {/* Transcript */}
          {video.transcript && (
            <div className="bg-white rounded-lg shadow-lg p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6">
                Full Transcript
              </h3>
              <TranscriptView transcript={video.transcript} />
            </div>
          )}
        </>
      )}

      {/* Video Metadata Footer */}
      <div className="mt-8 bg-gray-100 rounded-lg p-6">
        <h4 className="font-semibold text-gray-900 mb-3">Video Information</h4>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
          {video.duration_seconds && (
            <div>
              <p className="text-gray-600">Duration</p>
              <p className="font-medium text-gray-900">
                {formatDuration(video.duration_seconds)}
              </p>
            </div>
          )}
          {video.width && video.height && (
            <div>
              <p className="text-gray-600">Resolution</p>
              <p className="font-medium text-gray-900">
                {video.width}x{video.height}
              </p>
            </div>
          )}
          {video.codec && (
            <div>
              <p className="text-gray-600">Codec</p>
              <p className="font-medium text-gray-900">{video.codec}</p>
            </div>
          )}
          <div>
            <p className="text-gray-600">Uploaded</p>
            <p className="font-medium text-gray-900">
              {new Date(video.created_at).toLocaleDateString()}
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
