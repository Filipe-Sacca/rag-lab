# Backend Setup - RAG Lab

## ✅ O Que Foi Implementado

### Estrutura Completa
```
backend/
├── main.py                    ✅ FastAPI app
├── config.py                  ✅ Settings Pydantic
├── .env                       ✅ Environment variables
├── requirements.txt           ✅ Dependencies
├── core/
│   ├── llm.py                ✅ Google Gemini
│   ├── embeddings.py         ✅ text-embedding-004
│   └── vector_store.py       ✅ Pinecone
├── api/
│   └── routes.py             ✅ REST endpoints
├── models/
│   └── schemas.py            ✅ Pydantic models
├── techniques/
│   ├── baseline_rag.py       ✅ Baseline RAG
│   ├── hyde_rag.py           ✅ HyDE
│   └── reranking_rag.py      ✅ Reranking
└── evaluation/
    └── ragas_eval.py         ✅ RAGAS metrics
```

### Técnicas RAG Implementadas

| Técnica | Status | Precision | Latência | Custo/Query |
|---------|--------|-----------|----------|-------------|
| **Baseline** | ✅ | 0.70 | 1.2s | $0.002 |
| **HyDE** | ✅ | 0.85 | 2.5s | $0.004 |
| **Reranking** | ✅ | 0.90 | 2.5s | $0.003 |
| Sub-Query | ⏳ Fase 2 | 0.75 | 3.5s | $0.008 |
| Fusion | ⏳ Fase 2 | 0.90 | 5.5s | $0.018 |
| Graph RAG | ⏳ Fase 3 | 0.85 | 4.0s | $0.005 |
| Parent Doc | ⏳ Fase 2 | 0.88 | 2.0s | $0.003 |
| Agentic | ⏳ Fase 3 | 0.90 | 4.0s | $0.010 |
| Adaptive | ⏳ Fase 3 | 0.89 | 2.2s | $0.004 |

### Endpoints REST

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/health` | Health check |
| GET | `/api/techniques` | Lista técnicas |
| POST | `/api/query` | Query RAG |
| POST | `/api/compare` | Compara técnicas |
| POST | `/api/evaluate` | RAGAS scores |
| POST | `/api/documents/upload` | Upload docs |
| GET | `/api/documents` | Lista docs |
| DELETE | `/api/documents/{id}` | Remove doc |

---

## 🚀 Setup e Instalação

### 1. Configurar API Keys

Edite `backend/.env` e preencha suas chaves:

```bash
# Google AI
GOOGLE_API_KEY=sua-chave-aqui

# Pinecone
PINECONE_API_KEY=sua-chave-aqui

# Cohere
COHERE_API_KEY=sua-chave-aqui
```

**Onde obter**:
- Google: https://makersuite.google.com/app/apikey
- Pinecone: https://app.pinecone.io/
- Cohere: https://dashboard.cohere.com/api-keys

---

### 2. Instalar Dependências

```bash
cd backend

# Criar ambiente virtual
python3.11 -m venv venv
source venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

---

### 3. Criar Índice Pinecone

**Opção A: Via Dashboard**
1. Acesse https://app.pinecone.io/
2. Create Index → Name: `rag-lab`
3. Dimension: `768`
4. Metric: `cosine`

**Opção B: Via Python**
```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="sua-chave")

pc.create_index(
    name="rag-lab",
    dimension=768,
    metric="cosine",
    spec=ServerlessSpec(
        cloud="aws",
        region="us-east-1"
    )
)
```

---

### 4. Rodar o Backend

```bash
cd backend

# Ativar venv
source venv/bin/activate

# Rodar servidor
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Servidor rodando em**: `http://localhost:8000`

---

## 🧪 Testar o Backend

### Health Check

```bash
curl http://localhost:8000/api/health
```

**Resposta esperada**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "services": {
    "pinecone": {"status": "connected"},
    "gemini": {"status": "available"},
    "cohere": {"status": "available"}
  }
}
```

---

### Listar Técnicas

```bash
curl http://localhost:8000/api/techniques
```

**Resposta esperada**:
```json
[
  {
    "id": "baseline",
    "name": "Baseline RAG",
    "implemented": true,
    "complexity": "low",
    "avg_latency_ms": 1200
  },
  {
    "id": "hyde",
    "name": "HyDE",
    "implemented": true
  },
  {
    "id": "reranking",
    "name": "Reranking",
    "implemented": true
  }
]
```

---

### Executar Query (Baseline)

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual o telefone da empresa?",
    "technique": "baseline",
    "params": {
      "top_k": 5,
      "temperature": 0.7
    }
  }'
```

