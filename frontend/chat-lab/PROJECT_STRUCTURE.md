# RAG Lab Frontend - Project Structure

```
chat-lab/
│
├── 📄 Configuration Files
│   ├── package.json              # Dependencies and scripts
│   ├── tsconfig.json             # TypeScript configuration
│   ├── tsconfig.node.json        # Node TypeScript config
│   ├── vite.config.ts            # Vite build configuration
│   ├── tailwind.config.js        # TailwindCSS configuration
│   ├── postcss.config.js         # PostCSS configuration
│   ├── .env                      # Environment variables
│   └── .gitignore                # Git ignore rules
│
├── 📚 Documentation
│   ├── README.md                 # Main documentation
│   ├── QUICK_START.md            # Quick start guide
│   ├── IMPLEMENTATION_SUMMARY.md # Technical implementation details
│   └── PROJECT_STRUCTURE.md      # This file
│
├── 🚀 Entry Points
│   ├── index.html                # HTML template
│   ├── src/main.tsx              # React entry point
│   └── start.sh                  # Startup script
│
└── 📁 src/                       # Source code
    │
    ├── 🌐 API Layer
    │   ├── api/
    │   │   ├── client.ts         # Axios HTTP client (30s timeout)
    │   │   └── rag.service.ts    # RAG API methods (4 endpoints)
    │   │
    │   └── types/
    │       └── rag.types.ts      # TypeScript interfaces (8 main types)
    │
    ├── 🎨 Components
    │   └── components/
    │       ├── TechniqueSelector.tsx  # RAG technique dropdown
    │       ├── QueryInput.tsx         # Chat input with send button
    │       ├── ResponseDisplay.tsx    # Answer display
    │       ├── MetricsCard.tsx        # 4 metric cards (latency, cost, tokens, chunks)
    │       ├── RAGASChart.tsx         # Chart.js bar chart (4 RAGAS scores)
    │       └── SourcesList.tsx        # Document sources with scores
    │
    ├── 📱 Application
    │   └── App.tsx               # Main application component
    │
    └── 🎨 Styling
        ├── index.css             # Global styles + TailwindCSS
        └── vite-env.d.ts         # Vite environment types
```

## Component Hierarchy

```
App.tsx
│
├── Header
│   ├── Logo + Title
│   └── Backend Status Indicator
│
├── Error Alert (conditional)
│
├── Input Section
│   ├── TechniqueSelector
│   │   ├── Dropdown (9 techniques)
│   │   └── Technique Details Card
│   │       ├── Name + Complexity Badge
│   │       ├── Implementation Status
│   │       ├── Description
│   │       └── Avg Metrics
│   │
│   └── QueryInput
│       ├── Textarea (Enter to send)
│       └── Send Button (with loading)
│
├── Results Section (conditional)
│   │
│   ├── MetricsCard (4 cards in grid)
│   │   ├── Latency Card (blue)
│   │   ├── Cost Card (green)
│   │   ├── Tokens Card (purple)
│   │   └── Chunks Card (orange)
│   │
│   ├── Grid Layout (2 columns)
│   │   ├── ResponseDisplay
│   │   │   ├── Query Box
│   │   │   ├── Answer Box
│   │   │   └── Execution Steps
│   │   │
│   │   └── RAGASChart
│   │       ├── Average Score
│   │       ├── Bar Chart (4 metrics)
│   │       └── Score Details Grid
│   │
│   └── SourcesList
│       └── Source Cards (N items)
│           ├── Document Metadata
│           ├── Relevance Score Badge
│           └── Chunk Content
│
└── Footer
```

## Data Flow

```
1. App Mount
   ↓
   checkBackendHealth() → GET /api/health
   ↓
   loadTechniques() → GET /api/techniques
   ↓
   setTechniques(data)
   setSelectedTechnique(first)

2. User Query
   ↓
   handleQuery(query) → POST /api/query
   ↓
   {
     query: string,
     technique: string,
     params: { top_k, temperature, max_tokens }
   }
   ↓
   Response: QueryResponse
   ↓
   setResponse(data)
   ↓
   Render:
   - MetricsCard (metrics)
   - ResponseDisplay (answer + steps)
   - RAGASChart (ragas_scores)
   - SourcesList (sources)
```

## State Management

