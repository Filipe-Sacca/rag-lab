import { useState } from 'react'
import { RAGTechnique } from '../types/rag.types'
import { ChevronDown, Clock, DollarSign, Layers, Check, AlertTriangle } from 'lucide-react'

interface TechniqueSelectorProps {
  techniques: RAGTechnique[]
  selectedTechnique: string
  onSelect: (techniqueId: string) => void
  disabled?: boolean
}

export default function TechniqueSelector({
  techniques,
  selectedTechnique,
  onSelect,
  disabled = false
}: TechniqueSelectorProps) {
  const [isOpen, setIsOpen] = useState(false)
  const selected = techniques.find(t => t.id === selectedTechnique)

  const getComplexityBars = (complexity: string) => {
    const levels = { low: 1, medium: 2, high: 3, very_high: 4 }
    const level = levels[complexity as keyof typeof levels] || 1
    return (
      <div className="flex gap-0.5">
        {[1, 2, 3, 4].map((i) => (
          <div
            key={i}
            className={`w-1.5 h-3 rounded-sm ${
              i <= level ? 'bg-gray-900' : 'bg-gray-200'
            }`}
          />
        ))}
      </div>
    )
  }

  return (
    <div className="w-full">
      <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
        Select Technique
      </label>

      {/* Custom Dropdown Button */}
      <button
        type="button"
        onClick={() => !disabled && setIsOpen(!isOpen)}
        disabled={disabled}
        className={`w-full text-left bg-white border-2 rounded-xl px-4 py-3 transition-all ${
          isOpen ? 'border-gray-900 ring-4 ring-gray-100' : 'border-gray-200 hover:border-gray-300'
        } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
              selected?.implemented ? 'bg-gray-900 text-white' : 'bg-gray-200 text-gray-500'
            }`}>
              <Layers size={20} />
            </div>
            <div>
              <div className="font-semibold text-gray-900">
                {selected?.name || 'Select...'}
              </div>
              <div className="text-xs text-gray-500 truncate max-w-[200px]">
                {selected?.description || 'Choose a RAG technique'}
              </div>
            </div>
          </div>
          <ChevronDown
            className={`text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`}
            size={20}
          />
        </div>
      </button>

      {/* Dropdown Panel */}
      {isOpen && (
        <div className="absolute z-50 mt-2 w-full max-w-md bg-white border border-gray-200 rounded-xl shadow-xl overflow-hidden">
          <div className="max-h-96 overflow-y-auto">
            {techniques.map((technique) => (
              <button
                key={technique.id}
                onClick={() => {
                  if (technique.implemented) {
                    onSelect(technique.id)
                    setIsOpen(false)
                  }
                }}
                disabled={!technique.implemented}
                className={`w-full text-left px-4 py-3 border-b border-gray-100 last:border-0 transition-colors ${
                  selectedTechnique === technique.id
                    ? 'bg-gray-50'
                    : technique.implemented
                    ? 'hover:bg-gray-50'
                    : 'opacity-50 cursor-not-allowed'
                }`}
              >
                <div className="flex items-start gap-3">
                  {/* Selection indicator */}
                  <div className={`mt-0.5 w-5 h-5 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                    selectedTechnique === technique.id
                      ? 'border-gray-900 bg-gray-900'
                      : 'border-gray-300'
                  }`}>
                    {selectedTechnique === technique.id && (
                      <Check size={12} className="text-white" />
                    )}
                  </div>

                  {/* Content */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-900">{technique.name}</span>
                      {!technique.implemented && (
                        <span className="flex items-center gap-1 text-xs text-amber-600 bg-amber-50 px-1.5 py-0.5 rounded">
                          <AlertTriangle size={10} />
                          Soon
                        </span>
                      )}
                    </div>
                    <p className="text-xs text-gray-500 mt-0.5 line-clamp-1">
                      {technique.description}
                    </p>

                    {/* Stats */}
                    <div className="flex items-center gap-4 mt-2">
                      <div className="flex items-center gap-1.5 text-xs text-gray-400">
                        <Clock size={12} />
                        <span>{technique.avg_latency_ms}ms</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-gray-400">
                        <DollarSign size={12} />
                        <span>${technique.avg_cost_usd.toFixed(3)}</span>
                      </div>
                      <div className="flex items-center gap-1.5 text-xs text-gray-400">
                        <span>Complexity</span>
                        {getComplexityBars(technique.complexity)}
                      </div>
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Selected technique detail card */}
      {selected && !isOpen && (
        <div className="mt-3 p-4 bg-gray-50 rounded-xl border border-gray-100">
          <div className="flex items-center justify-between gap-4">
            <div className="flex items-center gap-4 text-sm">
              <div className="flex items-center gap-1.5 text-gray-600">
                <Clock size={14} className="text-gray-400" />
                <span>{selected.avg_latency_ms}ms</span>
              </div>
              <div className="flex items-center gap-1.5 text-gray-600">
                <DollarSign size={14} className="text-gray-400" />
                <span>${selected.avg_cost_usd.toFixed(3)}</span>
              </div>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500">Complexity</span>
              {getComplexityBars(selected.complexity)}
            </div>
          </div>
        </div>
      )}

      {/* Overlay to close dropdown */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  )
}
