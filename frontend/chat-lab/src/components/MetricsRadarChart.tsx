import {
  Chart as ChartJS,
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend,
} from 'chart.js'
import { Radar } from 'react-chartjs-2'

ChartJS.register(
  RadialLinearScale,
  PointElement,
  LineElement,
  Filler,
  Tooltip,
  Legend
)

interface MetricsRadarChartProps {
  faithfulness: number | null
  answerRelevancy: number | null
  contextPrecision: number | null
  contextRecall: number | null
  technique: string
}

/**
 * Radar chart component for displaying RAGAS metrics.
 * Shows 4 key metrics: Faithfulness, Answer Relevancy, Context Precision, Context Recall
 */
export default function MetricsRadarChart({
  faithfulness,
  answerRelevancy,
  contextPrecision,
  contextRecall,
  technique,
}: MetricsRadarChartProps) {
  const data = {
    labels: [
      'Faithfulness',
      'Answer Relevancy',
      'Context Precision',
      'Context Recall',
    ],
    datasets: [
      {
        label: technique,
        data: [
          faithfulness ?? 0,
          answerRelevancy ?? 0,
          contextPrecision ?? 0,
          contextRecall ?? 0,
        ],
        backgroundColor: 'rgba(59, 130, 246, 0.2)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(59, 130, 246, 1)',
        pointBorderColor: '#fff',
        pointHoverBackgroundColor: '#fff',
        pointHoverBorderColor: 'rgba(59, 130, 246, 1)',
      },
    ],
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        beginAtZero: true,
        max: 1,
        min: 0,
        ticks: {
          stepSize: 0.2,
          font: {
            size: 10,
          },
          backdropColor: 'transparent',
        },
        pointLabels: {
          font: {
            size: 11,
            weight: 500,
          },
          color: '#374151',
        },
        grid: {
          color: 'rgba(156, 163, 175, 0.3)',
        },
        angleLines: {
          color: 'rgba(156, 163, 175, 0.3)',
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
            return `${context.label}: ${(value * 100).toFixed(1)}%`
          },
        },
      },
    },
  }

  return (
    <div className="h-48 w-full">
      <Radar data={data} options={options} />
    </div>
  )
}
