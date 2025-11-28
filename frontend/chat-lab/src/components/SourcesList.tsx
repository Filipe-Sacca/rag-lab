import { useState, useMemo } from 'react'
import { Source } from '../types/rag.types'
import { FileText, ChevronDown, ChevronUp, ArrowUpDown } from 'lucide-react'
import { highlightText, truncateText } from '../utils/textHighlight'
import ScoreProgressBar from './ScoreProgressBar'

interface SourcesListProps {
  sources: Source[]
  query: string
}

type SortOption = 'score-desc' | 'score-asc' | 'document-asc' | 'original'

interface SortConfig {
  value: SortOption
  label: string
}

const SORT_OPTIONS: SortConfig[] = [
  { value: 'score-desc', label: 'Best Match' },
  { value: 'score-asc', label: 'Lowest Match' },
  { value: 'document-asc', label: 'Document Name' },
  { value: 'original', label: 'Original Order' }
]

const COLLAPSE_THRESHOLD = 300 // Characters before showing expand/collapse
const PREVIEW_LENGTH = 200 // Characters to show when collapsed

export default function SourcesList({ sources, query }: SourcesListProps) {
  // State
  const [expandedSources, setExpandedSources] = useState<Set<number>>(new Set())
  const [sortBy, setSortBy] = useState<SortOption>('score-desc')
  const [scoreFilter, setScoreFilter] = useState<number>(0) // 0 = show all

  if (!sources || sources.length === 0) {
    return null
  }

  const getScoreColor = (score: number) => {
    if (score >= 0.8) return 'text-green-600 bg-green-50'
    if (score >= 0.6) return 'text-yellow-600 bg-yellow-50'
    return 'text-orange-600 bg-orange-50'
  }

  const toggleExpanded = (index: number) => {
    const newExpanded = new Set(expandedSources)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedSources(newExpanded)
  }

  // Filter by score
  const filteredSources = useMemo(() => {
    return sources.filter(source => source.score >= scoreFilter)
  }, [sources, scoreFilter])

  // Sort sources
  const sortedSources = useMemo(() => {
    const sorted = [...filteredSources]

    switch (sortBy) {
      case 'score-desc':
        return sorted.sort((a, b) => b.score - a.score)
      case 'score-asc':
        return sorted.sort((a, b) => a.score - b.score)
      case 'document-asc':
        return sorted.sort((a, b) =>
          a.metadata.document.localeCompare(b.metadata.document) ||
          a.metadata.page - b.metadata.page
        )
      case 'original':
      default:
        return sorted
    }
  }, [filteredSources, sortBy])

  const getFilterLabel = (threshold: number): string => {
    if (threshold === 0) return 'All'
    if (threshold >= 0.8) return 'High (>80%)'
    if (threshold >= 0.6) return 'Medium (>60%)'
    if (threshold >= 0.4) return 'Low (>40%)'
    return `>${(threshold * 100).toFixed(0)}%`
  }

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      {/* Header with controls */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-4">
        <div className="flex items-center gap-2">
          <FileText className="text-gray-600" size={20} />
          <h3 className="text-sm font-medium text-gray-900">Retrieved Sources</h3>
          <span className="text-xs text-gray-500">
            {sortedSources.length === sources.length
              ? `${sources.length} chunks`
              : `${sortedSources.length} of ${sources.length} chunks`
            }
          </span>
        </div>

        <div className="flex items-center gap-3">
          {/* Sort dropdown */}
          <div className="flex items-center gap-2">
            <ArrowUpDown size={16} className="text-gray-500" />
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value as SortOption)}
              className="text-xs border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent bg-white cursor-pointer"
              aria-label="Sort sources"
            >
              {SORT_OPTIONS.map(option => (
                <option key={option.value} value={option.value}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>

          {/* Score filter pills */}
          <div className="flex items-center gap-1">
            {[0, 0.4, 0.6, 0.8].map(threshold => (
              <button
                key={threshold}
                onClick={() => setScoreFilter(threshold)}
                className={`text-xs px-2 py-1 rounded-full transition-colors ${
                  scoreFilter === threshold
                    ? 'bg-primary-500 text-white font-medium'
                    : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
                }`}
                aria-label={`Filter by ${getFilterLabel(threshold)}`}
              >
                {getFilterLabel(threshold)}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Empty state after filtering */}
      {sortedSources.length === 0 && (
        <div className="text-center py-8 text-gray-500">
          <p className="text-sm">No sources match the current filter</p>
          <button
            onClick={() => setScoreFilter(0)}
            className="text-xs text-primary-500 hover:text-primary-600 mt-2 underline"
          >
            Clear filter
          </button>
        </div>
      )}

      {/* Sources list */}
      <div className="space-y-3">
        {sortedSources.map((source, index) => {
          const isLong = source.content.length > COLLAPSE_THRESHOLD
          const isExpanded = expandedSources.has(index)
          const highlightedParts = highlightText(source.content, query)

          return (
            <div
              key={index}
              className={`border border-gray-200 rounded-lg p-3 transition-all duration-300 ${
                isExpanded ? 'bg-gray-50 border-primary-300' : 'hover:border-primary-300'
              }`}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="text-xs font-medium text-gray-700">
                      {source.metadata.document}
                    </span>
                    <span className="text-xs text-gray-500">
                      Page {source.metadata.page}
                    </span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {source.metadata.chunk_id}
                  </span>
                </div>
                <div className="w-32">
                  <ScoreProgressBar
                    score={source.score}
                    originalScore={source.original_score}
                    showTooltip={true}
                  />
                </div>
              </div>

              {/* Content with highlights */}
              <div className="text-sm text-gray-700 leading-relaxed">
                {isLong && !isExpanded ? (
                  // Collapsed view - show preview with highlights
                  <p>
                    {highlightText(truncateText(source.content, PREVIEW_LENGTH), query).map((part, i) => (
                      part.highlight ? (
                        <mark
                          key={i}
                          className="bg-yellow-200 text-yellow-900 px-0.5 rounded"
                        >
                          {part.text}
                        </mark>
                      ) : (
                        <span key={i}>{part.text}</span>
                      )
                    ))}
                  </p>
                ) : (
                  // Expanded view - show full content with highlights
                  <p>
                    {highlightedParts.map((part, i) => (
                      part.highlight ? (
                        <mark
                          key={i}
                          className="bg-yellow-200 text-yellow-900 px-0.5 rounded"
                        >
                          {part.text}
                        </mark>
                      ) : (
                        <span key={i}>{part.text}</span>
                      )
                    ))}
                  </p>
                )}

                {/* Expand/Collapse button */}
                {isLong && (
                  <button
                    onClick={() => toggleExpanded(index)}
                    className="mt-2 flex items-center gap-1 text-xs text-primary-600 hover:text-primary-700 font-medium transition-colors"
                    aria-label={isExpanded ? 'Show less' : 'Show more'}
                  >
                    {isExpanded ? (
                      <>
                        <span>Show less</span>
                        <ChevronUp size={14} />
                      </>
                    ) : (
                      <>
                        <span>Show more</span>
                        <ChevronDown size={14} />
                      </>
                    )}
                  </button>
                )}
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}
