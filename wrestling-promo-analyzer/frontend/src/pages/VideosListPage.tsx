import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { listVideos, formatDuration } from '../services/api'
import type { VideoListItem } from '../types'
import { SkeletonList } from '../components/SkeletonLoader'

export default function VideosListPage() {
  const [videos, setVideos] = useState<VideoListItem[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [statusFilter, setStatusFilter] = useState<string>('')

  useEffect(() => {
    loadVideos()
  }, [statusFilter])

  const loadVideos = async () => {
    try {
      setLoading(true)
      setError(null)
      const data = await listVideos({
        status: statusFilter || undefined,
      })
      setVideos(data)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load videos')
    } finally {
      setLoading(false)
    }
  }

  const getStatusBadge = (status: string) => {
    const badges = {
      uploaded: 'bg-gray-100 text-gray-800',
      processing: 'bg-blue-100 text-blue-800 animate-pulse',
      completed: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
    }
    return badges[status as keyof typeof badges] || 'bg-gray-100 text-gray-800'
  }

  const getStatusIcon = (status: string) => {
    const icons = {
      uploaded: '📤',
      processing: '⏳',
      completed: '✅',
      failed: '❌',
    }
    return icons[status as keyof typeof icons] || '📄'
  }

  return (
    <div className="max-w-6xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">My Videos</h2>
        <p className="text-lg text-gray-600">
          View all your uploaded promos and their analysis results
        </p>
      </div>

      {/* Filter */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <label className="text-sm font-medium text-gray-700">Filter:</label>
            <select
              value={statusFilter}
              onChange={(e) => setStatusFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
            >
              <option value="">All Videos</option>
              <option value="uploaded">Uploaded</option>
              <option value="processing">Processing</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
            </select>
          </div>

          <button
            onClick={loadVideos}
            className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
          >
            Refresh
          </button>
        </div>
      </div>

      {/* Loading State */}
      {loading && <SkeletonList />}

      {/* Error State */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
          <p className="font-medium">Error</p>
          <p className="text-sm">{error}</p>
        </div>
      )}

      {/* Videos List */}
      {!loading && !error && videos.length === 0 && (
        <div className="bg-white rounded-lg shadow-lg p-12 text-center">
          <div className="text-6xl mb-4">🎬</div>
          <h3 className="text-2xl font-bold text-gray-900 mb-2">
            No videos yet
          </h3>
          <p className="text-gray-600 mb-6">
            Upload your first promo to get started
          </p>
          <Link
            to="/"
            className="inline-block bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
          >
            Upload Video
          </Link>
        </div>
      )}

      {!loading && !error && videos.length > 0 && (
        <div className="space-y-4">
          {videos.map((video) => (
            <Link
              key={video.video_id}
              to={`/videos/${video.video_id}`}
              className="block bg-white rounded-lg shadow hover:shadow-lg transition-shadow p-6"
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-4 flex-1">
                  <div className="text-4xl">{getStatusIcon(video.status)}</div>

                  <div className="flex-1">
                    <h3 className="text-lg font-semibold text-gray-900 mb-1">
                      {video.promo_title || video.original_filename}
                    </h3>
                    {video.promo_title && (
                      <p className="text-sm text-gray-600 mb-2">
                        {video.original_filename}
                      </p>
                    )}
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>
                        Uploaded: {new Date(video.created_at).toLocaleDateString()}
                      </span>
                      {video.duration_seconds && (
                        <span>
                          Duration: {formatDuration(video.duration_seconds)}
                        </span>
                      )}
                    </div>
                  </div>
                </div>

                <div className="flex items-center space-x-4">
                  <span
                    className={`px-4 py-2 rounded-full text-sm font-medium ${getStatusBadge(
                      video.status
                    )}`}
                  >
                    {video.status.charAt(0).toUpperCase() + video.status.slice(1)}
                  </span>

                  <svg
                    className="w-6 h-6 text-gray-400"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      strokeWidth={2}
                      d="M9 5l7 7-7 7"
                    />
                  </svg>
                </div>
              </div>
            </Link>
          ))}
        </div>
      )}

      {/* Pagination (future enhancement) */}
      {videos.length >= 20 && (
        <div className="mt-8 text-center">
          <p className="text-sm text-gray-600">
            Showing {videos.length} videos
          </p>
        </div>
      )}
    </div>
  )
}
