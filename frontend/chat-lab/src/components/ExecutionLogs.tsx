import { Code2, Clock, Layers } from 'lucide-react'

interface ExecutionStep {
  step: string
  duration_ms: number
  [key: string]: any
}

interface ExecutionLogsProps {
  executionDetails: {
    technique: string
    steps: ExecutionStep[]
    [key: string]: any
  } | null
}

export default function ExecutionLogs({ executionDetails }: ExecutionLogsProps) {
  if (!executionDetails || !executionDetails.steps || executionDetails.steps.length === 0) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
        <div className="flex items-center gap-2 mb-3">
          <Code2 className="text-gray-600" size={20} />
          <h3 className="text-sm font-medium text-gray-900">Execution Logs</h3>
        </div>
        <p className="text-gray-500 text-center py-8">
          No execution data available. Run a query to see detailed logs.
        </p>
      </div>
    )
  }

  const totalDuration = executionDetails.steps.reduce((sum, step) => sum + (step.duration_ms || 0), 0)

  return (
    <div className="bg-white border border-gray-200 rounded-lg shadow-sm">
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Code2 className="text-gray-600" size={20} />
            <h3 className="text-sm font-medium text-gray-900">Execution Logs</h3>
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              {executionDetails.technique || 'Unknown'}
            </span>
          </div>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <Clock size={16} />
            <span className="font-mono">{totalDuration.toFixed(0)}ms total</span>
          </div>
        </div>
      </div>

      {/* Steps List */}
      <div className="divide-y divide-gray-100">
        {executionDetails.steps.map((step, index) => (
          <div key={index} className="p-4 hover:bg-gray-50 transition-colors">
            <div className="flex items-start justify-between gap-4">
              {/* Step Info */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <span className="flex-shrink-0 w-6 h-6 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-xs font-medium">
                    {index + 1}
                  </span>
                  <h4 className="text-sm font-medium text-gray-900 truncate">
                    {step.step.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </h4>
                </div>

                {/* Step Details */}
                <div className="ml-8 space-y-1">
                  {Object.entries(step).map(([key, value]) => {
                    // Skip the "step" and "duration_ms" keys as they're shown above
                    if (key === 'step' || key === 'duration_ms') return null

                    // Format the value based on type
                    let displayValue: string
                    if (Array.isArray(value)) {
                      displayValue = value.length > 0
                        ? `[${value.length} items: ${value.slice(0, 3).join(', ')}${value.length > 3 ? '...' : ''}]`
                        : '[]'
                    } else if (typeof value === 'object' && value !== null) {
                      displayValue = JSON.stringify(value, null, 2)
                    } else {
                      displayValue = String(value)
                    }

                    return (
                      <div key={key} className="text-xs">
                        <span className="text-gray-500">{key.replace(/_/g, ' ')}:</span>{' '}
                        <span className="text-gray-700 font-mono">{displayValue}</span>
                      </div>
                    )
                  })}
                </div>
              </div>

              {/* Duration Badge */}
              <div className="flex-shrink-0">
                <div className="text-right">
                  <div className="text-xs font-mono text-gray-600">
                    {step.duration_ms.toFixed(1)}ms
                  </div>
                  <div className="w-24 h-2 bg-gray-200 rounded-full mt-1 overflow-hidden">
                    <div
                      className="h-full bg-primary-500 rounded-full transition-all"
                      style={{ width: `${(step.duration_ms / totalDuration) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Additional Details Footer */}
      {Object.keys(executionDetails).filter(key =>
        key !== 'steps' && key !== 'technique'
      ).length > 0 && (
        <div className="p-4 bg-gray-50 border-t border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <Layers size={16} className="text-gray-600" />
            <h4 className="text-xs font-medium text-gray-700">Additional Information</h4>
          </div>
          <div className="ml-6 space-y-1">
            {Object.entries(executionDetails)
              .filter(([key]) => key !== 'steps' && key !== 'technique')
              .map(([key, value]) => (
                <div key={key} className="text-xs">
                  <span className="text-gray-500">{key.replace(/_/g, ' ')}:</span>{' '}
                  <span className="text-gray-700 font-mono">
                    {Array.isArray(value)
                      ? `[${value.join(', ')}]`
                      : typeof value === 'object'
                        ? JSON.stringify(value)
                        : String(value)}
                  </span>
                </div>
              ))}
          </div>
        </div>
      )}
    </div>
  )
}
