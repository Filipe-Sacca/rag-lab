import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { AlertCircle, FlaskConical, BarChart3 } from 'lucide-react'
import TechniqueSelector from './components/TechniqueSelector'
import TopKSelector from './components/TopKSelector'
import QueryInput from './components/QueryInput'
import ResponseDisplay from './components/ResponseDisplay'
import MetricsCard from './components/MetricsCard'
import SourcesList from './components/SourcesList'
import RAGASChart from './components/RAGASChart'
import ExecutionLogs from './components/ExecutionLogs'
import { ComparisonTable } from './components/ComparisonTable'
import { ragService } from './api/rag.service'
import type { RAGTechnique, QueryResponse } from './types/rag.types'

function App() {
  const [techniques, setTechniques] = useState<RAGTechnique[]>([])
  const [selectedTechnique, setSelectedTechnique] = useState<string>('')
  const [topK, setTopK] = useState<number>(5)
  const [response, setResponse] = useState<QueryResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking')
  const [currentQuery, setCurrentQuery] = useState<string>('')

  // Check backend health on mount
  useEffect(() => {
    checkBackendHealth()
  }, [])

  // Load techniques when backend is online
  useEffect(() => {
    if (backendStatus === 'online') {
      loadTechniques()
    }
  }, [backendStatus])

  const checkBackendHealth = async () => {
    try {
      await ragService.health()
      setBackendStatus('online')
    } catch (err) {
      setBackendStatus('offline')
      setError('Backend is offline. Please start the backend server.')
    }
  }

  const loadTechniques = async () => {
    try {
      const data = await ragService.getTechniques()
      setTechniques(data)
      if (data.length > 0) {
        setSelectedTechnique(data[0].id)
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load techniques')
    }
  }

  const handleQuery = async (query: string) => {
    setIsLoading(true)
    setError(null)
    setResponse(null)
    setCurrentQuery(query) // Store the current query for highlighting

    try {
      const result = await ragService.query({
        query,
        technique: selectedTechnique,
        top_k: topK,
        namespace: 'rag-docs',
        params: {
          top_k: topK,
          temperature: 0.7,
          max_tokens: 500
        }
      })
      console.log('🔍 Query Response:', result)
      console.log('📊 Metadata:', result.metadata)
      console.log('🎬 Execution Details:', result.metadata?.execution_details)
      setResponse(result)
    } catch (err: any) {
      if (err.response?.status === 501) {
        setError(`The technique "${selectedTechnique}" is not implemented yet. Please select another technique.`)
      } else {
        setError(err.response?.data?.detail || err.message || 'Failed to execute query')
      }
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            {/* Logo & Title */}
            <div className="flex items-center gap-3">
              <div className="p-2 bg-gray-900 rounded-lg">
                <FlaskConical className="text-white" size={24} />
              </div>
              <div>
                <h1 className="text-xl font-semibold text-gray-900 tracking-tight">
                  RAG Lab
                </h1>
                <p className="text-xs text-gray-500">
                  Compare RAG techniques
                </p>
              </div>
            </div>

            {/* Actions & Status */}
            <div className="flex items-center gap-4">
              {/* Analytics Button */}
              <Link
                to="/analytics"
                className="flex items-center gap-2 px-4 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                <BarChart3 size={18} className="text-gray-600" />
                <span className="text-sm font-medium text-gray-700">Analytics</span>
              </Link>

              {/* Status */}
              {backendStatus === 'online' && (
                <div className="flex items-center gap-2 px-3 py-1.5 text-sm">
                  <span className="h-2 w-2 bg-green-500 rounded-full"></span>
                  <span className="text-gray-600">Online</span>
                </div>
              )}
              {backendStatus === 'offline' && (
                <div className="flex items-center gap-2 px-3 py-1.5 text-sm text-red-600">
                  <span className="h-2 w-2 bg-red-500 rounded-full"></span>
                  <span>Offline</span>
                </div>
              )}
              {backendStatus === 'checking' && (
                <div className="flex items-center gap-2 px-3 py-1.5 text-sm text-gray-500">
                  <div className="animate-spin h-3 w-3 border-2 border-gray-300 border-t-gray-600 rounded-full" />
                  <span>Connecting...</span>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Error Alert */}
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
            <AlertCircle className="text-red-600 flex-shrink-0 mt-0.5" size={20} />
            <div>
              <h3 className="font-medium text-red-900">Error</h3>
              <p className="text-sm text-red-700 mt-1">{error}</p>
            </div>
          </div>
        )}

        {/* Input Section - Vertical Layout */}
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
          {/* Configuration Row - Technique + TopK */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            {/* Technique Selector */}
            <TechniqueSelector
              techniques={techniques}
              selectedTechnique={selectedTechnique}
              onSelect={setSelectedTechnique}
              disabled={isLoading || backendStatus !== 'online'}
            />

            {/* TopK Selector */}
            <TopKSelector
              value={topK}
              onChange={setTopK}
              disabled={isLoading || backendStatus !== 'online'}
            />
          </div>

          {/* Chat Input - Full Width Below */}
          <div className="w-full">
            <QueryInput
              onSubmit={handleQuery}
              isLoading={isLoading}
              disabled={backendStatus !== 'online'}
            />
          </div>
        </div>

        {/* Response Section - Right below chat */}
        {(response || isLoading) && (
          <div className="space-y-6 mb-6">
            {/* Loading or Response */}
            <div>
              {isLoading ? (
                <div className="bg-white rounded-lg p-8 text-center border border-gray-200">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900 mx-auto mb-4"></div>
                  <p className="text-gray-600">Processing your query...</p>
                </div>
              ) : (
                <ResponseDisplay response={response} />
              )}
            </div>

            {/* Metrics Cards */}
            {response && <MetricsCard metrics={response.metrics} />}

            {/* Sources */}
            {response && response.metadata?.sources && response.metadata.sources.length > 0 && (
              <SourcesList
                sources={response.metadata.sources}
                query={currentQuery}
              />
            )}
          </div>
        )}

        {/* RAGAS Chart & Execution Logs */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <RAGASChart
            scores={response?.metrics
              ? {
                  faithfulness: response.metrics.faithfulness,
                  answer_relevancy: response.metrics.answer_relevancy,
                  context_precision: response.metrics.context_precision || 0,
                  context_recall: response.metrics.context_recall || 0,
                }
              : undefined
            }
          />
          <ExecutionLogs executionDetails={response?.metadata?.execution_details || null} />
        </div>

        {/* Comparison Table - Always visible */}
        <div className="mb-6">
          <ComparisonTable />
        </div>
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <p className="text-center text-sm text-gray-500">
            RAG Lab — Compare and optimize RAG pipelines
          </p>
        </div>
      </footer>
    </div>
  )
}

export default App
