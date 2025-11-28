import api from './client'

export interface TechniqueMetrics {
  latency: {
    avg_ms: number
    min_ms: number
    max_ms: number
  }
  quality: {
    faithfulness: number
    answer_relevancy: number
    context_precision: number
    context_recall: number
  }
  retrieval: {
    avg_chunks: number
    total_chunks: number
    top_scores?: {
      avg_top1: number
      avg_top2: number
      avg_top3: number
      avg_top3_mean: number
    }
  }
}

export interface TechniqueData {
  technique: string
  total_executions: number
  metrics: TechniqueMetrics
}

export interface AggregatedStats {
  total_executions: number
  techniques_count: number
  techniques: Record<string, TechniqueData>
}

export interface Rankings {
  fastest: string[]
  most_faithful: string[]
  most_relevant: string[]
  best_precision: string[]
  best_recall: string[]
  best_chunk_scores?: string[]
}

export interface AnalysisResponse {
  aggregated_data: AggregatedStats
  rankings: Rankings
  llm_analysis: string
}

// Agent Analysis History Types
export interface SavedAnalysis {
  id: number
  question: string
  response: string
  analysis_data?: {
    aggregated_data?: AggregatedStats
    rankings?: Rankings
  }
  tool_calls: Array<{ tool: string; result_preview: string }>
  iterations: number
  duration_ms: number
  created_at: string
}

export interface AnalysesListResponse {
  total: number
  limit: number
  offset: number
  analyses: SavedAnalysis[]
}

export interface AnalysesSummary {
  total_analyses: number
  avg_iterations: number
  avg_duration_ms: number | null
  date_range: {
    oldest: string | null
    newest: string | null
  }
}

export const analyticsService = {
  async getStats(): Promise<AggregatedStats> {
    const { data } = await api.get('/api/v1/analytics/stats')
    return data
  },

  async getRankings(): Promise<Rankings> {
    const { data } = await api.get('/api/v1/analytics/rankings')
    return data
  },

  async analyze(): Promise<AnalysisResponse> {
    const { data } = await api.post('/api/v1/analytics/analyze')
    return data
  },

  // Agent Analysis History
  async getAnalyses(params?: {
    date_from?: string
    date_to?: string
    limit?: number
    offset?: number
  }): Promise<AnalysesListResponse> {
    const { data } = await api.get('/api/v1/analytics/analyses', { params })
    return data
  },

  async getAnalysesSummary(): Promise<AnalysesSummary> {
    const { data } = await api.get('/api/v1/analytics/analyses/summary')
    return data
  },

  async getAnalysisById(id: number): Promise<SavedAnalysis> {
    const { data } = await api.get(`/api/v1/analytics/analyses/${id}`)
    return data
  },

  async deleteAnalysis(id: number): Promise<void> {
    await api.delete(`/api/v1/analytics/analyses/${id}`)
  }
}
