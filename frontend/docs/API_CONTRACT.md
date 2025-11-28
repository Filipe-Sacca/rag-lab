# API Contract - RAG Lab Backend

**Versão**: 1.0
**Backend**: FastAPI
**Base URL**: `http://localhost:8000`
**LLM**: Google Gemini 2.5 Flash
**Vector DB**: Pinecone
**Reranking**: Cohere

---

## 📋 Endpoints Disponíveis

### 1. Listar Técnicas RAG

**GET** `/api/techniques`

Retorna todas as técnicas RAG disponíveis com status de implementação.

**Response 200**:
```json
[
  {
    "id": "baseline",
    "name": "Baseline RAG",
    "description": "Pipeline tradicional: embed → search → generate",
    "implemented": true,
    "complexity": "low",
    "avg_latency_ms": 1200,
    "avg_cost_usd": 0.002
  },
  {
    "id": "hyde",
    "name": "HyDE (Hypothetical Document Embeddings)",
    "description": "Gera resposta hipotética antes da busca",
    "implemented": true,
    "complexity": "medium",
    "avg_latency_ms": 2500,
    "avg_cost_usd": 0.004
  },
  {
    "id": "reranking",
    "name": "Reranking",
    "description": "Two-stage retrieval com cross-encoder",
    "implemented": true,
    "complexity": "medium",
    "avg_latency_ms": 2500,
    "avg_cost_usd": 0.003
  },
  {
    "id": "subquery",
    "name": "Sub-Query Decomposition",
    "description": "Decompõe query complexa em sub-queries",
    "implemented": false,
    "complexity": "high",
    "avg_latency_ms": 3500,
    "avg_cost_usd": 0.008
  },
  {
    "id": "fusion",
    "name": "Fusion",
    "description": "Combina múltiplas estratégias de retrieval",
    "implemented": false,
    "complexity": "high",
    "avg_latency_ms": 5500,
    "avg_cost_usd": 0.018
  },
  {
    "id": "graph",
    "name": "Graph RAG",
    "description": "Usa knowledge graph (Neo4j)",
    "implemented": false,
    "complexity": "very_high",
    "avg_latency_ms": 4000,
    "avg_cost_usd": 0.005
  },
  {
    "id": "parent",
    "name": "Parent Document",
    "description": "Busca chunks pequenos, retorna documento pai",
    "implemented": false,
    "complexity": "medium",
    "avg_latency_ms": 2000,
    "avg_cost_usd": 0.003
  },
  {
    "id": "agentic",
    "name": "Agentic RAG",
    "description": "RAG como ferramenta opcional de agente",
    "implemented": false,
    "complexity": "high",
    "avg_latency_ms": 4000,
    "avg_cost_usd": 0.010
  },
  {
    "id": "adaptive",
    "name": "Adaptive RAG",
    "description": "Seleciona técnica automaticamente",
    "implemented": false,
    "complexity": "high",
    "avg_latency_ms": 2200,
    "avg_cost_usd": 0.004
  }
]
```

---

### 2. Executar Query RAG

**POST** `/api/query`

Executa uma query usando técnica RAG específica.

**Request Body**:
```json
{
  "query": "Qual o telefone da empresa?",
  "technique": "baseline",
  "params": {
    "top_k": 5,
    "temperature": 0.7,
    "max_tokens": 500
  }
}
```

**Campos**:
- `query` (string, obrigatório): Pergunta do usuário
- `technique` (string, obrigatório): ID da técnica (`baseline`, `hyde`, etc)
- `params` (object, opcional): Parâmetros da técnica
  - `top_k` (int, default: 5): Número de chunks a recuperar
  - `temperature` (float, default: 0.7): Temperatura do LLM
  - `max_tokens` (int, default: 500): Máximo de tokens na resposta

**Response 200**:
```json
{
  "query": "Qual o telefone da empresa?",
  "answer": "O telefone da empresa é (11) 1234-5678.",
  "technique_used": "baseline",
  "sources": [
    {
      "content": "Contato: Telefone (11) 1234-5678, Email contato@empresa.com",
      "score": 0.92,
      "metadata": {
        "document": "contatos.pdf",
        "page": 1,
        "chunk_id": "chunk_42"
      }
    },
    {
      "content": "Para mais informações, ligue (11) 1234-5678.",
      "score": 0.88,
      "metadata": {
        "document": "faq.pdf",
        "page": 3,
        "chunk_id": "chunk_127"
      }
    }
  ],
  "metrics": {
    "latency_ms": 1234,
    "tokens_input": 156,
    "tokens_output": 23,
    "tokens_total": 179,
    "cost_usd": 0.0021,
    "chunks_retrieved": 5,
    "chunks_used": 2
  },
  "ragas_scores": {
    "faithfulness": 0.95,
    "answer_relevancy": 0.92,
    "context_precision": 0.78,
    "context_recall": 0.65
  },
  "execution_details": {
    "technique_steps": [
      "Embedding da query com text-embedding-004",
      "Busca vetorial no Pinecone (top_k=5)",
      "Geração de resposta com Gemini 2.5 Flash"
    ],
    "timestamp": "2024-11-19T15:30:45.123Z"
  }
}
```

