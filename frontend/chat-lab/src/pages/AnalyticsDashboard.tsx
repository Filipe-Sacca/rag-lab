import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import DatePicker, { registerLocale } from 'react-datepicker'
import { ptBR } from 'date-fns/locale'
import 'react-datepicker/dist/react-datepicker.css'
import {
  BarChart3,
  FileDown,
  Loader2,
  ArrowLeft,
  Trophy,
  Clock,
  Target,
  Zap,
  Database,
  Brain,
  History,
  Calendar,
  ChevronDown,
  ChevronUp,
  Filter,
  Trash2
} from 'lucide-react'

// Register Portuguese locale
registerLocale('pt-BR', ptBR)
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
} from 'chart.js'
import { Bar, Radar } from 'react-chartjs-2'
import { analyticsService, type AnalysisResponse, type SavedAnalysis } from '../api/analytics.service'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler
)

export default function AnalyticsDashboard() {
  const [analysis, setAnalysis] = useState<AnalysisResponse | null>(null)
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const reportRef = useRef<HTMLDivElement>(null)

  // History states
  const [savedAnalyses, setSavedAnalyses] = useState<SavedAnalysis[]>([])
  const [historyLoading, setHistoryLoading] = useState(false)
  const [dateFrom, setDateFrom] = useState<Date | null>(null)
  const [dateTo, setDateTo] = useState<Date | null>(null)
  const [expandedAnalysis, setExpandedAnalysis] = useState<number | null>(null)
  const [totalAnalyses, setTotalAnalyses] = useState(0)

  // Load history on mount
  useEffect(() => {
    loadHistory()
  }, [])

  const loadHistory = async (from?: Date | null, to?: Date | null) => {
    setHistoryLoading(true)
    try {
      const params: any = { limit: 20 }
      if (from) {
        // Start of the day
        const startDate = new Date(from)
        startDate.setHours(0, 0, 0, 0)
        params.date_from = startDate.toISOString()
      }
      if (to) {
        // End of the day
        const endDate = new Date(to)
        endDate.setHours(23, 59, 59, 999)
        params.date_to = endDate.toISOString()
      }
      const result = await analyticsService.getAnalyses(params)
      setSavedAnalyses(result.analyses)
      setTotalAnalyses(result.total)
    } catch (err) {
      console.error('Failed to load history:', err)
    } finally {
      setHistoryLoading(false)
    }
  }

  const handleFilterHistory = () => {
    loadHistory(dateFrom, dateTo)
  }

  const handleClearFilter = () => {
    setDateFrom(null)
    setDateTo(null)
    loadHistory()
  }

  const handleDeleteAnalysis = async (id: number) => {
    if (!confirm('Tem certeza que deseja excluir esta análise?')) return
    try {
      await analyticsService.deleteAnalysis(id)
      loadHistory(dateFrom || undefined, dateTo || undefined)
    } catch (err) {
      console.error('Failed to delete:', err)
    }
  }

  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  }

  const handleAnalyze = async () => {
    setIsLoading(true)
    setError(null)
    try {
      const result = await analyticsService.analyze()
      setAnalysis(result)
      // Reload history to show the new saved analysis
      loadHistory(dateFrom, dateTo)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to generate analysis')
    } finally {
      setIsLoading(false)
    }
  }

  const handleExportPDF = async () => {
    if (!reportRef.current) return

    const html2pdf = (await import('html2pdf.js')).default
    const element = reportRef.current

    const opt = {
      margin: 10,
      filename: `rag-analysis-${new Date().toISOString().split('T')[0]}.pdf`,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { scale: 2 },
      jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
    }

    html2pdf().set(opt).from(element).save()
  }

  // Prepare chart data
  const getBarChartData = () => {
    if (!analysis) return null

    const techniques = Object.values(analysis.aggregated_data.techniques)
    const labels = techniques.map(t => t.technique.charAt(0).toUpperCase() + t.technique.slice(1))

    return {
      labels,
      datasets: [
        {
          label: 'Faithfulness',
          data: techniques.map(t => t.metrics.quality.faithfulness * 100),
          backgroundColor: 'rgba(34, 197, 94, 0.8)',
        },
        {
          label: 'Answer Relevancy',
          data: techniques.map(t => t.metrics.quality.answer_relevancy * 100),
          backgroundColor: 'rgba(59, 130, 246, 0.8)',
        },
        {
          label: 'Context Precision',
          data: techniques.map(t => t.metrics.quality.context_precision * 100),
          backgroundColor: 'rgba(168, 85, 247, 0.8)',
        },
        {
          label: 'Context Recall',
          data: techniques.map(t => t.metrics.quality.context_recall * 100),
          backgroundColor: 'rgba(249, 115, 22, 0.8)',
        },
      ],
    }
  }

  const getLatencyChartData = () => {
    if (!analysis) return null

    const techniques = Object.values(analysis.aggregated_data.techniques)
    const labels = techniques.map(t => t.technique.charAt(0).toUpperCase() + t.technique.slice(1))

    return {
      labels,
      datasets: [
        {
          label: 'Avg Latency (ms)',
          data: techniques.map(t => t.metrics.latency.avg_ms),
          backgroundColor: 'rgba(239, 68, 68, 0.8)',
        },
      ],
    }
  }

  const getRadarChartData = () => {
    if (!analysis) return null

    const techniques = Object.values(analysis.aggregated_data.techniques)
    const colors = [
      { bg: 'rgba(34, 197, 94, 0.2)', border: 'rgba(34, 197, 94, 1)' },
      { bg: 'rgba(59, 130, 246, 0.2)', border: 'rgba(59, 130, 246, 1)' },
      { bg: 'rgba(168, 85, 247, 0.2)', border: 'rgba(168, 85, 247, 1)' },
      { bg: 'rgba(249, 115, 22, 0.2)', border: 'rgba(249, 115, 22, 1)' },
      { bg: 'rgba(236, 72, 153, 0.2)', border: 'rgba(236, 72, 153, 1)' },
    ]

    return {
      labels: ['Faithfulness', 'Relevancy', 'Precision', 'Recall'],
      datasets: techniques.map((t, i) => ({
        label: t.technique.charAt(0).toUpperCase() + t.technique.slice(1),
        data: [
          t.metrics.quality.faithfulness,
          t.metrics.quality.answer_relevancy,
          t.metrics.quality.context_precision,
          t.metrics.quality.context_recall,
        ],
        backgroundColor: colors[i % colors.length].bg,
        borderColor: colors[i % colors.length].border,
        borderWidth: 2,
      })),
    }
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Link
                to="/"
                className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
              >
                <ArrowLeft size={20} className="text-gray-600" />
              </Link>
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gray-900 rounded-lg">
                  <BarChart3 className="text-white" size={24} />
                </div>
                <div>
                  <h1 className="text-xl font-semibold text-gray-900">
                    Analytics Dashboard
                  </h1>
                  <p className="text-xs text-gray-500">
                    Comparative analysis of RAG techniques
                  </p>
                </div>
              </div>
            </div>

            <div className="flex items-center gap-3">
              {analysis && (
                <button
                  onClick={handleExportPDF}
                  className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <FileDown size={18} />
                  Export PDF
                </button>
              )}
              <button
                onClick={handleAnalyze}
                disabled={isLoading}
                className="flex items-center gap-2 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {isLoading ? (
                  <Loader2 size={18} className="animate-spin" />
                ) : (
                  <Brain size={18} />
                )}
                {isLoading ? 'Analyzing...' : 'Generate Analysis'}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <p className="text-red-700">{error}</p>
          </div>
        )}

        {!analysis && !isLoading && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <Database size={48} className="mx-auto text-gray-300 mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              No Analysis Generated Yet
            </h2>
            <p className="text-gray-500 mb-6">
              Click "Generate Analysis" to aggregate all execution data and get AI-powered insights.
            </p>
            <button
              onClick={handleAnalyze}
              className="inline-flex items-center gap-2 px-6 py-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 transition-colors"
            >
              <Brain size={20} />
              Generate Analysis
            </button>
          </div>
        )}

        {isLoading && (
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-12 text-center">
            <Loader2 size={48} className="mx-auto text-gray-400 animate-spin mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">
              Generating Analysis...
            </h2>
            <p className="text-gray-500">
              Aggregating data and consulting AI analyst. This may take a few seconds.
            </p>
          </div>
        )}

        {analysis && (
          <div ref={reportRef} className="space-y-6">
            {/* Summary Cards */}
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-blue-50 rounded-lg">
                    <Database size={20} className="text-blue-600" />
                  </div>
                  <span className="text-sm text-gray-500">Total Executions</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {analysis.aggregated_data.total_executions}
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-purple-50 rounded-lg">
                    <Zap size={20} className="text-purple-600" />
                  </div>
                  <span className="text-sm text-gray-500">Techniques</span>
                </div>
                <p className="text-2xl font-bold text-gray-900">
                  {analysis.aggregated_data.techniques_count}
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-green-50 rounded-lg">
                    <Trophy size={20} className="text-green-600" />
                  </div>
                  <span className="text-sm text-gray-500">Best Quality</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 capitalize">
                  {analysis.rankings?.most_faithful?.[0] || '-'}
                </p>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4">
                <div className="flex items-center gap-3 mb-2">
                  <div className="p-2 bg-orange-50 rounded-lg">
                    <Clock size={20} className="text-orange-600" />
                  </div>
                  <span className="text-sm text-gray-500">Fastest</span>
                </div>
                <p className="text-2xl font-bold text-gray-900 capitalize">
                  {analysis.rankings?.fastest?.[0] || '-'}
                </p>
              </div>
            </div>

            {/* Charts Row */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Quality Metrics Bar Chart */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <Target size={20} className="text-gray-400" />
                  Quality Metrics by Technique
                </h3>
                <div className="h-72">
                  {getBarChartData() && (
                    <Bar
                      data={getBarChartData()!}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                          y: {
                            beginAtZero: true,
                            max: 100,
                            ticks: {
                              callback: (value) => `${value}%`,
                            },
                          },
                        },
                        plugins: {
                          legend: {
                            position: 'bottom',
                          },
                        },
                      }}
                    />
                  )}
                </div>
              </div>

              {/* Radar Chart */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <BarChart3 size={20} className="text-gray-400" />
                  Technique Comparison Radar
                </h3>
                <div className="h-72">
                  {getRadarChartData() && (
                    <Radar
                      data={getRadarChartData()!}
                      options={{
                        responsive: true,
                        maintainAspectRatio: false,
                        scales: {
                          r: {
                            beginAtZero: true,
                            max: 1,
                            ticks: {
                              stepSize: 0.2,
                            },
                          },
                        },
                        plugins: {
                          legend: {
                            position: 'bottom',
                          },
                        },
                      }}
                    />
                  )}
                </div>
              </div>
            </div>

            {/* Latency Chart */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Clock size={20} className="text-gray-400" />
                Average Latency by Technique
              </h3>
              <div className="h-48">
                {getLatencyChartData() && (
                  <Bar
                    data={getLatencyChartData()!}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      indexAxis: 'y',
                      scales: {
                        x: {
                          beginAtZero: true,
                          ticks: {
                            callback: (value) => `${value}ms`,
                          },
                        },
                      },
                      plugins: {
                        legend: {
                          display: false,
                        },
                      },
                    }}
                  />
                )}
              </div>
            </div>

            {/* Rankings */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Trophy size={20} className="text-gray-400" />
                Rankings by Metric
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
                {[
                  { key: 'fastest', label: 'Fastest', icon: Clock },
                  { key: 'most_faithful', label: 'Most Faithful', icon: Target },
                  { key: 'most_relevant', label: 'Most Relevant', icon: Zap },
                  { key: 'best_precision', label: 'Best Precision', icon: Target },
                  { key: 'best_recall', label: 'Best Recall', icon: Database },
                  { key: 'best_chunk_scores', label: 'Best Retrieval', icon: BarChart3 },
                ].filter(({ key }) => analysis.rankings?.[key as keyof typeof analysis.rankings]?.length).map(({ key, label, icon: Icon }) => (
                  <div key={key} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex items-center gap-2 mb-3">
                      <Icon size={16} className="text-gray-400" />
                      <span className="text-sm font-medium text-gray-700">{label}</span>
                    </div>
                    <ol className="space-y-1">
                      {(analysis.rankings?.[key as keyof typeof analysis.rankings] || []).map((technique, i) => (
                        <li key={technique} className="flex items-center gap-2 text-sm">
                          <span className={`w-5 h-5 rounded-full flex items-center justify-center text-xs font-bold ${
                            i === 0 ? 'bg-yellow-400 text-yellow-900' :
                            i === 1 ? 'bg-gray-300 text-gray-700' :
                            i === 2 ? 'bg-orange-300 text-orange-900' :
                            'bg-gray-100 text-gray-500'
                          }`}>
                            {i + 1}
                          </span>
                          <span className="capitalize text-gray-700">{technique}</span>
                        </li>
                      ))}
                    </ol>
                  </div>
                ))}
              </div>
            </div>

            {/* LLM Analysis */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                <Brain size={20} className="text-gray-400" />
                AI Analysis
              </h3>
              <div className="prose prose-gray max-w-none">
                <div className="bg-gray-50 rounded-lg p-6 whitespace-pre-wrap text-gray-700 leading-relaxed">
                  {analysis.llm_analysis}
                </div>
              </div>
            </div>

            {/* Detailed Data Table */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">Detailed Metrics</h3>
              </div>
              <div className="overflow-x-auto">
                <table className="w-full">
                  <thead>
                    <tr className="bg-gray-50">
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Technique</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Executions</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Avg Latency</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Faithfulness</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Relevancy</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Precision</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Recall</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Avg Chunks</th>
                      <th className="px-4 py-3 text-left text-xs font-medium text-gray-700 uppercase">Top Scores</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {Object.values(analysis.aggregated_data.techniques).map((tech) => (
                      <tr key={tech.technique} className="hover:bg-gray-50">
                        <td className="px-4 py-3 font-medium text-gray-900 capitalize">{tech.technique}</td>
                        <td className="px-4 py-3 text-gray-600">{tech.total_executions}</td>
                        <td className="px-4 py-3 text-gray-600">{tech.metrics.latency.avg_ms.toFixed(0)}ms</td>
                        <td className="px-4 py-3 text-gray-600">{(tech.metrics.quality.faithfulness * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3 text-gray-600">{(tech.metrics.quality.answer_relevancy * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3 text-gray-600">{(tech.metrics.quality.context_precision * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3 text-gray-600">{(tech.metrics.quality.context_recall * 100).toFixed(1)}%</td>
                        <td className="px-4 py-3 text-gray-600">{tech.metrics.retrieval.avg_chunks.toFixed(1)}</td>
                        <td className="px-4 py-3 text-gray-600">
                          {tech.metrics.retrieval.top_scores?.avg_top3_mean != null ? (
                            <span title={`#1: ${tech.metrics.retrieval.top_scores.avg_top1?.toFixed(3) ?? 'N/A'}, #2: ${tech.metrics.retrieval.top_scores.avg_top2?.toFixed(3) ?? 'N/A'}, #3: ${tech.metrics.retrieval.top_scores.avg_top3?.toFixed(3) ?? 'N/A'}`}>
                              {tech.metrics.retrieval.top_scores.avg_top3_mean.toFixed(3)}
                            </span>
                          ) : '-'}
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}

        {/* Analysis History Section */}
        <div className="mt-8 bg-white rounded-lg shadow-sm border border-gray-200">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
              <History size={20} className="text-gray-400" />
              Histórico de Análises ({totalAnalyses})
            </h3>
          </div>

          {/* Date Filter */}
          <div className="px-6 py-5 bg-gradient-to-r from-slate-50 via-gray-50 to-slate-50 border-b border-gray-200">
            <div className="flex flex-wrap items-center gap-6">
              <div className="flex items-center gap-3">
                <div className="p-2.5 bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl shadow-md">
                  <Calendar size={18} className="text-white" />
                </div>
                <div>
                  <span className="text-sm font-semibold text-gray-800">Filtrar Período</span>
                  <p className="text-xs text-gray-500">Selecione o intervalo de datas</p>
                </div>
              </div>

              <div className="flex items-center gap-4">
                <div className="relative">
                  <span className="absolute -top-2.5 left-3 px-2 bg-white text-xs font-medium text-gray-500 z-10">
                    Data Inicial
                  </span>
                  <DatePicker
                    selected={dateFrom}
                    onChange={(date) => setDateFrom(date)}
                    selectsStart
                    startDate={dateFrom}
                    endDate={dateTo}
                    locale="pt-BR"
                    dateFormat="dd/MM/yyyy"
                    placeholderText="Selecionar..."
                    isClearable
                    className="w-44 px-4 py-3 text-sm border-2 border-gray-200 rounded-xl bg-white
                             hover:border-gray-300 focus:border-gray-900 focus:ring-0
                             transition-all cursor-pointer shadow-sm"
                    calendarClassName="shadow-2xl rounded-xl border-0"
                    popperClassName="z-50"
                    showPopperArrow={false}
                  />
                </div>

                <div className="flex items-center gap-1">
                  <div className="w-3 h-0.5 bg-gray-300 rounded" />
                  <div className="w-2 h-0.5 bg-gray-400 rounded" />
                  <div className="w-3 h-0.5 bg-gray-300 rounded" />
                </div>

                <div className="relative">
                  <span className="absolute -top-2.5 left-3 px-2 bg-white text-xs font-medium text-gray-500 z-10">
                    Data Final
                  </span>
                  <DatePicker
                    selected={dateTo}
                    onChange={(date) => setDateTo(date)}
                    selectsEnd
                    startDate={dateFrom}
                    endDate={dateTo}
                    minDate={dateFrom}
                    locale="pt-BR"
                    dateFormat="dd/MM/yyyy"
                    placeholderText="Selecionar..."
                    isClearable
                    className="w-44 px-4 py-3 text-sm border-2 border-gray-200 rounded-xl bg-white
                             hover:border-gray-300 focus:border-gray-900 focus:ring-0
                             transition-all cursor-pointer shadow-sm"
                    calendarClassName="shadow-2xl rounded-xl border-0"
                    popperClassName="z-50"
                    showPopperArrow={false}
                  />
                </div>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={handleFilterHistory}
                  className="flex items-center gap-2 px-5 py-3 bg-gradient-to-r from-gray-800 to-gray-900
                           text-white text-sm font-semibold rounded-xl shadow-md
                           hover:from-gray-700 hover:to-gray-800 hover:shadow-lg
                           transition-all duration-200 active:scale-95"
                >
                  <Filter size={16} />
                  Aplicar Filtro
                </button>
                {(dateFrom || dateTo) && (
                  <button
                    onClick={handleClearFilter}
                    className="px-4 py-3 text-sm font-medium text-gray-600 hover:text-gray-900
                             bg-white hover:bg-gray-50 rounded-xl transition-all
                             border border-gray-200 hover:border-gray-300 shadow-sm"
                  >
                    Limpar
                  </button>
                )}
              </div>
            </div>
          </div>

          {/* History List */}
          <div className="divide-y divide-gray-200 max-h-96 overflow-y-auto">
            {historyLoading ? (
              <div className="px-6 py-8 text-center">
                <Loader2 size={24} className="mx-auto text-gray-400 animate-spin" />
              </div>
            ) : savedAnalyses.length === 0 ? (
              <div className="px-6 py-8 text-center text-gray-500">
                Nenhuma análise encontrada
              </div>
            ) : (
              savedAnalyses.map((item) => (
                <div key={item.id} className="hover:bg-gray-50">
                  <div
                    className="px-6 py-4 cursor-pointer"
                    onClick={() => setExpandedAnalysis(expandedAnalysis === item.id ? null : item.id)}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-1">
                          <span className="text-xs text-gray-400">{formatDate(item.created_at)}</span>
                          <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">
                            {item.iterations} tool{item.iterations !== 1 ? 's' : ''}
                          </span>
                          <span className="text-xs text-gray-400">{item.duration_ms?.toFixed(0)}ms</span>
                        </div>
                        <p className="font-medium text-gray-900">{item.question}</p>
                      </div>
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={(e) => { e.stopPropagation(); handleDeleteAnalysis(item.id) }}
                          className="p-1 text-gray-400 hover:text-red-500"
                        >
                          <Trash2 size={16} />
                        </button>
                        {expandedAnalysis === item.id ? <ChevronUp size={20} /> : <ChevronDown size={20} />}
                      </div>
                    </div>
                  </div>
                  {expandedAnalysis === item.id && (
                    <div className="px-6 pb-4 bg-gray-50 border-t border-gray-100">
                      <div className="pt-4 space-y-4">
                        {/* Analysis Data - Rankings & Metrics */}
                        {item.analysis_data && (
                          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
                            {/* Rankings */}
                            {item.analysis_data.rankings && (
                              <div className="bg-white rounded-lg p-4 border">
                                <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                                  <Trophy size={16} className="text-yellow-500" />
                                  Rankings
                                </h4>
                                <div className="grid grid-cols-2 gap-3 text-sm">
                                  <div>
                                    <span className="text-gray-500">Mais rápido:</span>
                                    <p className="font-medium capitalize">{item.analysis_data.rankings.fastest?.[0] || '-'}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Mais fiel:</span>
                                    <p className="font-medium capitalize">{item.analysis_data.rankings.most_faithful?.[0] || '-'}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Mais relevante:</span>
                                    <p className="font-medium capitalize">{item.analysis_data.rankings.most_relevant?.[0] || '-'}</p>
                                  </div>
                                  <div>
                                    <span className="text-gray-500">Melhor precisão:</span>
                                    <p className="font-medium capitalize">{item.analysis_data.rankings.best_precision?.[0] || '-'}</p>
                                  </div>
                                </div>
                              </div>
                            )}

                            {/* Aggregated Stats */}
                            {item.analysis_data.aggregated_data && (
                              <div className="bg-white rounded-lg p-4 border">
                                <h4 className="font-semibold text-gray-800 mb-3 flex items-center gap-2">
                                  <BarChart3 size={16} className="text-blue-500" />
                                  Estatísticas ({item.analysis_data.aggregated_data.total_executions} execuções)
                                </h4>
                                <div className="space-y-2 text-sm max-h-32 overflow-y-auto">
                                  {Object.values(item.analysis_data.aggregated_data.techniques || {}).map((tech: any) => (
                                    <div key={tech.technique} className="flex justify-between items-center py-1 border-b border-gray-100 last:border-0">
                                      <span className="capitalize font-medium">{tech.technique}</span>
                                      <div className="flex gap-3 text-xs text-gray-500">
                                        <span>{tech.metrics?.latency?.avg_ms?.toFixed(0)}ms</span>
                                        <span>F:{(tech.metrics?.quality?.faithfulness * 100)?.toFixed(0)}%</span>
                                        <span>R:{(tech.metrics?.quality?.answer_relevancy * 100)?.toFixed(0)}%</span>
                                      </div>
                                    </div>
                                  ))}
                                </div>
                              </div>
                            )}
                          </div>
                        )}

                        {/* LLM Response */}
                        <div className="bg-white rounded-lg p-4 text-sm whitespace-pre-wrap border">{item.response}</div>

                        {/* Tool calls */}
                        {item.tool_calls?.length > 0 && (
                          <div className="flex gap-2">
                            {item.tool_calls.map((tc, i) => (
                              <span key={i} className="px-2 py-1 bg-gray-200 text-xs rounded">{tc.tool}</span>
                            ))}
                          </div>
                        )}
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </main>
    </div>
  )
}
