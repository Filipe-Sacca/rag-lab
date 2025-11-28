import { useState } from 'react'
import { Send, Loader2 } from 'lucide-react'

interface QueryInputProps {
  onSubmit: (query: string) => void
  isLoading?: boolean
  disabled?: boolean
}

export default function QueryInput({ onSubmit, isLoading = false, disabled = false }: QueryInputProps) {
  const [query, setQuery] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim() && !isLoading) {
      onSubmit(query.trim())
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="w-full">
      <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
        Your Question
      </label>
      <div className="relative">
        <textarea
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={disabled || isLoading}
          placeholder="Ask a question about your documents..."
          rows={5}
          className="w-full px-4 py-4 pr-14 border-2 border-gray-200 rounded-xl focus:outline-none focus:ring-4 focus:ring-gray-100 focus:border-gray-900 resize-none disabled:bg-gray-50 disabled:cursor-not-allowed transition-all text-gray-900 placeholder:text-gray-400"
        />
        <button
          type="submit"
          disabled={!query.trim() || isLoading || disabled}
          className="absolute bottom-4 right-4 p-3 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
        >
          {isLoading ? (
            <Loader2 className="animate-spin" size={20} />
          ) : (
            <Send size={20} />
          )}
        </button>
      </div>
      <p className="mt-2 text-xs text-gray-400">
        Press Enter to send, Shift+Enter for new line
      </p>
    </form>
  )
}