**Response 400** (Query inválida):
```json
{
  "error": "invalid_query",
  "message": "Query não pode ser vazia",
  "details": {}
}
```

**Response 404** (Técnica não encontrada):
```json
{
  "error": "technique_not_found",
  "message": "Técnica 'invalid_technique' não existe",
  "available_techniques": ["baseline", "hyde", "reranking", ...]
}
```

**Response 501** (Técnica não implementada):
```json
{
  "error": "not_implemented",
  "message": "Técnica 'fusion' ainda não foi implementada",
  "status": "planned",
  "eta": "Fase 3"
}
```

---

### 3. Comparar Técnicas

**POST** `/api/compare`

Executa a mesma query em múltiplas técnicas para comparação.

**Request Body**:
```json
{
  "query": "Qual o telefone da empresa?",
  "techniques": ["baseline", "hyde", "reranking"],
  "params": {
    "top_k": 5,
    "temperature": 0.7
  }
}
```

**Response 200**:
```json
{
  "query": "Qual o telefone da empresa?",
  "results": [
    {
      "technique": "baseline",
      "answer": "O telefone é (11) 1234-5678.",
      "metrics": { ... },
      "ragas_scores": { ... }
    },
    {
      "technique": "hyde",
      "answer": "O telefone da empresa é (11) 1234-5678.",
      "metrics": { ... },
      "ragas_scores": { ... }
    },
    {
      "technique": "reranking",
      "answer": "Telefone: (11) 1234-5678.",
      "metrics": { ... },
      "ragas_scores": { ... }
    }
  ],
  "comparison": {
    "fastest": "baseline",
    "cheapest": "baseline",
    "best_faithfulness": "reranking",
    "best_relevancy": "hyde",
    "best_precision": "reranking",
    "best_recall": "baseline"
  },
  "total_time_ms": 6200,
  "total_cost_usd": 0.009
}
```

---

### 4. Avaliar Resposta (RAGAS)

**POST** `/api/evaluate`

Avalia uma resposta RAG usando métricas RAGAS.

**Request Body**:
```json
{
  "query": "Qual o telefone?",
  "answer": "O telefone é (11) 1234-5678.",
  "contexts": [
    "Contato: Telefone (11) 1234-5678",
    "Email: contato@empresa.com"
  ],
  "ground_truth": "O telefone da empresa é (11) 1234-5678." // opcional
}
```

**Response 200**:
```json
{
  "scores": {
    "faithfulness": 0.95,
    "answer_relevancy": 0.92,
    "context_precision": 0.78,
    "context_recall": 0.65,
    "answer_similarity": 0.98
  },
  "evaluation_details": {
    "llm_used": "gemini-2.5-flash",
    "evaluation_time_ms": 450,
    "evaluation_cost_usd": 0.0005
  }
}
```

---

### 5. Upload de Documentos

**POST** `/api/documents/upload`

Faz upload de documentos para indexação no Pinecone.

**Request**: `multipart/form-data`
- `file`: PDF, TXT, DOCX, MD

**Response 200**:
```json
{
  "document_id": "doc_abc123",
  "filename": "manual.pdf",
  "pages": 15,
  "chunks_created": 47,
  "indexed": true,
  "processing_time_ms": 3400
}
```

---

### 6. Listar Documentos

**GET** `/api/documents`

Lista todos os documentos indexados.

**Response 200**:
```json
[
  {
    "id": "doc_abc123",
    "filename": "manual.pdf",
    "upload_date": "2024-11-19T15:30:45Z",
    "pages": 15,
    "chunks": 47,
    "size_bytes": 524288
  },
  {
    "id": "doc_def456",
    "filename": "faq.md",
    "upload_date": "2024-11-19T16:00:12Z",
    "pages": 1,
    "chunks": 12,
    "size_bytes": 8192
  }
]
```

---

### 7. Deletar Documento

