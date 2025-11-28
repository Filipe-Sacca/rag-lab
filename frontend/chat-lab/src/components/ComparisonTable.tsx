import React, { useState } from 'react'
import { RefreshCw, AlertCircle, Database, ChevronDown, ChevronUp, BarChart3 } from 'lucide-react'
import { useComparison } from '../hooks/useComparison'
import MetricsBarChart from './MetricsBarChart'

export const ComparisonTable: React.FC = () => {
  const { data, loading, error, refresh } = useComparison()
  const [expandedRows, setExpandedRows] = useState<Set<number>>(new Set())

  const toggleRow = (index: number) => {
    const newExpanded = new Set(expandedRows)
    if (newExpanded.has(index)) {
      newExpanded.delete(index)
    } else {
      newExpanded.add(index)
    }
    setExpandedRows(newExpanded)
  }

  const handleRefresh = () => {
    refresh()
  }

  // Color coding for metric values
  const getScoreColor = (score: number | null): string => {
    if (score === null) return 'text-gray-400'
    if (score >= 0.8) return 'text-green-600'
    if (score >= 0.6) return 'text-yellow-600'
    if (score >= 0.4) return 'text-orange-500'
    return 'text-red-500'
  }

  const formatScore = (score: number | null): string => {
    if (score === null) return 'N/A'
    return (score * 100).toFixed(0) + '%'
  }

  if (loading && data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex items-center justify-center gap-3">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-500" />
          <span className="text-gray-600">Loading comparison data...</span>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-start gap-3 mb-4">
          <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
          <div className="flex-1">
            <h3 className="font-medium text-red-900">Error Loading Comparison Data</h3>
            <p className="text-sm text-red-700 mt-1">{error}</p>
          </div>
        </div>
        <button
          onClick={handleRefresh}
          className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors flex items-center gap-2"
        >
          <RefreshCw size={16} />
          Try Again
        </button>
      </div>
    )
  }

  if (data.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-8">
        <div className="flex flex-col items-center justify-center gap-3 text-gray-500">
          <Database size={48} className="opacity-50" />
          <p className="text-center">
            No comparison data available yet.
            <br />
            <span className="text-sm">Execute queries to see technique comparisons.</span>
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200">
      {/* Header */}
      <div className="border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-bold text-gray-900">RAG Technique Comparison</h2>
            <p className="text-sm text-gray-600 mt-1">
              Comparing {data.length} execution{data.length !== 1 ? 's' : ''} across different techniques
            </p>
          </div>
          <button
            onClick={handleRefresh}
            disabled={loading}
            className="px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider w-10">
                {/* Expand column */}
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Technique
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Precision
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Recall
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Latency
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Faithfulness
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Relevancy
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Chunks
              </th>
              <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase tracking-wider">
                Top Scores
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {data.map((row, index) => {
              const isExpanded = expandedRows.has(index)
              return (
                <React.Fragment key={index}>
                  {/* Main row */}
                  <tr
                    className={`hover:bg-gray-50 transition-colors cursor-pointer ${
                      isExpanded ? 'bg-primary-50' : ''
                    }`}
                    onClick={() => toggleRow(index)}
                  >
                    <td className="px-4 py-3">
                      <button
                        className="p-1 rounded hover:bg-gray-200 transition-colors"
                        aria-label={isExpanded ? 'Collapse' : 'Expand'}
                      >
                        {isExpanded ? (
                          <ChevronUp size={18} className="text-primary-600" />
                        ) : (
                          <ChevronDown size={18} className="text-gray-400" />
                        )}
                      </button>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="font-medium text-gray-900">{row.technique}</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getScoreColor(row.precision)}`}>
                        {formatScore(row.precision)}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getScoreColor(row.recall)}`}>
                        {formatScore(row.recall)}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-600">
                        {row.latency_ms != null ? `${row.latency_ms.toFixed(0)}ms` : 'N/A'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getScoreColor(row.faithfulness)}`}>
                        {formatScore(row.faithfulness)}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`text-sm font-medium ${getScoreColor(row.answer_relevancy)}`}>
                        {formatScore(row.answer_relevancy)}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className="text-sm text-gray-600">
                        {row.chunks_retrieved || 'N/A'}
                      </span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {row.top_scores ? (
                        <div className="flex flex-col gap-0.5">
                          <div className="flex items-center gap-1 text-xs">
                            <span className="text-gray-400 w-4">#1</span>
                            <span className={`font-medium ${getScoreColor(row.top_scores.top1)}`}>
                              {row.top_scores.top1 != null ? `${(row.top_scores.top1 * 100).toFixed(1)}%` : 'N/A'}
                            </span>
                          </div>
                          <div className="flex items-center gap-1 text-xs">
                            <span className="text-gray-400 w-4">#2</span>
                            <span className={`font-medium ${getScoreColor(row.top_scores.top2)}`}>
                              {row.top_scores.top2 != null ? `${(row.top_scores.top2 * 100).toFixed(1)}%` : 'N/A'}
                            </span>
                          </div>
                          <div className="flex items-center gap-1 text-xs">
                            <span className="text-gray-400 w-4">#3</span>
                            <span className={`font-medium ${getScoreColor(row.top_scores.top3)}`}>
                              {row.top_scores.top3 != null ? `${(row.top_scores.top3 * 100).toFixed(1)}%` : 'N/A'}
                            </span>
                          </div>
                        </div>
                      ) : (
                        <span className="text-sm text-gray-400">N/A</span>
                      )}
                    </td>
                  </tr>

                  {/* Expanded detail row */}
                  {isExpanded && (
                    <tr className="bg-gray-50">
                      <td colSpan={9} className="px-6 py-4">
                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                          {/* Left: Metrics Chart */}
                          <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <div className="flex items-center gap-2 mb-3">
                              <BarChart3 size={18} className="text-primary-600" />
                              <h4 className="font-medium text-gray-900">Quality Metrics</h4>
                            </div>
                            <MetricsBarChart
                              faithfulness={row.faithfulness}
                              answerRelevancy={row.answer_relevancy}
                              contextPrecision={row.precision}
                              contextRecall={row.recall}
                              latencyMs={row.latency_ms}
                              chunksRetrieved={row.chunks_retrieved}
                            />
                          </div>

                          {/* Right: Full Answer */}
                          <div className="bg-white rounded-lg border border-gray-200 p-4">
                            <h4 className="font-medium text-gray-900 mb-3">Full Answer</h4>
                            {row.query && (
                              <div className="mb-3 p-2 bg-primary-50 rounded-lg border border-primary-200">
                                <span className="text-xs text-primary-600 font-medium">Query:</span>
                                <p className="text-sm text-primary-800 mt-1">{row.query}</p>
                              </div>
                            )}
                            <div className="text-sm text-gray-700 whitespace-pre-wrap max-h-48 overflow-y-auto p-3 bg-gray-50 rounded-lg border border-gray-200">
                              {row.answer || 'No answer available'}
                            </div>
                            {row.created_at && (
                              <p className="text-xs text-gray-400 mt-2">
                                Executed: {new Date(row.created_at).toLocaleString()}
                              </p>
                            )}
                          </div>
                        </div>
                      </td>
                    </tr>
                  )}
                </React.Fragment>
              )
            })}
          </tbody>
        </table>
      </div>

      {/* Footer */}
      <div className="border-t border-gray-200 px-6 py-3 bg-gray-50">
        <div className="flex items-center justify-between text-sm text-gray-600">
          <span>Total executions: {data.length}</span>
          <span>Click a row to see details</span>
          <span className="text-xs">Auto-refresh: 5s</span>
        </div>
      </div>
    </div>
  )
}
