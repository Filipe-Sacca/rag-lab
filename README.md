# 🧪 RAG Lab - Laboratório de Técnicas RAG

Plataforma interativa para **experimentação e comparação** de técnicas avançadas de Retrieval-Augmented Generation (RAG).

---

## 🎯 Propósito

O **RAG Lab** é um ambiente de aprendizado prático que permite:

✅ **Experimentar** 9 técnicas RAG diferentes em um único projeto
✅ **Comparar** métricas de desempenho (precision, recall, latência, custo)
✅ **Entender** quando usar cada técnica através de exemplos práticos
✅ **Avaliar** qualidade com métricas RAGAS automatizadas
✅ **Aprender** conceitos RAG de forma incremental e prática

**Público-Alvo**:
- Desenvolvedores estudando RAG
- Engenheiros de ML avaliando técnicas
- Equipes técnicas decidindo arquitetura RAG
- Pesquisadores comparando abordagens

---

## 🏗️ Stack Tecnológica

### Backend

| Componente | Tecnologia | Versão | Justificativa |
|------------|------------|--------|---------------|
| **Linguagem** | Python | 3.11+ | Ecossistema RAG mais maduro |
| **API Framework** | FastAPI | 0.109+ | Alta performance, async nativo |
| **LLM** | Google Gemini | 2.5 Flash | Custo-benefício ideal ($0.075/1M tokens) |
| **Embeddings** | Google | text-embedding-004 | Gratuito, alta qualidade |
| **Vector DB** | Pinecone | Latest | Serverless, fácil setup |
| **Graph DB** | Neo4j | 5.x | Para Graph RAG (opcional) |
| **Reranking** | Cohere | rerank-english-v3.0 | Melhor precisão do mercado |
| **Orchestration** | LangChain | 0.1.x | Chains e integrações |
| **Agent Framework** | LangGraph | 0.0.26+ | Para Agentic RAG |
| **Evaluation** | RAGAS | 0.1.x | Métricas automáticas |

### Frontend

| Componente | Tecnologia | Versão | Justificativa |
|------------|------------|--------|---------------|
| **Framework** | React | 18.x | Ecosistema maduro |
| **Build Tool** | Vite | 5.x | Velocidade de desenvolvimento |
| **Styling** | TailwindCSS | 3.x | Prototipagem rápida |
| **Charts** | Chart.js | 4.x | Visualização de métricas |
| **HTTP Client** | Axios | 1.x | Simplicidade |

### Infraestrutura

| Componente | Tecnologia |
|------------|------------|
| **Package Manager** | uv (Python) |
| **Environment** | python-dotenv |
| **Code Quality** | Ruff, Black |

---

## 📊 Técnicas RAG Implementadas

### 🎯 Core Techniques (6)

1. **Baseline RAG** - Pipeline tradicional (fundação)
2. **HyDE** - Hypothetical Document Embeddings (queries ambíguas)
3. **Reranking** - Cross-encoder precision (filtro de ruído)
4. **Sub-Query** - Decomposição multi-hop (recall máximo)
5. **Fusion** - Multi-strategy combination (qualidade máxima)
6. **Graph RAG** - Knowledge graphs (queries relacionais)

### 🚀 Advanced Techniques (3)

7. **Parent Document** - Chunk size optimization (precisão + contexto)
8. **Agentic RAG** - RAG como ferramenta (multi-fonte)
9. **Adaptive RAG** - Seleção inteligente (produção)

### 📚 Documentação Completa

Cada técnica possui documentação detalhada em `docs/`:
- Como funciona (pipeline completo)
- Vantagens e desvantagens
- Métricas esperadas (RAGAS scores)
- Quando usar vs quando NÃO usar
- Código de exemplo
- Variações avançadas

**Comparação completa**: `docs/COMPARISON.md`

---

## 🚀 Quick Start

### Pré-requisitos

```bash
# Python 3.11+
python --version

# uv (package manager)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Node.js 18+ (para frontend)
node --version
```

### Configuração (.env)

```bash
# Backend/.env
GOOGLE_API_KEY=your-gemini-api-key
PINECONE_API_KEY=your-pinecone-api-key
PINECONE_ENVIRONMENT=gcp-starter
PINECONE_INDEX_NAME=rag-lab
COHERE_API_KEY=your-cohere-api-key  # Opcional (para Reranking)
```

---

## 💰 Estimativa de Custos

### Por Query (Média)

| Técnica | LLM Calls | Vector Search | Total |
|---------|-----------|---------------|-------|
| Baseline | 1 | 1 | $0.002 |
| HyDE | 2 | 1 | $0.004 |
| Reranking | 1 | 1 + Rerank | $0.003 |
| Sub-Query | 1 + decomp | 3 | $0.008 |
| Fusion | 5 | 8 | $0.018 |
| Agentic | 3-10 | 1-5 | $0.005-0.015 |

### Uso Típico Laboratório

```
100 queries/dia × 30 dias = 3000 queries/mês

Se usar sempre Baseline:
3000 × $0.002 = $6/mês ✅

Se testar todas técnicas igualmente:
3000 / 9 técnicas ≈ 333 queries/técnica
Custo médio: ~$0.006/query
Total: 3000 × $0.006 = $18/mês ✅

Budget recomendado: $20-30/mês
```

---

## 📚 Recursos de Aprendizado

### Documentação Interna
- `docs/COMPARISON.md` - Começar aqui!
- `docs/BASELINE_RAG.md` - Fundação
- `docs/FUTURE_TECHNIQUES.md` - Próximas técnicas

### Papers Fundamentais
- Lewis et al. (2020) - RAG original
- Gao et al. (2022) - HyDE
- Yao et al. (2023) - ReAct
- Jeong et al. (2024) - Adaptive RAG

### Recursos Externos
- [LangChain Docs](https://python.langchain.com/docs)
- [RAGAS Framework](https://docs.ragas.io/)
- [Pinecone Learning Center](https://www.pinecone.io/learn/)

---

**Status**: 🔄 Em desenvolvimento ativo
**Última atualização**: 2024-11-19
**Versão**: 0.1.0-alpha
