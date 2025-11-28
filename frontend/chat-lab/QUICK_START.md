# RAG Lab Frontend - Quick Start Guide

## Prerequisites

- Node.js 18+ installed
- Backend server running on http://localhost:8000

## Installation

```bash
cd /root/Filipe/Teste-Claude/rag-lab/frontend/chat-lab
npm install
```

## Running the Application

### Option 1: Using the start script
```bash
./start.sh
```

### Option 2: Using npm directly
```bash
npm run dev
```

The application will be available at: **http://localhost:5173**

## First Time Setup

1. Make sure the backend is running:
   ```bash
   # In another terminal
   cd /root/Filipe/Teste-Claude/rag-lab/backend
   # Follow backend startup instructions
   ```

2. Start the frontend:
   ```bash
   cd /root/Filipe/Teste-Claude/rag-lab/frontend/chat-lab
   npm run dev
   ```

3. Open your browser to http://localhost:5173

4. You should see:
   - "Backend Online" indicator (green) in the header
   - 9 RAG techniques loaded in the dropdown
   - A chat input ready for your questions

## Usage

1. **Select a RAG Technique**
   - Use the dropdown to choose from 9 techniques
   - View technique description, complexity, and average metrics

2. **Ask a Question**
   - Type your question in the text area
   - Press Enter or click the Send button
   - Wait for the response

3. **View Results**
   - See the AI-generated answer
   - Review performance metrics (latency, cost, tokens, chunks)
   - Analyze RAGAS quality scores in the chart
   - Examine source documents with relevance scores

## Troubleshooting

### "Backend Offline" Error
- Make sure the backend server is running on port 8000
- Check that `.env` has the correct API URL: `VITE_API_URL=http://localhost:8000`

### "Technique Not Implemented" Error
- Some techniques may not be implemented yet in the backend
- Try selecting a different technique (e.g., "baseline")

### Build Errors
```bash
# Clean and rebuild
rm -rf node_modules dist
npm install
npm run build
```

## Environment Variables

Create or edit `.env` file:

```env
VITE_API_URL=http://localhost:8000
```

## Development Commands

```bash
# Start development server with hot reload
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Type checking
npm run build

# Lint code
npm run lint
```

## Project Structure

```
src/
├── api/              # API client and services
├── components/       # React components
├── types/           # TypeScript interfaces
├── App.tsx          # Main application
├── main.tsx         # Entry point
└── index.css        # Global styles
```

## Features

- **9 RAG Techniques**: Baseline, HyDE, Reranking, Query Expansion, Fusion, Agentic, Corrective, Self-RAG, Adaptive
- **Real-time Metrics**: Latency, cost, token usage, chunks retrieved
- **Quality Scores**: RAGAS evaluation (Faithfulness, Relevancy, Precision, Recall)
- **Source Display**: View retrieved document chunks with relevance scores
- **Responsive Design**: Works on desktop, tablet, and mobile

## Next Steps

1. Test with different RAG techniques
2. Compare results across techniques
3. Analyze RAGAS scores to understand quality
4. Review source documents to verify answers

## Support

For issues or questions, check:
- `README.md` - Full documentation
- `IMPLEMENTATION_SUMMARY.md` - Technical details
- Backend documentation for API contract

## Quick Tips

- Press **Enter** to send, **Shift+Enter** for new line
- Hover over source cards to see full content
- Check the execution steps to understand the technique's workflow
- Compare latency and cost metrics across different techniques

Enjoy exploring RAG techniques! 🚀
