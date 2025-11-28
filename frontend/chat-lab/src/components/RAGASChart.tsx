import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js'
import { RAGASScores } from '../types/rag.types'
import { BarChart3 } from 'lucide-react'
import { useComparison } from '../hooks/useComparison'

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend
)

interface RAGASChartProps {
  scores?: RAGASScores | null  // Now optional - will fall back to database averages
}

export default function RAGASChart({ scores }: RAGASChartProps) {
  // Fetch comparison data from database
  const { data: comparisonData, loading } = useComparison()

  // Calculate average RAGAS scores from all database entries
  const calculateAverageScores = (): RAGASScores | null => {
    if (!comparisonData || comparisonData.length === 0) return null

    let faithfulnessSum = 0
    let answerRelevancySum = 0
    let precisionSum = 0
    let recallSum = 0
    let count = 0

    // Sum all valid scores from database
    comparisonData.forEach(item => {
      if (item.faithfulness !== null && item.faithfulness !== undefined) {
        faithfulnessSum += item.faithfulness
        answerRelevancySum += item.answer_relevancy || 0
        precisionSum += item.precision || 0
        recallSum += item.recall || 0
        count++
      }
    })

    if (count === 0) return null

    // Return average scores
    return {
      faithfulness: faithfulnessSum / count,
      answer_relevancy: answerRelevancySum / count,
      context_precision: precisionSum / count,
      context_recall: recallSum / count,
    }
  }

  // Priority: scores from props (individual query) > database averages
  const displayScores = scores || calculateAverageScores()

  // Show empty state if no data available
  if (!displayScores) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
        <div className="flex items-center gap-2 mb-3">
          <BarChart3 className="text-gray-600" size={20} />
          <h3 className="text-sm font-medium text-gray-900">RAGAS Quality Scores</h3>
        </div>
        {loading ? (
          <p className="text-gray-500 text-center py-8">Loading RAGAS data...</p>
        ) : (
          <p className="text-gray-500 text-center py-8">
            No RAGAS data available. Run queries to see quality scores.
          </p>
        )}
      </div>
    )
  }

  const data = {
    labels: ['Faithfulness', 'Answer Relevancy', 'Context Precision', 'Context Recall'],
    datasets: [
      {
        label: 'RAGAS Scores',
        data: [
          displayScores.faithfulness,
          displayScores.answer_relevancy,
          displayScores.context_precision,
          displayScores.context_recall
        ],
        backgroundColor: [
          'rgba(59, 130, 246, 0.8)',  // blue
          'rgba(16, 185, 129, 0.8)',  // green
          'rgba(245, 158, 11, 0.8)',  // orange
          'rgba(139, 92, 246, 0.8)'   // purple
        ],
        borderColor: [
          'rgb(59, 130, 246)',
          'rgb(16, 185, 129)',
          'rgb(245, 158, 11)',
          'rgb(139, 92, 246)'
        ],
        borderWidth: 2
      }
    ]
  }

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        display: false
      },
      title: {
        display: false
      },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return `Score: ${(context.parsed.y * 100).toFixed(1)}%`
          }
        }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        max: 1,
        ticks: {
          callback: function(value: any) {
            return (value * 100) + '%'
          }
        }
      }
    }
  }

  const avgScore = (
    displayScores.faithfulness +
    displayScores.answer_relevancy +
    displayScores.context_precision +
    displayScores.context_recall
  ) / 4

  // Determine if showing database averages or individual query scores
  const isShowingAverages = !scores && comparisonData.length > 0

  return (
    <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="text-gray-600" size={20} />
          <h3 className="text-sm font-medium text-gray-900">RAGAS Quality Scores</h3>
          {isShowingAverages && (
            <span className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded">
              Avg of {comparisonData.length} queries
            </span>
          )}
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500">Average Score</p>
          <p className="text-lg font-bold text-primary-600">{(avgScore * 100).toFixed(1)}%</p>
        </div>
      </div>

      <div style={{ height: '250px' }}>
        <Bar data={data} options={options} />
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3 text-xs">
        <div>
          <p className="text-gray-600">Faithfulness</p>
          <p className="font-medium text-blue-600">{(displayScores.faithfulness * 100).toFixed(1)}%</p>
        </div>
        <div>
          <p className="text-gray-600">Answer Relevancy</p>
          <p className="font-medium text-green-600">{(displayScores.answer_relevancy * 100).toFixed(1)}%</p>
        </div>
        <div>
          <p className="text-gray-600">Context Precision</p>
          <p className="font-medium text-orange-600">{(displayScores.context_precision * 100).toFixed(1)}%</p>
        </div>
        <div>
          <p className="text-gray-600">Context Recall</p>
          <p className="font-medium text-purple-600">{(displayScores.context_recall * 100).toFixed(1)}%</p>
        </div>
      </div>
    </div>
  )
}
