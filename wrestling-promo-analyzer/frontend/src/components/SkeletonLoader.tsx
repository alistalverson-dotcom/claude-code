/**
 * Skeleton loading components for better perceived performance
 */

export function SkeletonCard() {
  return (
    <div className="bg-white rounded-lg shadow-lg p-8 animate-pulse">
      <div className="h-8 bg-gray-200 rounded w-3/4 mb-4"></div>
      <div className="space-y-3">
        <div className="h-4 bg-gray-200 rounded"></div>
        <div className="h-4 bg-gray-200 rounded w-5/6"></div>
        <div className="h-4 bg-gray-200 rounded w-4/6"></div>
      </div>
    </div>
  )
}

export function SkeletonScore() {
  return (
    <div className="bg-gradient-to-r from-gray-300 to-gray-400 rounded-lg shadow-lg p-8 animate-pulse">
      <div className="flex items-center justify-between">
        <div className="space-y-3">
          <div className="h-6 bg-gray-500 rounded w-48"></div>
          <div className="h-12 bg-gray-500 rounded w-32"></div>
        </div>
        <div className="h-16 w-16 bg-gray-500 rounded-full"></div>
      </div>
    </div>
  )
}

export function SkeletonCategoryBar() {
  return (
    <div className="animate-pulse">
      <div className="flex justify-between items-center mb-2">
        <div className="space-y-2 flex-1">
          <div className="h-5 bg-gray-200 rounded w-1/4"></div>
          <div className="h-3 bg-gray-200 rounded w-1/2"></div>
        </div>
        <div className="h-8 w-12 bg-gray-200 rounded ml-4"></div>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-3">
        <div className="h-3 rounded-full bg-gray-300" style={{ width: '60%' }}></div>
      </div>
    </div>
  )
}

export function SkeletonList() {
  return (
    <div className="space-y-4">
      {[1, 2, 3].map((i) => (
        <div key={i} className="bg-white rounded-lg shadow p-6 animate-pulse">
          <div className="flex items-center space-x-4">
            <div className="h-12 w-12 bg-gray-200 rounded-full"></div>
            <div className="flex-1 space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
            <div className="h-8 w-24 bg-gray-200 rounded-full"></div>
          </div>
        </div>
      ))}
    </div>
  )
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
  return (
    <div className="space-y-3 animate-pulse">
      {Array.from({ length: lines }).map((_, i) => (
        <div
          key={i}
          className="h-4 bg-gray-200 rounded"
          style={{ width: i === lines - 1 ? '80%' : '100%' }}
        ></div>
      ))}
    </div>
  )
}
