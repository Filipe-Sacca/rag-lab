import { useState } from 'react'

interface ScoreProgressBarProps {
  score: number           // Rerank score (0-1)
  originalScore?: number  // Original bi-encoder score (0-1)
  showTooltip?: boolean
}

/**
 * Progress bar component for displaying rerank scores with tooltip showing original score.
 *
 * Visual requirements:
 * - Bar fills based on score percentage (0-100%)
 * - Color changes based on score thresholds (red → yellow → green)
 * - Tooltip shows both scores on hover
 */
export default function ScoreProgressBar({
  score,
  originalScore,
  showTooltip = true
}: ScoreProgressBarProps) {
  const [isHovered, setIsHovered] = useState(false)

  const percentage = Math.min(100, Math.max(0, score * 100))

  // Color coding based on relevance score thresholds
  const getBarColor = (score: number): string => {
    if (score >= 0.8) return 'bg-green-500'    // High relevance
    if (score >= 0.6) return 'bg-yellow-500'   // Medium relevance
    if (score >= 0.4) return 'bg-orange-500'   // Low relevance
    return 'bg-red-500'                         // Very low relevance
  }

  const barColor = getBarColor(score)
  const hasImproved = originalScore !== undefined && score > originalScore
  const improvement = originalScore !== undefined
    ? ((score - originalScore) * 100).toFixed(1)
    : null

  return (
    <div
      className="relative flex items-center gap-2"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Progress bar container */}
      <div className="flex-1 h-2 bg-gray-200 rounded-full overflow-hidden min-w-[60px]">
        <div
          className={`h-full ${barColor} transition-all duration-300 ease-out`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      {/* Score percentage */}
      <span className="text-xs font-medium text-gray-700 min-w-[40px] text-right">
        {percentage.toFixed(1)}%
      </span>

      {/* Tooltip on hover */}
      {showTooltip && isHovered && originalScore !== undefined && (
        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-3 py-2 bg-gray-900 text-white text-xs rounded-lg shadow-lg z-10 whitespace-nowrap">
          <div className="flex flex-col gap-1">
            <div className="flex justify-between gap-4">
              <span className="text-gray-400">Rerank:</span>
              <span className="font-medium">{(score * 100).toFixed(1)}%</span>
            </div>
            <div className="flex justify-between gap-4">
              <span className="text-gray-400">Original:</span>
              <span>{(originalScore * 100).toFixed(1)}%</span>
            </div>
            {improvement && (
              <div className={`text-center pt-1 border-t border-gray-700 ${hasImproved ? 'text-green-400' : 'text-red-400'}`}>
                {hasImproved ? '↑' : '↓'} {Math.abs(parseFloat(improvement))}%
              </div>
            )}
          </div>
          {/* Tooltip arrow */}
          <div className="absolute top-full left-1/2 transform -translate-x-1/2 border-4 border-transparent border-t-gray-900" />
        </div>
      )}
    </div>
  )
}
