import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface MetricsBarChartProps {
  faithfulness: number | null
  answerRelevancy: number | null
  contextPrecision: number | null
  contextRecall: number | null
  latencyMs: number | null
  chunksRetrieved: number | null
}

/**
 * Horizontal bar chart component for displaying RAGAS metrics.
 * Compact visualization suitable for expanded table rows.
 */
export default function MetricsBarChart({
  faithfulness,
  answerRelevancy,
  contextPrecision,
  contextRecall,
  latencyMs,
  chunksRetrieved,
}: MetricsBarChartProps) {
  // Color coding based on score thresholds
  const getColor = (value: number | null): string => {
    if (value === null) return 'rgba(156, 163, 175, 0.8)' // gray
    if (value >= 0.8) return 'rgba(34, 197, 94, 0.8)'  // green
    if (value >= 0.6) return 'rgba(234, 179, 8, 0.8)'   // yellow
    if (value >= 0.4) return 'rgba(249, 115, 22, 0.8)' // orange
    return 'rgba(239, 68, 68, 0.8)' // red
  }

  const metrics = [
    { label: 'Faithfulness', value: faithfulness },
    { label: 'Relevancy', value: answerRelevancy },
    { label: 'Precision', value: contextPrecision },
    { label: 'Recall', value: contextRecall },
  ]

  const data = {
    labels: metrics.map(m => m.label),
    datasets: [
      {
        label: 'Score',
        data: metrics.map(m => m.value ?? 0),
        backgroundColor: metrics.map(m => getColor(m.value)),
        borderColor: metrics.map(m => getColor(m.value).replace('0.8', '1')),
        borderWidth: 1,
        borderRadius: 4,
      },
    ],
  }

  const options = {
    indexAxis: 'y' as const,
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      x: {
        beginAtZero: true,
        max: 1,
        ticks: {
          callback: function (value: number | string) {
            return `${Number(value) * 100}%`
          },
          font: {
            size: 10,
          },
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.2)',
        },
      },
      y: {
        ticks: {
          font: {
            size: 11,
            weight: 500,
          },
        },
        grid: {
          display: false,
        },
      },
    },
    plugins: {
      legend: {
        display: false,
      },
      tooltip: {
        callbacks: {
          label: function (context: any) {
            const value = context.raw as number
            return `${(value * 100).toFixed(1)}%`
          },
        },
      },
    },
  }

  return (
    <div className="space-y-4">
      {/* Bar Chart */}
      <div className="h-32">
        <Bar data={data} options={options} />
      </div>

      {/* Additional Stats */}
      <div className="flex gap-4 text-sm">
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
          <span className="text-gray-500">Latency:</span>
          <span className="font-medium text-gray-900">
            {latencyMs != null ? `${latencyMs.toFixed(0)}ms` : 'N/A'}
          </span>
        </div>
        <div className="flex items-center gap-2 px-3 py-1.5 bg-gray-100 rounded-lg">
          <span className="text-gray-500">Chunks:</span>
          <span className="font-medium text-gray-900">
            {chunksRetrieved ?? 'N/A'}
          </span>
        </div>
      </div>
    </div>
  )
}
