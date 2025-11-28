import { Clock, DollarSign, FileText, Database } from 'lucide-react'

interface MetricsCardProps {
  metrics: {
    latency_ms?: number
    tokens?: {
      input?: number
      output?: number
      total?: number
    }
    cost?: {
      total_usd?: number
    }
    chunks_retrieved?: number
  } | null
}

export default function MetricsCard({ metrics }: MetricsCardProps) {
  if (!metrics) return null

  const metricItems = [
    {
      icon: Clock,
      label: 'Latency',
      value: `${(metrics.latency_ms || 0).toFixed(0)}ms`,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50'
    },
    {
      icon: DollarSign,
      label: 'Cost',
      value: `$${(metrics.cost?.total_usd || 0).toFixed(6)}`,
      color: 'text-green-600',
      bgColor: 'bg-green-50'
    },
    {
      icon: FileText,
      label: 'Total Tokens',
      value: (metrics.tokens?.total || 0).toLocaleString(),
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      subtitle: `${metrics.tokens?.input || 0} in / ${metrics.tokens?.output || 0} out`
    },
    {
      icon: Database,
      label: 'Chunks',
      value: `${metrics.chunks_retrieved || 0}`,
      color: 'text-orange-600',
      bgColor: 'bg-orange-50',
      subtitle: 'retrieved'
    }
  ]

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {metricItems.map((item, index) => {
        const Icon = item.icon
        return (
          <div key={index} className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
            <div className="flex items-center justify-between mb-2">
              <div className={`p-2 rounded-lg ${item.bgColor}`}>
                <Icon className={item.color} size={20} />
              </div>
            </div>
            <p className="text-2xl font-bold text-gray-900">{item.value}</p>
            <p className="text-sm text-gray-600">{item.label}</p>
            {item.subtitle && (
              <p className="text-xs text-gray-500 mt-1">{item.subtitle}</p>
            )}
          </div>
        )
      })}
    </div>
  )
}
