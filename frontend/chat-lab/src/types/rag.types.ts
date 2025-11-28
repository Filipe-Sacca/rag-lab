export interface RAGTechnique {
  id: string
  name: string
  description: string
  implemented: boolean
  complexity: 'low' | 'medium' | 'high' | 'very_high'
  avg_latency_ms: number
  avg_cost_usd: number
}

export interface QueryRequest {
  query: string
  technique: string
  top_k?: number
  namespace?: string
  params?: {
    top_k?: number
    temperature?: number
    max_tokens?: number
  }
}

export interface Source {
  content: string
  score: number
  original_score?: number  // Original bi-encoder score (before reranking)
  metadata: {
    document: string
    page: number
    chunk_id: string
  }
}

export interface Metrics {
  latency_ms: number
  tokens_input: number
  tokens_output: number
  tokens_total: number
  cost_usd: number
  chunks_retrieved: number
  chunks_used: number
}

export interface RAGASScores {
  faithfulness: number
  answer_relevancy: number
  context_precision: number
  context_recall: number
}

export interface ExecutionStep {
  step: string
  duration_ms: number
  [key: string]: any  // Dynamic fields like num_docs, components, etc.
}

export interface ExecutionDetails {
  technique: string
  steps: ExecutionStep[]
  [key: string]: any  // Dynamic fields like query_entities, hypothesis, etc.
}

export interface QueryResponse {
  query: string
  answer: string
  technique: string
  retrieved_docs: string[]
  metrics: {
    latency_ms: number
    latency_seconds: number
    tokens: {
      input: number
      output: number
      total: number
    }
    cost: {
      input_usd: number
      output_usd: number
      total_usd: number
    }
    chunks_retrieved: number
    technique: string
    faithfulness: number
    answer_relevancy: number
    context_precision: number | null
    context_recall: number | null
  } | null
  metadata: {
    top_k: number
    num_docs_retrieved: number
    execution_details: ExecutionDetails
    execution_id: number | null
    sources?: Source[]  // Add sources with scores and metadata
  }
}

export interface CompareRequest {
  query: string
  techniques: string[]
  params?: {
    top_k?: number
    temperature?: number
  }
}

export interface ComparisonResult {
  query: string
  results: QueryResponse[]
  comparison: {
    fastest: string
    cheapest: string
    best_faithfulness: string
    best_relevancy: string
    best_precision: string
    best_recall: string
  }
  total_time_ms: number
  total_cost_usd: number
}
