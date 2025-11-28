import api from './client'
import type {
  RAGTechnique,
  QueryRequest,
  QueryResponse,
  CompareRequest,
  ComparisonResult
} from '../types/rag.types'

export const ragService = {
  async getTechniques(): Promise<RAGTechnique[]> {
    const { data } = await api.get('/api/v1/techniques')
    return data
  },

  async query(request: QueryRequest): Promise<QueryResponse> {
    const { data } = await api.post('/api/v1/query', request)

    // Return backend response directly (it already matches our types)
    return data
  },

  async compare(request: CompareRequest): Promise<ComparisonResult> {
    const { data } = await api.post('/api/v1/compare', request)
    return data
  },

  async health() {
    const { data } = await api.get('/health')
    return data
  }
}
