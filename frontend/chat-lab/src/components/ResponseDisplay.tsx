import { QueryResponse } from '../types/rag.types'
import { MessageSquare, Sparkles } from 'lucide-react'

interface ResponseDisplayProps {
  response: QueryResponse | null
}

export default function ResponseDisplay({ response }: ResponseDisplayProps) {
  if (!response) {
    return (
      <div className="bg-gray-50 rounded-lg p-8 text-center">
        <MessageSquare className="mx-auto mb-3 text-gray-400" size={48} />
        <p className="text-gray-500">No response yet. Ask a question to get started.</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Query Display */}
      <div className="bg-primary-50 border border-primary-200 rounded-lg p-4">
        <h3 className="text-sm font-medium text-primary-900 mb-2">Your Question</h3>
        <p className="text-primary-800">{response.query}</p>
      </div>

      {/* Answer Display */}
      <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Sparkles size={16} className="text-primary-500" />
            <h3 className="text-sm font-medium text-gray-900">Answer</h3>
          </div>
          <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
            {response.technique}
          </span>
        </div>
        <div className="prose prose-sm max-w-none">
          <p className="text-gray-800 whitespace-pre-wrap">{response.answer}</p>
        </div>
      </div>
    </div>
  )
}
