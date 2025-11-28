import { useState, useEffect } from 'react'
import api from '../api/client'
import type { ComparisonData } from '../types/comparison.types'

interface UseComparisonReturn {
  data: ComparisonData[]
  loading: boolean
  error: string | null
  refresh: () => Promise<void>
}

export const useComparison = (): UseComparisonReturn => {
  const [data, setData] = useState<ComparisonData[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  const fetchData = async () => {
    try {
      setLoading(true)
      const response = await api.get('/api/v1/comparison-data')
      setData(response.data)
      setError(null)
    } catch (err: any) {
      const message = err.response?.data?.detail || err.message || 'Failed to fetch comparison data'
      setError(message)
      console.error('Comparison data fetch error:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchData()

    // Auto-refresh every 5 seconds
    const interval = setInterval(fetchData, 5000)
    return () => clearInterval(interval)
  }, [])

  return { data, loading, error, refresh: fetchData }
}
