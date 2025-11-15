import { Routes, Route, Link } from 'react-router-dom'
import UploadPage from './pages/UploadPage'
import VideoDetailPage from './pages/VideoDetailPage'
import VideosListPage from './pages/VideosListPage'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-gradient-to-r from-purple-900 via-purple-800 to-indigo-900 text-white shadow-lg">
        <div className="container mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <Link to="/" className="flex items-center space-x-3">
              <div className="text-4xl">🎭</div>
              <div>
                <h1 className="text-3xl font-bold">Wrestling Promo Analyzer</h1>
                <p className="text-sm text-purple-200">AI-Powered Feedback by Jake Morrison</p>
              </div>
            </Link>

            <nav className="flex space-x-6">
              <Link
                to="/"
                className="hover:text-purple-200 transition-colors font-medium"
              >
                Upload
              </Link>
              <Link
                to="/videos"
                className="hover:text-purple-200 transition-colors font-medium"
              >
                My Videos
              </Link>
            </nav>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        <Routes>
          <Route path="/" element={<UploadPage />} />
          <Route path="/videos" element={<VideosListPage />} />
          <Route path="/videos/:videoId" element={<VideoDetailPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 mt-16">
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <p className="text-sm">
              Wrestling Promo Analyzer - Train with Jake Morrison AI
            </p>
            <p className="text-xs text-gray-400 mt-2">
              Powered by Claude AI &amp; Whisper Speech Recognition
            </p>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default App
