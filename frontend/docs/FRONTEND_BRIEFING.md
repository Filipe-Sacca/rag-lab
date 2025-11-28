# Frontend Briefing - RAG Lab

**Bem-vindo!** Você é responsável pelo **frontend** do RAG Lab.

Outro Claude está cuidando do **backend** (FastAPI + Gemini + Pinecone).

---

## 🎯 Seu Objetivo

Criar uma aplicação React para **testar e comparar 9 técnicas RAG** através de uma interface chat intuitiva.

---

## 📚 Contexto do Projeto

### O Que é RAG Lab?

Laboratório interativo para **experimentação** de técnicas RAG (Retrieval-Augmented Generation):

**9 Técnicas Implementadas**:
1. **Baseline RAG** - Pipeline tradicional
2. **HyDE** - Hypothetical Document Embeddings
3. **Reranking** - Cross-encoder precision
4. **Sub-Query** - Query decomposition
5. **Fusion** - Multi-strategy combination
6. **Graph RAG** - Knowledge graphs (Neo4j)
7. **Parent Document** - Chunk size optimization
8. **Agentic RAG** - RAG como ferramenta
9. **Adaptive RAG** - Seleção automática

### Objetivo Educacional

Permitir que o usuário:
- ✅ Teste cada técnica individualmente
- ✅ Compare múltiplas técnicas lado-a-lado
- ✅ Veja métricas RAGAS em tempo real
- ✅ Entenda quando usar cada técnica

---

## 🏗️ Stack Frontend

```yaml
Framework: React 18.x
Build Tool: Vite 5.x
Linguagem: TypeScript
Styling: TailwindCSS 3.x
HTTP Client: Axios 1.x
Charts: Chart.js 4.x
Ícones: Lucide React ou Heroicons
Formulários: React Hook Form (opcional)
```

---

## 🎨 Interface Proposta

### Modo 1: Single Query (Principal)

```
┌─────────────────────────────────────────────┐
│  RAG Lab - Teste de Técnicas                │
├─────────────────────────────────────────────┤
│                                             │
│  [Dropdown: Selecione a técnica ▼]          │
│  ○ Baseline RAG                             │
│  ○ HyDE                                     │
│  ○ Reranking                                │
│  ○ Sub-Query                                │
│  ...                                        │
│                                             │
│  ┌────────────────────────────────────┐    │
│  │ Digite sua pergunta aqui...        │    │
│  └────────────────────────────────────┘    │
│                           [Enviar →]        │
│                                             │
├─────────────────────────────────────────────┤
│  💬 Resposta:                               │
│  O telefone da empresa é (11) 1234-5678.    │
│                                             │
│  📊 Métricas:                               │
│  ⏱️ Latência: 1.2s                          │
│  💰 Custo: $0.002                           │
│  🎯 Faithfulness: 0.95                      │
│  🎯 Relevancy: 0.92                         │
│  🎯 Precision: 0.78                         │
│  🎯 Recall: 0.65                            │
│                                             │
│  📄 Fontes (2):                             │
│  [1] "Contato: Tel (11) 1234..." (score: 0.92)│
│  [2] "Para mais informações..." (score: 0.88) │
└─────────────────────────────────────────────┘
```

### Modo 2: Compare Mode (Secundário)

```
┌─────────────────────────────────────────────┐
│  Modo Comparação                            │
├─────────────────────────────────────────────┤
│  Selecione técnicas:                        │
│  ☑ Baseline  ☑ HyDE  ☑ Reranking           │
│                                             │
│  Pergunta: Qual o telefone?                 │
│                           [Comparar →]      │
├─────────────────────────────────────────────┤
│  ┌───────────┬───────────┬───────────┐     │
│  │ Baseline  │   HyDE    │ Reranking │     │
│  ├───────────┼───────────┼───────────┤     │
│  │ Resposta A│ Resposta B│ Resposta C│     │
│  │ 1.2s      │ 2.5s      │ 2.5s      │     │
│  │ $0.002    │ $0.004    │ $0.003    │     │
│  │ F: 0.85   │ F: 0.92   │ F: 0.95   │     │
│  └───────────┴───────────┴───────────┘     │
│                                             │
│  🏆 Melhor Faithfulness: Reranking          │
│  ⚡ Mais Rápido: Baseline                   │
│  💰 Mais Barato: Baseline                   │
└─────────────────────────────────────────────┘
```

