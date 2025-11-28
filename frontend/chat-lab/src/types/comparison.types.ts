export interface TopScores {
  top1: number | null
  top2: number | null
  top3: number | null
  avg: number | null
}

export interface ComparisonData {
  technique: string
  precision: number
  recall: number
  latency_ms: number
  answer: string
  query: string
  created_at: string
  faithfulness: number
  answer_relevancy: number
  chunks_retrieved: number
  top_scores: TopScores | null
}
