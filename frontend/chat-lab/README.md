# RAG Lab - Frontend

Interactive chat interface for comparing 9 RAG (Retrieval-Augmented Generation) techniques.

## Features

- Real-time RAG query interface
- 9 different RAG techniques comparison
- Visual metrics dashboard (latency, cost, tokens, chunks)
- RAGAS quality scores visualization (Chart.js)
- Source documents display with relevance scores
- Responsive design with TailwindCSS
- TypeScript for type safety

## Tech Stack

- **React 18** - UI framework
- **TypeScript** - Type safety
- **Vite 5** - Build tool
- **TailwindCSS 3** - Styling
- **Axios** - HTTP client
- **Chart.js 4** - Data visualization
- **Lucide React** - Icons

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- Backend server running on http://localhost:8000

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev
```

The application will be available at http://localhost:5173

### Build for Production

```bash
npm run build
npm run preview
```

## Project Structure

```
src/
├── api/
│   ├── client.ts           # Axios configuration
│   └── rag.service.ts      # API service methods
├── components/
│   ├── TechniqueSelector.tsx   # RAG technique dropdown
│   ├── QueryInput.tsx          # Chat input with send button
│   ├── ResponseDisplay.tsx     # Answer display
│   ├── MetricsCard.tsx         # Performance metrics cards
│   ├── SourcesList.tsx         # Retrieved sources list
│   └── RAGASChart.tsx          # RAGAS quality chart
├── types/
│   └── rag.types.ts        # TypeScript interfaces
├── App.tsx                 # Main application
├── main.tsx                # Application entry point
└── index.css               # Global styles with Tailwind
```

## Environment Variables

Create a `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Available RAG Techniques

1. Baseline RAG - Traditional pipeline
2. HyDE - Hypothetical Document Embeddings
3. Reranking - Two-stage retrieval with reranking
4. Query Expansion - Multiple query variations
5. Fusion RAG - Ensemble retrieval
6. Agentic RAG - Multi-step reasoning
7. Corrective RAG - Self-correcting retrieval
8. Self-RAG - Self-reflection mechanism
9. Adaptive RAG - Dynamic strategy selection

## API Integration

The frontend connects to the backend API:

- `GET /api/techniques` - List available techniques
- `POST /api/query` - Execute RAG query
- `POST /api/compare` - Compare multiple techniques
- `GET /api/health` - Check backend status

## Components Usage

### TechniqueSelector
Displays RAG techniques with implementation status, complexity, and average metrics.

### QueryInput
Chat-style input with Enter to send, Shift+Enter for new line.

### ResponseDisplay
Shows the query, answer, and execution steps.

### MetricsCard
Displays 4 key metrics: Latency, Cost, Tokens, Chunks.

### RAGASChart
Bar chart showing 4 RAGAS quality scores with average.

### SourcesList
Lists retrieved document chunks with relevance scores.

## Development

```bash
# Run dev server with hot reload
npm run dev

# Type checking
npm run build

# Lint code
npm run lint
```

## License

MIT