### Modo 3: Batch Mode (Opcional)

Upload de CSV com múltiplas perguntas para teste em lote.

---

## 📋 Componentes a Criar

### 1. Layout Principal
```typescript
// src/App.tsx
- Header com logo e modo (Single/Compare)
- Sidebar com informações das técnicas (opcional)
- Main content area
- Footer com créditos
```

### 2. Technique Selector
```typescript
// src/components/TechniqueSelector.tsx
interface TechniqueSelectorProps {
  onSelect: (techniqueId: string) => void
  mode: 'single' | 'multiple'
}

// Lista técnicas do backend (/api/techniques)
// Mostra status: implementado, não implementado
// Exibe complexidade e métricas médias
```

### 3. Query Input
```typescript
// src/components/QueryInput.tsx
interface QueryInputProps {
  onSubmit: (query: string) => void
  loading: boolean
}

// Textarea para pergunta
// Botão de envio
// Loading state
// Validação (query não vazia)
```

### 4. Response Display
```typescript
// src/components/ResponseDisplay.tsx
interface ResponseDisplayProps {
  response: QueryResponse | null
  loading: boolean
}

// Mostra resposta formatada
// Exibe métricas em cards
// Lista fontes expandíveis
// Gráfico RAGAS scores
```

### 5. Metrics Card
```typescript
// src/components/MetricsCard.tsx
interface MetricsCardProps {
  metrics: Metrics
  ragas: RAGASScores
}

// Cards visuais para latência, custo, tokens
// Gráfico de barras para RAGAS scores
// Comparação com médias da técnica
```

### 6. Sources List
```typescript
// src/components/SourcesList.tsx
interface SourcesListProps {
  sources: Source[]
}

// Lista de chunks recuperados
// Score de cada chunk
// Metadata expandível
// Highlight de trechos relevantes
```

### 7. Compare View
```typescript
// src/components/CompareView.tsx
interface CompareViewProps {
  results: ComparisonResult
}

// Layout de colunas para múltiplas técnicas
// Tabela comparativa
// Gráficos comparativos
// Winner badges (fastest, cheapest, best quality)
```

---

## 🔌 Integração com Backend

### Setup do Axios

```typescript
// src/api/client.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json'
  }
})

export default api
```

### API Service

```typescript
// src/api/rag.service.ts
import api from './client'

export const ragService = {
  // Listar técnicas
  async getTechniques(): Promise<RAGTechnique[]> {
    const { data } = await api.get('/api/techniques')
    return data
  },

  // Executar query
  async query(request: QueryRequest): Promise<QueryResponse> {
    const { data } = await api.post('/api/query', request)
    return data
  },

  // Comparar técnicas
  async compare(request: CompareRequest): Promise<ComparisonResult> {
    const { data } = await api.post('/api/compare', request)
    return data
  },

  // Health check
  async health(): Promise<HealthStatus> {
    const { data } = await api.get('/api/health')
    return data
  }
}
```

### Tipos TypeScript

```typescript
// src/types/rag.types.ts

export interface RAGTechnique {
  id: string
  name: string
  description: string
  implemented: boolean
  complexity: 'low' | 'medium' | 'high' | 'very_high'
  avg_latency_ms: number
  avg_cost_usd: number
}

export interface QueryRequest {
  query: string
  technique: string
  params?: {
    top_k?: number
    temperature?: number
    max_tokens?: number
  }
}

export interface QueryResponse {
  query: string
  answer: string
  technique_used: string
  sources: Source[]
  metrics: Metrics
  ragas_scores: RAGASScores
  execution_details: ExecutionDetails
}

export interface Source {
  content: string
  score: number
  metadata: {
    document: string
    page: number
    chunk_id: string
  }
}

export interface Metrics {
  latency_ms: number
  tokens_input: number
  tokens_output: number
  tokens_total: number
  cost_usd: number
  chunks_retrieved: number
  chunks_used: number
}

export interface RAGASScores {
  faithfulness: number
  answer_relevancy: number
  context_precision: number
  context_recall: number
}

export interface ExecutionDetails {
  technique_steps: string[]
  timestamp: string
}

export interface CompareRequest {
  query: string
  techniques: string[]
  params?: {
    top_k?: number
    temperature?: number
  }
}

export interface ComparisonResult {
  query: string
  results: QueryResponse[]
  comparison: {
    fastest: string
    cheapest: string
    best_faithfulness: string
    best_relevancy: string
    best_precision: string
    best_recall: string
  }
  total_time_ms: number
  total_cost_usd: number
}
```