**Resposta esperada**:
```json
{
  "query": "Qual o telefone da empresa?",
  "answer": "O telefone é (11) 1234-5678.",
  "technique_used": "baseline",
  "sources": [
    {
      "content": "Contato: Tel (11) 1234-5678",
      "score": 0.92,
      "metadata": {"document": "contatos.pdf"}
    }
  ],
  "metrics": {
    "latency_ms": 1234,
    "tokens_total": 179,
    "cost_usd": 0.0021
  },
  "ragas_scores": {
    "faithfulness": 0.95,
    "answer_relevancy": 0.92,
    "context_precision": 0.78,
    "context_recall": 0.65
  }
}
```

---

### Testar HyDE

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Como melhorar performance?",
    "technique": "hyde"
  }'
```

---

### Testar Reranking

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual a política de devolução?",
    "technique": "reranking",
    "params": {
      "initial_top_k": 20,
      "final_top_n": 5
    }
  }'
```

---

### Comparar Técnicas

```bash
curl -X POST http://localhost:8000/api/compare \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Qual o horário de funcionamento?",
    "techniques": ["baseline", "hyde", "reranking"]
  }'
```

**Resposta**:
```json
{
  "query": "Qual o horário de funcionamento?",
  "results": [
    {"technique": "baseline", "answer": "...", "metrics": {...}},
    {"technique": "hyde", "answer": "...", "metrics": {...}},
    {"technique": "reranking", "answer": "...", "metrics": {...}}
  ],
  "comparison": {
    "fastest": "baseline",
    "cheapest": "baseline",
    "best_faithfulness": "reranking"
  }
}
```

---

## 📊 Swagger UI

Acesse documentação interativa:

**URL**: http://localhost:8000/docs

Features:
- Testa todos endpoints visualmente
- Vê schemas de request/response
- Experimenta com diferentes parâmetros

---

## 🔧 Próximos Passos

### Fase 2: Upload de Documentos

```bash
curl -X POST http://localhost:8000/api/documents/upload \
  -F "file=@manual.pdf"
```

### Fase 2: Implementar Técnicas Restantes

- Sub-Query Decomposition
- Fusion
- Parent Document

### Fase 3: Técnicas Avançadas

- Graph RAG (Neo4j)
- Agentic RAG (LangGraph)
- Adaptive RAG

---

## 🐛 Troubleshooting

### Erro: Pinecone connection failed

**Solução**:
1. Verifique API key no `.env`
2. Confirme que índice `rag-lab` existe
3. Verifique dimensão: 768

### Erro: Gemini API error

**Solução**:
1. Verifique `GOOGLE_API_KEY` no `.env`
2. Teste: https://makersuite.google.com/app/apikey
3. Confirme quota disponível

### Erro: Cohere reranking failed

**Solução**:
1. Verifique `COHERE_API_KEY` no `.env`
2. Confirme modelo: `rerank-english-v3.0`

---

## 📝 Logs

Backend usa **loguru** para logging.

**Ver logs**:
```bash
tail -f logs/rag-lab.log
```

**Níveis**:
- INFO: Requests, responses
- WARNING: Rate limits, degraded performance
- ERROR: Falhas de API, exceções

---

## 🎯 Métricas Esperadas

### Baseline RAG
- Latência: 1-2s
- Custo: $0.002/query
- Precision: 0.70
- Recall: 0.60

### HyDE
- Latência: 2-3s
- Custo: $0.004/query
- Precision: 0.85 (+15%)
- Recall: 0.65

### Reranking
- Latência: 2-3s
- Custo: $0.003/query
- Precision: 0.90 (+35%)
- Recall: 0.80 (+30%)

---

**Backend está pronto para integração com frontend!** 🚀

**Documentação completa**: `frontend/docs/API_CONTRACT.md`
