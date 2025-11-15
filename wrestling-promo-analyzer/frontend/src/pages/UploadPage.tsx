import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadVideo } from '../services/api'
import { CHARACTER_TYPES, PROMO_TYPES, type VideoUploadForm } from '../types'

export default function UploadPage() {
  const navigate = useNavigate()
  const fileInputRef = useRef<HTMLInputElement>(null)

  const [file, setFile] = useState<File | null>(null)
  const [promoTitle, setPromoTitle] = useState('')
  const [promoType, setPromoType] = useState('')
  const [characterType, setCharacterType] = useState('')
  const [promoContext, setPromoContext] = useState('')

  const [uploading, setUploading] = useState(false)
  const [uploadProgress, setUploadProgress] = useState(0)
  const [error, setError] = useState<string | null>(null)
  const [dragActive, setDragActive] = useState(false)

  const ALLOWED_FORMATS = ['.mp4', '.mov', '.avi', '.mkv']
  const MAX_SIZE_MB = 500

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === 'dragenter' || e.type === 'dragover') {
      setDragActive(true)
    } else if (e.type === 'dragleave') {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFileSelect(e.dataTransfer.files[0])
    }
  }

  const handleFileSelect = (selectedFile: File) => {
    setError(null)

    // Check file extension
    const ext = '.' + selectedFile.name.split('.').pop()?.toLowerCase()
    if (!ALLOWED_FORMATS.includes(ext)) {
      setError(`Invalid file type. Allowed formats: ${ALLOWED_FORMATS.join(', ')}`)
      return
    }

    // Check file size
    const sizeMB = selectedFile.size / 1024 / 1024
    if (sizeMB > MAX_SIZE_MB) {
      setError(`File too large. Maximum size: ${MAX_SIZE_MB}MB. Your file: ${sizeMB.toFixed(1)}MB`)
      return
    }

    setFile(selectedFile)
  }

  const handleFileInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      handleFileSelect(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!file) {
      setError('Please select a video file')
      return
    }

    setUploading(true)
    setError(null)
    setUploadProgress(0)

    try {
      const formData: VideoUploadForm = {
        file,
        promo_title: promoTitle || undefined,
        promo_type: promoType || undefined,
        character_type: characterType || undefined,
        promo_context: promoContext || undefined,
      }

      const response = await uploadVideo(formData, (progress) => {
        setUploadProgress(progress)
      })

      // Navigate to video detail page
      navigate(`/videos/${response.video_id}`)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Upload failed')
      setUploading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      {/* Header */}
      <div className="text-center mb-8">
        <h2 className="text-4xl font-bold text-gray-900 mb-4">
          Upload Your Promo
        </h2>
        <p className="text-lg text-gray-600">
          Get AI-powered feedback from Jake Morrison in under 2 minutes
        </p>
      </div>

      {/* Upload Form */}
      <div className="bg-white rounded-lg shadow-lg p-8">
        <form onSubmit={handleSubmit}>
          {/* File Drop Zone */}
          <div
            className={`border-2 border-dashed rounded-lg p-12 text-center transition-colors ${
              dragActive
                ? 'border-purple-500 bg-purple-50'
                : 'border-gray-300 hover:border-purple-400'
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <input
              ref={fileInputRef}
              type="file"
              accept={ALLOWED_FORMATS.join(',')}
              onChange={handleFileInputChange}
              className="hidden"
            />

            {file ? (
              <div>
                <div className="text-5xl mb-4">🎬</div>
                <p className="text-xl font-semibold text-gray-900 mb-2">
                  {file.name}
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  {(file.size / 1024 / 1024).toFixed(2)} MB
                </p>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="text-purple-600 hover:text-purple-700 font-medium"
                >
                  Change file
                </button>
              </div>
            ) : (
              <div>
                <div className="text-5xl mb-4">📁</div>
                <p className="text-xl font-semibold text-gray-900 mb-2">
                  Drop your video here
                </p>
                <p className="text-sm text-gray-600 mb-4">
                  or click to browse
                </p>
                <button
                  type="button"
                  onClick={() => fileInputRef.current?.click()}
                  className="bg-purple-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-purple-700 transition-colors"
                >
                  Select Video
                </button>
                <p className="text-xs text-gray-500 mt-4">
                  Supported formats: MP4, MOV, AVI, MKV (max {MAX_SIZE_MB}MB)
                </p>
              </div>
            )}
          </div>

          {/* Optional Metadata */}
          {file && (
            <div className="mt-8 space-y-6">
              <h3 className="text-xl font-semibold text-gray-900">
                Optional Information
              </h3>
              <p className="text-sm text-gray-600">
                Help Jake understand your promo better
              </p>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Promo Title
                </label>
                <input
                  type="text"
                  value={promoTitle}
                  onChange={(e) => setPromoTitle(e.target.value)}
                  placeholder="e.g., Championship Challenge"
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>

              <div className="grid grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Character Type
                  </label>
                  <select
                    value={characterType}
                    onChange={(e) => setCharacterType(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Select...</option>
                    {CHARACTER_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Promo Type
                  </label>
                  <select
                    value={promoType}
                    onChange={(e) => setPromoType(e.target.value)}
                    className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                  >
                    <option value="">Select...</option>
                    {PROMO_TYPES.map((type) => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Context / Notes
                </label>
                <textarea
                  value={promoContext}
                  onChange={(e) => setPromoContext(e.target.value)}
                  placeholder="Any background info that helps Jake understand the promo..."
                  rows={4}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                />
              </div>
            </div>
          )}

          {/* Error Message */}
          {error && (
            <div className="mt-6 bg-red-50 border border-red-200 text-red-800 px-4 py-3 rounded-lg">
              <p className="font-medium">Error</p>
              <p className="text-sm">{error}</p>
            </div>
          )}

          {/* Upload Progress */}
          {uploading && (
            <div className="mt-6">
              <div className="flex justify-between items-center mb-2">
                <span className="text-sm font-medium text-gray-700">
                  Uploading...
                </span>
                <span className="text-sm text-gray-600">
                  {uploadProgress.toFixed(0)}%
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div
                  className="bg-purple-600 h-3 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                />
              </div>
            </div>
          )}

          {/* Submit Button */}
          {file && !uploading && (
            <div className="mt-8">
              <button
                type="submit"
                className="w-full bg-gradient-to-r from-purple-600 to-indigo-600 text-white py-4 rounded-lg font-bold text-lg hover:from-purple-700 hover:to-indigo-700 transition-all shadow-lg"
              >
                Upload & Analyze
              </button>
            </div>
          )}
        </form>
      </div>

      {/* Info Cards */}
      <div className="mt-12 grid grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="text-3xl mb-3">⚡</div>
          <h4 className="font-semibold text-gray-900 mb-2">Fast Analysis</h4>
          <p className="text-sm text-gray-600">
            Get results in under 2 minutes for most videos
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="text-3xl mb-3">🎯</div>
          <h4 className="font-semibold text-gray-900 mb-2">Detailed Feedback</h4>
          <p className="text-sm text-gray-600">
            6 category scores with timestamped comments
          </p>
        </div>

        <div className="bg-white rounded-lg shadow p-6 text-center">
          <div className="text-3xl mb-3">📈</div>
          <h4 className="font-semibold text-gray-900 mb-2">Actionable Tips</h4>
          <p className="text-sm text-gray-600">
            Specific recommendations to improve your craft
          </p>
        </div>
      </div>
    </div>
  )
}