---

## 🎨 Design System (Sugestão)

### Cores
```css
/* TailwindCSS config */
colors: {
  primary: '#3b82f6',    /* Blue */
  success: '#10b981',    /* Green */
  warning: '#f59e0b',    /* Orange */
  danger: '#ef4444',     /* Red */
  neutral: '#6b7280',    /* Gray */
}
```

### Componentes Base
- Buttons: Primary, Secondary, Outline
- Cards: Com shadow e border radius
- Inputs: Com focus states
- Badges: Para status (implementado/não implementado)
- Tooltips: Para explicar métricas

---

## 📊 Visualizações de Dados

### Chart.js - RAGAS Scores

```typescript
// src/components/RAGASChart.tsx
import { Bar } from 'react-chartjs-2'

const data = {
  labels: ['Faithfulness', 'Relevancy', 'Precision', 'Recall'],
  datasets: [{
    label: 'RAGAS Scores',
    data: [0.95, 0.92, 0.78, 0.65],
    backgroundColor: ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']
  }]
}

<Bar data={data} options={{ ... }} />
```

### Comparação Visual

Gráfico de barras agrupadas para comparar métricas entre técnicas.

---

## 🚀 Estrutura de Pastas

```
frontend/chat-lab/
├── src/
│   ├── api/
│   │   ├── client.ts              # Axios instance
│   │   └── rag.service.ts         # API calls
│   ├── components/
│   │   ├── TechniqueSelector.tsx
│   │   ├── QueryInput.tsx
│   │   ├── ResponseDisplay.tsx
│   │   ├── MetricsCard.tsx
│   │   ├── SourcesList.tsx
│   │   ├── RAGASChart.tsx
│   │   └── CompareView.tsx
│   ├── types/
│   │   └── rag.types.ts           # TypeScript interfaces
│   ├── hooks/
│   │   └── useRAG.ts              # Custom hook
│   ├── utils/
│   │   └── formatters.ts          # Helper functions
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
├── docs/
│   ├── API_CONTRACT.md            # ← LEIA ESTE ARQUIVO!
│   └── FRONTEND_BRIEFING.md       # ← VOCÊ ESTÁ AQUI
├── package.json
├── tsconfig.json
├── vite.config.ts
└── tailwind.config.js
```

---

## 📦 Dependências

```json
{
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "axios": "^1.6.0",
    "chart.js": "^4.4.0",
    "react-chartjs-2": "^5.2.0",
    "lucide-react": "^0.300.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "@vitejs/plugin-react": "^4.2.0",
    "typescript": "^5.3.0",
    "vite": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "autoprefixer": "^10.4.0",
    "postcss": "^8.4.0"
  }
}
```

---

## 🔧 Variáveis de Ambiente

```bash
# frontend/chat-lab/.env

VITE_API_URL=http://localhost:8000
```

---

## ✅ Checklist de Implementação

### Fase 1: Setup Básico
- [ ] Criar projeto Vite + React + TypeScript
- [ ] Instalar dependências (axios, chart.js, tailwindcss)
- [ ] Configurar TailwindCSS
- [ ] Criar estrutura de pastas
- [ ] Configurar API client (axios)
- [ ] Criar tipos TypeScript

### Fase 2: Componentes Core
- [ ] TechniqueSelector
- [ ] QueryInput
- [ ] ResponseDisplay
- [ ] MetricsCard
- [ ] SourcesList

