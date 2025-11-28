import { Layers } from 'lucide-react'

interface TopKSelectorProps {
  value: number
  onChange: (value: number) => void
  disabled?: boolean
}

export default function TopKSelector({ value, onChange, disabled = false }: TopKSelectorProps) {
  const presets = [3, 5, 10, 15, 20]

  return (
    <div className="w-full">
      <label className="block text-xs font-medium text-gray-500 uppercase tracking-wider mb-2">
        Chunks to Retrieve
      </label>

      <div className="flex items-center gap-4">
        {/* Slider */}
        <div className="flex-1">
          <input
            type="range"
            min={1}
            max={20}
            value={value}
            onChange={(e) => onChange(Number(e.target.value))}
            disabled={disabled}
            className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-gray-900 disabled:opacity-50 disabled:cursor-not-allowed"
          />
        </div>

        {/* Current Value Display */}
        <div className="flex items-center gap-2 px-3 py-2 bg-gray-900 text-white rounded-lg min-w-[60px] justify-center">
          <Layers size={14} />
          <span className="font-semibold">{value}</span>
        </div>
      </div>

      {/* Preset Buttons */}
      <div className="flex items-center gap-2 mt-3">
        <span className="text-xs text-gray-400">Quick:</span>
        {presets.map((preset) => (
          <button
            key={preset}
            onClick={() => onChange(preset)}
            disabled={disabled}
            className={`px-2.5 py-1 text-xs rounded-md transition-colors ${
              value === preset
                ? 'bg-gray-900 text-white'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            } disabled:opacity-50 disabled:cursor-not-allowed`}
          >
            {preset}
          </button>
        ))}
      </div>

      {/* Helper Text */}
      <p className="text-xs text-gray-400 mt-2">
        {value <= 3 && '🎯 Focused: Best for simple, specific questions'}
        {value > 3 && value <= 7 && '⚖️ Balanced: Good for most queries'}
        {value > 7 && value <= 12 && '📚 Comprehensive: Better coverage, higher cost'}
        {value > 12 && '🔍 Deep Search: Maximum context, highest latency'}
      </p>
    </div>
  )
}