**DELETE** `/api/documents/{document_id}`

Remove documento e seus chunks do Pinecone.

**Response 200**:
```json
{
  "deleted": true,
  "document_id": "doc_abc123",
  "chunks_removed": 47
}
```

---

### 8. Health Check

**GET** `/api/health`

Verifica status do backend e dependências.

**Response 200**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "pinecone": {
      "status": "connected",
      "index": "rag-lab",
      "dimension": 768,
      "total_vectors": 1247
    },
    "gemini": {
      "status": "available",
      "model": "gemini-2.5-flash"
    },
    "cohere": {
      "status": "available",
      "model": "rerank-english-v3.0"
    }
  },
  "uptime_seconds": 3600
}
```

**Response 503** (Serviço indisponível):
```json
{
  "status": "unhealthy",
  "services": {
    "pinecone": {
      "status": "error",
      "error": "Connection timeout"
    },
    "gemini": {
      "status": "available"
    },
    "cohere": {
      "status": "available"
    }
  }
}
```

---

### 9. WebSocket - Streaming (Opcional)

**WS** `/ws/stream`

Streaming de respostas em tempo real.

**Conexão**:
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/stream')
```

**Enviar query**:
```json
{
  "type": "query",
  "query": "Qual o telefone?",
  "technique": "baseline",
  "params": { "top_k": 5 }
}
```

**Receber chunks**:
```json
{ "type": "chunk", "content": "O telefone" }
{ "type": "chunk", "content": " é (11)" }
{ "type": "chunk", "content": " 1234-5678." }
{ "type": "complete", "metrics": { ... } }
```

---

## 🔐 Autenticação

**Fase 1**: Sem autenticação (desenvolvimento local)
**Fase 2**: API Key via header `X-API-Key`
**Fase 3**: JWT tokens

---

## 🌐 CORS

Backend configurado para aceitar:
```
Access-Control-Allow-Origin: http://localhost:5173
Access-Control-Allow-Methods: GET, POST, DELETE, OPTIONS
Access-Control-Allow-Headers: Content-Type
```

---

## 📊 Rate Limits

**Desenvolvimento**: Sem limites
**Produção**: 100 requests/minuto por IP

---

## 🐛 Códigos de Erro

| Código | Erro | Descrição |
|--------|------|-----------|
| 400 | `invalid_query` | Query vazia ou inválida |
| 400 | `invalid_params` | Parâmetros inválidos |
| 404 | `technique_not_found` | Técnica não existe |
| 404 | `document_not_found` | Documento não existe |
| 501 | `not_implemented` | Técnica não implementada |
| 503 | `service_unavailable` | Pinecone/Gemini/Cohere offline |
| 429 | `rate_limit_exceeded` | Muitas requisições |

---

## 📝 Schemas TypeScript

```typescript
// Técnica RAG
interface RAGTechnique {
  id: string
  name: string
  description: string
  implemented: boolean
  complexity: 'low' | 'medium' | 'high' | 'very_high'
  avg_latency_ms: number
  avg_cost_usd: number
}

// Request de query
interface QueryRequest {
  query: string
  technique: string
  params?: {
    top_k?: number
    temperature?: number
    max_tokens?: number
  }
}

// Response de query
interface QueryResponse {
  query: string
  answer: string
  technique_used: string
  sources: Source[]
  metrics: Metrics
  ragas_scores: RAGASScores
  execution_details: ExecutionDetails
}

interface Source {
  content: string
  score: number
  metadata: {
    document: string
    page: number
    chunk_id: string
  }
}

interface Metrics {
  latency_ms: number
  tokens_input: number
  tokens_output: number
  tokens_total: number
  cost_usd: number
  chunks_retrieved: number
  chunks_used: number
}

interface RAGASScores {
  faithfulness: number
  answer_relevancy: number
  context_precision: number
  context_recall: number
}

interface ExecutionDetails {
  technique_steps: string[]
  timestamp: string
}
```

---

## 🚀 Exemplo de Uso (Axios)

```typescript
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: { 'Content-Type': 'application/json' }
})

// Listar técnicas
const techniques = await api.get('/api/techniques')

// Executar query
const result = await api.post('/api/query', {
  query: 'Qual o telefone?',
  technique: 'baseline',
  params: { top_k: 5, temperature: 0.7 }
})

console.log(result.data.answer) // "O telefone é (11) 1234-5678."
console.log(result.data.metrics) // { latency_ms: 1234, cost_usd: 0.002, ... }
```

---

**Última atualização**: 2024-11-19
**Versão do contrato**: 1.0