### Fase 3: Single Query Mode
- [ ] Integrar componentes
- [ ] Conectar com backend (/api/query)
- [ ] Exibir respostas
- [ ] Mostrar métricas RAGAS
- [ ] Listar fontes

### Fase 4: Visualizações
- [ ] Gráfico RAGAS (Chart.js)
- [ ] Cards de métricas
- [ ] Loading states
- [ ] Error handling

### Fase 5: Compare Mode
- [ ] UI de seleção múltipla
- [ ] Integrar com /api/compare
- [ ] Layout comparativo
- [ ] Gráficos comparativos
- [ ] Winner badges

### Fase 6: Polimento
- [ ] Responsividade mobile
- [ ] Animações de transição
- [ ] Dark mode (opcional)
- [ ] Documentação de componentes

---

## 🧪 Como Testar Localmente

### 1. Backend rodando
```bash
# Outro Claude deve ter o backend rodando em:
http://localhost:8000
```

### 2. Frontend dev server
```bash
cd frontend/chat-lab
npm install
npm run dev

# Abre em: http://localhost:5173
```

### 3. Testar integração
```bash
# 1. Verificar se backend está online
curl http://localhost:8000/api/health

# 2. Listar técnicas
curl http://localhost:8000/api/techniques

# 3. Executar query de teste
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual o telefone?",
    "technique": "baseline"
  }'
```

---

## 🐛 Troubleshooting

### CORS Error
```
Backend deve configurar:
Access-Control-Allow-Origin: http://localhost:5173
```

### Conexão recusada
```
Verificar se backend está rodando:
ps aux | grep uvicorn
```

### Técnica não implementada
```
Backend retorna 501 - mostrar mensagem amigável:
"Esta técnica será implementada na Fase 3"
```

---

## 📚 Documentação Complementar

**IMPORTANTE**: Leia estes arquivos para contexto completo:

1. **`/root/Filipe/Teste-Claude/rag-lab/README.md`**
   - Visão geral do projeto
   - Stack completa (Gemini, Pinecone, Cohere)
   - Custo e objetivos

2. **`/root/Filipe/Teste-Claude/rag-lab/docs/COMPARISON.md`**
   - Comparação detalhada das 9 técnicas
   - Métricas esperadas
   - Quando usar cada técnica

3. **`frontend/docs/API_CONTRACT.md`** ← **CRUCIAL!**
   - Especificação completa da API
   - Schemas TypeScript
   - Exemplos de requests/responses

4. **`/root/Filipe/Teste-Claude/rag-lab/docs/BASELINE_RAG.md`** (e outros)
   - Detalhes de cada técnica
   - Como funcionam
   - Vantagens/desvantagens

---

## 🎯 Seu Objetivo Final

Entregar uma aplicação React que permita:

1. ✅ **Testar técnicas individualmente** com interface chat simples
2. ✅ **Ver métricas RAGAS** em tempo real com visualizações
3. ✅ **Comparar técnicas** lado-a-lado
4. ✅ **Entender diferenças** através de gráficos e tabelas

---

## 🤝 Comunicação com Outro Claude (Backend)

**Você não precisa se comunicar diretamente com o outro Claude.**

Apenas siga o **contrato da API** em `API_CONTRACT.md`.

Se houver mudanças na API:
1. Outro Claude atualizará `API_CONTRACT.md`
2. Você adapta o frontend conforme necessário

---

## 🚀 Comece Agora!

```bash
# 1. Criar projeto Vite
cd /root/Filipe/Teste-Claude/rag-lab/frontend
npm create vite@latest chat-lab -- --template react-ts
cd chat-lab
npm install

# 2. Instalar dependências
npm install axios chart.js react-chartjs-2 lucide-react
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p

# 3. Configurar TailwindCSS
# ... (editar tailwind.config.js)

# 4. Começar desenvolvimento
npm run dev
```

---

**Boa sorte! Você tem tudo que precisa para começar.** 🎉

**Dúvidas?** Consulte `API_CONTRACT.md` ou `README.md`.

---

**Última atualização**: 2024-11-19