```typescript
// App.tsx State
const [techniques, setTechniques] = useState<RAGTechnique[]>([])
const [selectedTechnique, setSelectedTechnique] = useState<string>('')
const [response, setResponse] = useState<QueryResponse | null>(null)
const [isLoading, setIsLoading] = useState(false)
const [error, setError] = useState<string | null>(null)
const [backendStatus, setBackendStatus] = useState<'checking' | 'online' | 'offline'>('checking')
```

## TypeScript Types

```typescript
// Core Types (8 main interfaces)
1. RAGTechnique          # Technique metadata
2. QueryRequest          # API request format
3. QueryResponse         # API response format
4. Source                # Document chunk with score
5. Metrics               # Performance metrics
6. RAGASScores          # Quality evaluation scores
7. ExecutionDetails     # Execution metadata
8. CompareRequest       # (Future) Comparison request

// Props Types (6 components)
- TechniqueSelectorProps
- QueryInputProps
- ResponseDisplayProps
- MetricsCardProps
- RAGASChartProps
- SourcesListProps
```

## Styling System

```css
/* TailwindCSS Utility Classes */
Primary Colors:
- primary-50 to primary-900  (Blue)
- green-50 to green-900      (Success)
- orange-50 to orange-900    (Warning)
- red-50 to red-900          (Danger)

/* Custom Components */
.btn-primary      # Primary button style
.btn-secondary    # Secondary button style
.card             # Card container style

/* Responsive Breakpoints */
sm:  640px
md:  768px
lg:  1024px
xl:  1280px
```

## API Endpoints

```
Backend: http://localhost:8000

GET  /api/health       # Health check
GET  /api/techniques   # List techniques
POST /api/query        # Execute query
POST /api/compare      # Compare techniques (future)
```

## Build Output

```
dist/
├── index.html                  # 0.49 kB
├── assets/
│   ├── index-[hash].css       # 14.60 kB (TailwindCSS)
│   └── index-[hash].js        # 353.12 kB (React + deps)
└── vite.svg
```

## Dependencies Tree

```
Production Dependencies (6)
├── react ^18.2.0
├── react-dom ^18.2.0
├── axios ^1.6.2
├── chart.js ^4.4.0
├── react-chartjs-2 ^5.2.0
└── lucide-react ^0.294.0

Development Dependencies (12)
├── @vitejs/plugin-react ^4.2.1
├── typescript ^5.2.2
├── vite ^5.0.8
├── tailwindcss ^3.3.6
├── autoprefixer ^10.4.16
├── postcss ^8.4.32
├── eslint ^8.55.0
├── eslint-plugin-react-hooks ^4.6.0
├── eslint-plugin-react-refresh ^0.4.5
├── @typescript-eslint/eslint-plugin ^6.14.0
├── @typescript-eslint/parser ^6.14.0
├── @types/react ^18.2.43
└── @types/react-dom ^18.2.17
```

## File Statistics

```
Total Files: 27
├── TypeScript/TSX: 13
├── JSON: 3
├── JavaScript: 3
├── CSS: 1
├── HTML: 1
├── Markdown: 4
├── Shell: 1
└── Config: 1

Lines of Code (approx):
├── Components: ~800 lines
├── API/Types: ~150 lines
├── App.tsx: ~200 lines
├── Styles: ~50 lines
└── Total: ~1,200 lines
```

## Commands Reference

```bash
# Development
npm run dev          # Start dev server (http://localhost:5173)
./start.sh           # Alternative start script

# Build
npm run build        # TypeScript compile + Vite build
npm run preview      # Preview production build

# Quality
npm run lint         # ESLint check
tsc --noEmit        # Type check only
```

## Browser Support

- Chrome/Edge: Latest 2 versions
- Firefox: Latest 2 versions
- Safari: Latest 2 versions
- Mobile: iOS Safari 14+, Chrome Android

## Performance Metrics

```
Build Time: ~3.6s
Bundle Size: 353 kB (119 kB gzipped)
Dependencies: 301 packages
TypeScript: 100% coverage
Lighthouse Score: Not yet measured
```

## Future Enhancements

```
Priority 1 (High):
- [ ] Compare Mode implementation
- [ ] Query history
- [ ] Error boundary component

Priority 2 (Medium):
- [ ] Dark mode toggle
- [ ] Advanced parameters UI
- [ ] Export results feature

Priority 3 (Low):
- [ ] Analytics integration
- [ ] WebSocket streaming
- [ ] Mobile app version
```
