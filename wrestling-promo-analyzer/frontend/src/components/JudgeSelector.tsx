import { useState, useEffect } from 'react';
import type { JudgeResponse } from '../types';

interface JudgeSelectorProps {
  selectedJudge: string;
  onSelectJudge: (slug: string) => void;
  className?: string;
}

export default function JudgeSelector({ selectedJudge, onSelectJudge, className = '' }: JudgeSelectorProps) {
  const [judges, setJudges] = useState<JudgeResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDetails, setShowDetails] = useState(false);

  useEffect(() => {
    fetchJudges();
  }, []);

  const fetchJudges = async () => {
    try {
      const response = await fetch('/api/v1/judges');
      if (!response.ok) {
        throw new Error('Failed to fetch judges');
      }
      const data = await response.json();
      setJudges(data.filter((j: JudgeResponse) => j.is_active));
      setLoading(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load judges');
      setLoading(false);
    }
  };

  const selectedJudgeData = judges.find(j => j.slug === selectedJudge);

  if (loading) {
    return (
      <div className={`border border-gray-300 rounded-lg p-6 bg-gray-50 ${className}`}>
        <div className="animate-pulse">
          <div className="h-4 bg-gray-300 rounded w-1/3 mb-4"></div>
          <div className="h-10 bg-gray-300 rounded mb-2"></div>
          <div className="h-10 bg-gray-300 rounded"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`border border-red-300 rounded-lg p-6 bg-red-50 ${className}`}>
        <p className="text-red-700">⚠️ {error}</p>
        <p className="text-sm text-red-600 mt-2">Using default judge (Jake Morrison)</p>
      </div>
    );
  }

  return (
    <div className={`border border-gray-300 rounded-lg p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-4">
        <label className="block text-lg font-semibold text-gray-900">
          Select AI Judge
        </label>
        <button
          type="button"
          onClick={() => setShowDetails(!showDetails)}
          className="text-sm text-blue-600 hover:text-blue-800 underline"
        >
          {showDetails ? 'Hide Details' : 'Show Details'}
        </button>
      </div>

      <div className="space-y-3">
        {judges.map((judge) => (
          <div key={judge.slug}>
            <label
              className={`flex items-start p-4 border-2 rounded-lg cursor-pointer transition-all ${
                selectedJudge === judge.slug
                  ? 'border-blue-500 bg-blue-50'
                  : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
              }`}
            >
              <input
                type="radio"
                name="judge"
                value={judge.slug}
                checked={selectedJudge === judge.slug}
                onChange={(e) => onSelectJudge(e.target.value)}
                className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
              />
              <div className="ml-3 flex-1">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-gray-900">{judge.name}</span>
                  <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                    {judge.personality_type}
                  </span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{judge.description}</p>

                {showDetails && selectedJudge === judge.slug && (
                  <div className="mt-3 pt-3 border-t border-gray-200">
                    <p className="text-sm font-medium text-gray-700 mb-2">Evaluation Focus:</p>
                    <p className="text-sm text-gray-600">{judge.evaluation_focus}</p>
                  </div>
                )}
              </div>
            </label>
          </div>
        ))}
      </div>

      {selectedJudgeData && (
        <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
          <p className="text-sm text-blue-900">
            <span className="font-semibold">Selected:</span> {selectedJudgeData.name} will analyze your promo
            {selectedJudgeData.slug === 'jake-morrison' && ' with a veteran coaching perspective'}
            {selectedJudgeData.slug === 'diana-sterling' && ' through a performance psychology lens'}
          </p>
        </div>
      )}

      <div className="mt-4 p-3 bg-gray-50 rounded-lg">
        <p className="text-xs text-gray-600">
          💡 <span className="font-semibold">Tip:</span> Different judges provide unique perspectives.
          Jake focuses on traditional coaching, while Dr. Sterling analyzes psychological authenticity.
        </p>
      </div>
    </div>
  );
}
