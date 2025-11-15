import { useState, useEffect } from 'react'
import { useParams, Link } from 'react-router-dom'
import { getVideo, pollVideoStatus, formatDuration, getGradeColor, getScoreColor } from '../services/api'
import type { VideoDetailResponse, AnalysisResponse } from '../types'
import CategoryScoreBar from '../components/CategoryScoreBar'
import TimestampedFeedbackList from '../components/TimestampedFeedbackList'
import TranscriptView from '../components/TranscriptView'
import ProcessingStatus from '../components/ProcessingStatus'
import VideoPlayer from '../components/VideoPlayer'
import ErrorDisplay from '../components/ErrorDisplay'
import { SkeletonScore, SkeletonCard, SkeletonCategoryBar } from '../components/SkeletonLoader'
import VisualPerformanceMetrics from '../components/VisualPerformanceMetrics'
import EmotionBreakdownChart from '../components/EmotionBreakdownChart'
import GestureAnalysisCard from '../components/GestureAnalysisCard'
import ProductionQualityCard from '../components/ProductionQualityCard'
import EffectsSummaryCard from '../components/EffectsSummaryCard'
import ColorGradingVisualization from '../components/ColorGradingVisualization'
import EffectsBreakdownTable from '../components/EffectsBreakdownTable'

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
      <div className="max-w-6xl mx-auto">
        {/* Header Skeleton */}
        <div className="mb-6 animate-pulse">
          <div className="h-4 bg-gray-200 rounded w-32 mb-4"></div>
          <div className="h-10 bg-gray-200 rounded w-3/4 mb-2"></div>
          <div className="h-4 bg-gray-200 rounded w-1/2"></div>
        </div>

        {/* Content Skeletons */}
        <div className="space-y-8">
          <SkeletonScore />
          <SkeletonCard />
          <div className="bg-white rounded-lg shadow-lg p-8">
            <div className="space-y-4">
              <SkeletonCategoryBar />
              <SkeletonCategoryBar />
              <SkeletonCategoryBar />
            </div>
          </div>
        </div>
      </div>
    )
  }

  if (error || !video) {
    return (
      <div className="max-w-6xl mx-auto">
        <ErrorDisplay
          error={error || 'Video not found'}
          onRetry={() => videoId && loadVideo(videoId)}
        />
        <div className="mt-4">
          <Link to="/videos" className="text-purple-600 hover:text-purple-700 font-medium">
            ← Back to videos
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

      {/* Video Player */}
      {video.status !== 'failed' && (
        <div className="mb-8">
          <VideoPlayer
            videoUrl={`${import.meta.env.VITE_API_URL || 'http://localhost:8000'}/api/v1/videos/${video.video_id}/stream`}
            title={video.promo_title || video.original_filename}
          />
        </div>
      )}

      {/* Processing Status */}
      {video.status !== 'completed' && (
        <ProcessingStatus
          videoStatus={video.status as 'uploaded' | 'processing' | 'failed'}
          currentStep={2}
        />
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

          {/* Visual Performance Metrics */}
          {(analysis.category_scores.facial_expressions ||
            analysis.category_scores.body_language ||
            analysis.category_scores.visual_presence ||
            analysis.visual_analysis) && (
            <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                <span className="mr-3">📹</span>
                Visual Performance Analysis
              </h3>
              <VisualPerformanceMetrics
                facialExpression={analysis.category_scores.facial_expressions}
                bodyLanguage={analysis.category_scores.body_language}
                visualPresence={analysis.category_scores.visual_presence}
                productionQuality={analysis.visual_analysis?.production_quality?.overall}
              />

              {/* Emotion & Gesture Details */}
              {analysis.visual_analysis && (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-8">
                  {/* Emotion Breakdown */}
                  {analysis.visual_analysis.emotion_breakdown && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <span className="mr-2">🎭</span>
                        Emotion Breakdown
                      </h4>
                      <EmotionBreakdownChart
                        emotionBreakdown={analysis.visual_analysis.emotion_breakdown}
                      />
                    </div>
                  )}

                  {/* Gesture Analysis */}
                  {analysis.visual_analysis.top_gestures && (
                    <div>
                      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <span className="mr-2">👋</span>
                        Top Gestures
                      </h4>
                      <GestureAnalysisCard gestures={analysis.visual_analysis.top_gestures} />
                    </div>
                  )}
                </div>
              )}

              {/* Production Quality */}
              {analysis.visual_analysis?.production_quality && (
                <div className="mt-8">
                  <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                    <span className="mr-2">🎬</span>
                    Production Quality
                  </h4>
                  <ProductionQualityCard
                    productionDetails={analysis.visual_analysis.production_quality}
                  />
                </div>
              )}
            </div>
          )}

          {/* Visual Effects & Production Techniques (NEW) */}
          {analysis.visual_analysis?.effects_analysis && (
            <>
              {/* Effects Summary Card */}
              <EffectsSummaryCard effectsAnalysis={analysis.visual_analysis.effects_analysis} />

              {/* Detailed Effects Analysis */}
              <div className="bg-white rounded-lg shadow-lg p-8 mb-8">
                <h3 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <span className="mr-3">🎨</span>
                  Visual Effects Details
                </h3>

                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                  {/* Color Grading */}
                  {analysis.visual_analysis.effects_analysis.color_grading && (
                    <ColorGradingVisualization
                      colorGrading={analysis.visual_analysis.effects_analysis.color_grading}
                    />
                  )}

                  {/* Placeholder for additional visualizations if needed */}
                  {analysis.visual_analysis.effects_analysis.camera_work && (
                    <div className="bg-white rounded-lg shadow-md p-6">
                      <h4 className="text-lg font-semibold text-gray-900 mb-4 flex items-center">
                        <span className="mr-2">🎥</span>
                        Camera Work
                      </h4>
                      <div className="space-y-3">
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Stability</span>
                          <span className="text-sm font-semibold text-gray-900">
                            {analysis.visual_analysis.effects_analysis.camera_work.stability?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                          </span>
                        </div>
                        <div className="flex justify-between items-center p-3 bg-gray-50 rounded-lg">
                          <span className="text-sm text-gray-600">Style</span>
                          <span className="text-sm font-semibold text-gray-900">
                            {analysis.visual_analysis.effects_analysis.camera_work.style?.split('_').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')}
                          </span>
                        </div>
                        {analysis.visual_analysis.effects_analysis.camera_work.feedback && (
                          <div className="mt-4 p-3 bg-green-50 rounded-lg border-l-4 border-green-500">
                            <p className="text-sm text-green-800">{analysis.visual_analysis.effects_analysis.camera_work.feedback}</p>
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>

                {/* Effects Breakdown Table */}
                <EffectsBreakdownTable
                  visualFilters={analysis.visual_analysis.effects_analysis.filters}
                  visualEffects={analysis.visual_analysis.effects_analysis.visual_effects}
                  cameraWork={analysis.visual_analysis.effects_analysis.camera_work}
                />
              </div>
            </>
          )}

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

              {/* Visual category scores */}
              {analysis.category_scores.facial_expressions && (
                <CategoryScoreBar
                  name="Facial Expressions"
                  score={analysis.category_scores.facial_expressions}
                  description="Emotion conveyance, authenticity, and eye contact"
                />
              )}
              {analysis.category_scores.body_language && (
                <CategoryScoreBar
                  name="Body Language"
                  score={analysis.category_scores.body_language}
                  description="Posture, gestures, and physical presence"
                />
              )}
              {analysis.category_scores.visual_presence && (
                <CategoryScoreBar
                  name="Visual Presence"
                  score={analysis.category_scores.visual_presence}
                  description="Camera work, charisma, and overall presentation"
                />
              )}
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
