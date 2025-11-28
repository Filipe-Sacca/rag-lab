# Como Construir um Backend Python Profissional: Guia Completo

## Analogia Central: Construindo uma Casa

Antes de começar, pense em construir um backend como construir uma casa:

```
❌ ERRADO: Começar pelas paredes e depois pensar onde colocar a fundação
✅ CERTO: Fundação → Estrutura → Instalações → Acabamento

Backend é igual:
❌ ERRADO: Escrever rotas primeiro, depois "descobrir" o que precisa
✅ CERTO: Dados → Lógica → Rotas → Integração
```

---

## PARTE 1: Planejamento (ANTES de Escrever Código)

### 1.1 Perguntas Fundamentais

Antes de abrir o editor, responda:

**a) Qual problema estou resolvendo?**
```
Exemplo RAG Lab:
"Preciso comparar 9 técnicas diferentes de RAG (Retrieval-Augmented Generation)
com métricas de qualidade e performance"
```

**b) Quem vai usar?**
```
Exemplo RAG Lab:
- Pesquisadores testando técnicas de IA
- Desenvolvedores comparando abordagens
- Interface web (frontend separado)
```

**c) Que dados vou manipular?**
```
Exemplo RAG Lab:
✅ Documentos (texto para indexação)
✅ Embeddings (vetores)
✅ Queries (perguntas dos usuários)
✅ Resultados (respostas + métricas)
✅ Histórico de execuções
```

**d) Que operações são necessárias?**
```
Exemplo RAG Lab:
1. Upload de documentos → vetorizar → salvar em Pinecone
2. Query → recuperar contexto → gerar resposta
3. Avaliar qualidade (métricas RAGAS)
4. Comparar técnicas diferentes
5. Persistir resultados para análise
```

### 1.2 Escolhendo Tecnologias

**Framework Web: FastAPI vs Flask vs Django**

```python
# DECISÃO: Quando usar cada um?

FastAPI ✅
├─ API moderna com OpenAPI automático
├─ Type hints nativos (Pydantic)
├─ Async/await suporte
├─ Alta performance
└─ Melhor para: APIs REST, microserviços, ML/AI

Flask 🟡
├─ Simples e flexível
├─ Grande ecossistema
├─ Curva de aprendizado suave
└─ Melhor para: MVPs rápidos, projetos pequenos

Django 🟡
├─ "Batteries included" (admin, ORM, auth)
├─ Monolítico
├─ Mais opinativo
└─ Melhor para: CRUD completo, sites tradicionais
```

**Por que RAG Lab escolheu FastAPI?**
```python
✅ Integração com LLMs (async é crucial)
✅ Validação automática (Pydantic schemas)
✅ Documentação interativa (/docs)
✅ Performance para embeddings pesados
```

### 1.3 Desenhando Arquitetura de Dados

**Mental Model: Fluxo de Dados**

```
RAG Lab - Fluxo de Dados:

┌─────────────┐
│   Cliente   │
│  (Frontend) │
└──────┬──────┘
       │ HTTP Request
       ↓
┌─────────────────────────────────┐
│        FastAPI (API Layer)       │
│  ┌──────────────────────────┐  │
│  │   Routers (Endpoints)    │  │
│  │  /upload  /query  /health│  │
│  └──────────┬───────────────┘  │
└─────────────┼───────────────────┘
              │
    ┌─────────┼─────────┐
    │         │         │
    ↓         ↓         ↓
┌──────┐  ┌──────┐  ┌──────────┐
│Models│  │ Core │  │Techniques│
│(DTOs)│  │(LLM) │  │(RAG Impl)│
└──────┘  └──┬───┘  └─────┬────┘
             │            │
        ┌────┼────────────┼─────┐
        ↓    ↓            ↓     ↓
   ┌────────┐  ┌─────────────┐  │
   │SQLite  │  │  Pinecone   │  │
   │(Local) │  │(Vector DB)  │  │
   └────────┘  └─────────────┘  │
                                 ↓
                         ┌──────────────┐
                         │Google Gemini │
                         │    (LLM)     │
                         └──────────────┘
```

**Decisões de Arquitetura do RAG Lab:**
```python
# 1. SEPARAÇÃO DE CAMADAS
api/         # ← Endpoints HTTP (interface externa)
models/      # ← Schemas Pydantic (contratos de dados)
core/        # ← Lógica central (LLM, embeddings, vector store)
techniques/  # ← Implementações RAG (regras de negócio)
db/          # ← Persistência (SQLAlchemy + helpers)

# Por quê?
✅ Mudança independente (trocar Pinecone não afeta rotas)
✅ Testabilidade (testa lógica sem HTTP)
✅ Reusabilidade (core/ usado por múltiplas técnicas)
```

### 1.4 Definindo Endpoints da API

**Método: Design Contract-First**

```python
# ANTES de implementar, defina contratos:

# 1. Listar operações necessárias
Operations = [
    "Upload documento",
    "Fazer query",
    "Listar técnicas disponíveis",
    "Comparar técnicas",
    "Ver histórico",
    "Health check"
]

# 2. Mapear para endpoints REST
POST   /api/v1/upload          # Criar recurso (documento)
POST   /api/v1/query           # Ação (gerar resposta)
GET    /api/v1/techniques      # Listar recursos
GET    /api/v1/executions      # Listar histórico
POST   /api/v1/compare         # Ação (comparação)
GET    /health                 # Status do serviço

# 3. Definir schemas de entrada/saída
class QueryRequest(BaseModel):
    query: str               # O que enviar
    technique: str          # Qual técnica usar
    top_k: int = 5         # Quantos docs recuperar

class QueryResponse(BaseModel):
    answer: str            # Resposta gerada
    sources: list[str]     # Contexto usado
    metrics: RAGMetrics    # Avaliação RAGAS
```

---

## PARTE 2: Ordem de Desenvolvimento (Passo a Passo)

### Passo 1: Setup Inicial (Fundação da Casa)

**Por que primeiro?** Sem ambiente configurado, não roda nada.

```bash
# 1.1 Criar estrutura de projeto
mkdir backend
cd backend

# 1.2 Criar ambiente virtual (SEMPRE!)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

# 1.3 Criar .env (segredos NUNCA no código)
cat > .env << EOF
GOOGLE_API_KEY=your_key_here
PINECONE_API_KEY=your_key_here
ENVIRONMENT=development
DEBUG=True
EOF

# 1.4 Criar requirements.txt
cat > requirements.txt << EOF
fastapi==0.115.4
uvicorn[standard]==0.32.0
pydantic==2.9.2
pydantic-settings==2.6.1
sqlalchemy==2.0.36
pinecone-client==5.0.1
langchain==0.3.7
google-generativeai==0.8.3
EOF

# 1.5 Instalar dependências
pip install -r requirements.txt

# 1.6 Criar .gitignore
cat > .gitignore << EOF
venv/
.env
__pycache__/
*.pyc
*.db
EOF
```

**Checkpoint Visual:**
```
backend/
├── venv/           ✅ Ambiente isolado
├── .env            ✅ Segredos seguros
├── .gitignore      ✅ Git configurado
└── requirements.txt ✅ Dependências declaradas
```

---

### Passo 2: Estrutura de Pastas (Planta da Casa)

**Por que essa ordem?** Bottom-up: das fundações para o telhado.

```bash
# Criar estrutura completa
mkdir -p {api,models,core,techniques,db,utils,tests}
touch {api,models,core,techniques,db,utils}/__init__.py

# Resultado:
backend/
├── api/              # ← CAMADA 4: HTTP Endpoints (último)
│   └── __init__.py
├── models/           # ← CAMADA 1: Contratos de dados (primeiro)
│   └── __init__.py
├── core/             # ← CAMADA 2: Funcionalidades base
│   └── __init__.py
├── techniques/       # ← CAMADA 3: Lógica de negócio
│   └── __init__.py
├── db/               # ← CAMADA 2: Persistência
│   └── __init__.py
├── utils/            # ← Helpers gerais
│   └── __init__.py
├── tests/            # ← Testes (parallel ao desenvolvimento)
├── config.py         # ← PRÓXIMO: Configuração
├── main.py           # ← ÚLTIMO: Entry point
├── .env
└── requirements.txt
```

**Por que __init__.py?**
```python
# Torna pastas em "Python packages" (importáveis)

# SEM __init__.py ❌
from models.schemas import QueryRequest  # ModuleNotFoundError

# COM __init__.py ✅
from models.schemas import QueryRequest  # Funciona!

# BÔNUS: Pode controlar o que é exposto
# models/__init__.py
from .schemas import QueryRequest, QueryResponse

# Agora pode fazer:
from models import QueryRequest  # Mais limpo!
```

---

### Passo 3: Configuração (config.py)

**Por que agora?** Todos os outros arquivos vão precisar de settings.

```python
# config.py - OLHE O CÓDIGO REAL DO RAG LAB
from pydantic import Field
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """
    🎯 PATTERN: Centralize configuração em uma classe

    Benefícios:
    ✅ Type hints (IDE autocomplete)
    ✅ Validação automática (Pydantic)
    ✅ Carrega de .env automaticamente
    ✅ Valores default seguros
    """

    model_config = SettingsConfigDict(
        env_file=".env",           # Carrega automaticamente
        case_sensitive=False       # GOOGLE_API_KEY = google_api_key
    )

    # Application settings
    VERSION: str = "0.1.0"
    ENVIRONMENT: str = Field(default="development")
    DEBUG: bool = Field(default=True)
    HOST: str = Field(default="0.0.0.0")
    PORT: int = Field(default=8000)

    # External APIs
    GOOGLE_API_KEY: str = Field(..., description="Required!")
    GEMINI_MODEL: str = Field(default="gemini-2.0-flash-001")

    # Business logic defaults
    CHUNK_SIZE: int = Field(default=1000)
    TOP_K: int = Field(default=5)

# Global instance (singleton pattern)
settings = Settings()
```

**Como usar em outros arquivos:**
```python
# Em qualquer lugar do projeto:
from config import settings

# Acesso type-safe com autocomplete!
print(settings.GOOGLE_API_KEY)  # IDE sabe que é str
print(settings.PORT)             # IDE sabe que é int
```

**❌ ANTI-PATTERN (o que NÃO fazer):**
```python
# ❌ Hardcoded
API_KEY = "sk-12345..."  # NUNCA!

# ❌ os.getenv direto
import os
api_key = os.getenv("API_KEY")  # Sem validação, sem defaults

# ❌ Configuração espalhada
# file1.py
DEBUG = True
# file2.py
DEBUG = False  # Qual é o valor real? 🤔
```

---

### Passo 4: Modelos de Dados (models/schemas.py)

**Por que agora?** Define contratos entre camadas antes de implementar.

```python
# models/schemas.py - VEJA O PADRÃO DO RAG LAB

from pydantic import BaseModel, Field
from typing import Optional

# 🎯 PATTERN: Request/Response pairs

class QueryRequest(BaseModel):
    """
    DTO (Data Transfer Object) para ENTRADA

    Cliente envia:
    POST /query
    {
        "query": "What is RAG?",
        "technique": "hyde",
        "top_k": 5
    }
    """
    query: str = Field(..., description="User question")
    technique: str = Field(default="baseline")
    top_k: int = Field(default=5, ge=1, le=20)  # ge=greater/equal
    namespace: Optional[str] = None

    # Pydantic valida automaticamente!
    # top_k = -1  → ValidationError ❌
    # top_k = 10  → OK ✅


class QueryResponse(BaseModel):
    """
    DTO para SAÍDA

    Backend responde:
    {
        "query": "What is RAG?",
        "answer": "RAG stands for...",
        "retrieved_docs": [...],
        "metrics": {...}
    }
    """
    query: str
    answer: str
    technique: str
    retrieved_docs: list[str]
    metrics: Optional["RAGMetrics"] = None
    metadata: dict = Field(default_factory=dict)


class RAGMetrics(BaseModel):
    """Nested model para métricas de avaliação"""
    faithfulness: float = Field(ge=0.0, le=1.0)
    answer_relevancy: float = Field(ge=0.0, le=1.0)
    context_precision: float = Field(ge=0.0, le=1.0)
```

**Por que Pydantic é poderoso:**
```python
# Validação automática
request = QueryRequest(query="test", top_k=100)  # ❌ ValidationError: top_k > 20

# Serialização JSON automática
response = QueryResponse(query="test", answer="...")
print(response.model_dump_json())  # → JSON string

# Type hints funcionam
def process(req: QueryRequest):
    print(req.query)  # IDE sabe que é string!
```

**Mental Model: Schemas são Contratos**
```
Frontend    →  [QueryRequest]  →  Backend
Backend     →  [QueryResponse] →  Frontend

Qualquer mudança no contrato = quebra clientes
→ Versionamento de API (/api/v1, /api/v2)
```

---

### Passo 5: Banco de Dados (db/)

**Por que agora?** Antes de implementar lógica, precisamos de persistência.

**5.1 Definir Modelos ORM (db/models.py)**

```python
# db/models.py - ESTRUTURA DO RAG LAB

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class RAGExecution(Base):
    """
    🎯 PATTERN: ORM Model representa TABELA no banco

    SQLAlchemy mapeia Python Class ↔ SQL Table
    """
    __tablename__ = "rag_executions"

    # Primary key (auto-incrementa)
    id = Column(Integer, primary_key=True, index=True)

    # Dados da execução
    technique = Column(String, nullable=False, index=True)  # index para queries rápidas
    query = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)

    # Métricas (JSON para flexibilidade)
    metrics = Column(JSON, nullable=True)

    # Metadados
    namespace = Column(String, default="default", index=True)
    execution_time_ms = Column(Float, nullable=True)

    # Timestamps (sempre útil!)
    created_at = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<RAGExecution(id={self.id}, technique={self.technique})>"
```

**5.2 Configurar Conexão (db/database.py)**

```python
# db/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Base

# SQLite para desenvolvimento (zero setup!)
# PostgreSQL para produção
DATABASE_URL = "sqlite:///./rag_lab.db"

# Engine: gerencia conexões com o banco
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Necessário para SQLite
)

# SessionLocal: factory para criar sessões (transações)
SessionLocal = sessionmaker(
    autocommit=False,  # Manual commit (controle de transação)
    autoflush=False,
    bind=engine
)

def init_db():
    """Cria todas as tabelas (roda no startup)"""
    Base.metadata.create_all(bind=engine)

def get_db():
    """
    🎯 PATTERN: Dependency Injection para FastAPI

    Usage:
    @app.get("/data")
    def get_data(db: Session = Depends(get_db)):
        # db é injetado automaticamente
        # e fechado após a request
    """
    db = SessionLocal()
    try:
        yield db  # Fornece a sessão
    finally:
        db.close()  # Garante fechamento
```

**5.3 CRUD Operations (db/crud.py)**

```python
# db/crud.py - PADRÃO REPOSITORY

from sqlalchemy.orm import Session
from .models import RAGExecution
from typing import List, Optional

def create_execution(db: Session, data: dict) -> RAGExecution:
    """
    🎯 PATTERN: Repository abstrai SQL

    Benefício: Trocar banco não afeta código chamador
    """
    execution = RAGExecution(**data)
    db.add(execution)
    db.commit()
    db.refresh(execution)  # Atualiza com ID gerado
    return execution

def get_execution(db: Session, execution_id: int) -> Optional[RAGExecution]:
    """Busca por ID"""
    return db.query(RAGExecution).filter(
        RAGExecution.id == execution_id
    ).first()

def get_executions_by_technique(
    db: Session,
    technique: str,
    limit: int = 100
) -> List[RAGExecution]:
    """Busca por técnica com paginação"""
    return db.query(RAGExecution).filter(
        RAGExecution.technique == technique
    ).order_by(
        RAGExecution.created_at.desc()
    ).limit(limit).all()
```

**Por que separar em 3 arquivos?**
```
models.py    → Define ESTRUTURA (tabelas)
database.py  → Gerencia CONEXÕES
crud.py      → Implementa OPERAÇÕES

Analogia: Cozinha
models.py    = Utensílios (o que existe)
database.py  = Fogão (como funciona)
crud.py      = Receitas (o que fazer)
```

---

### Passo 6: Lógica de Negócio (core/ e techniques/)

**Por que agora?** Temos dados e persistência, hora da inteligência.

**6.1 Core: Funcionalidades Base (core/)**

```python
# core/llm.py - Abstração do LLM

from langchain_google_genai import ChatGoogleGenerativeAI
from config import settings

def get_llm(temperature: float = 0.7):
    """
    🎯 PATTERN: Factory function

    Benefícios:
    ✅ Configuração centralizada
    ✅ Fácil trocar provider (OpenAI → Gemini → Anthropic)
    ✅ Lazy loading (só cria quando usar)
    """
    return ChatGoogleGenerativeAI(
        model=settings.GEMINI_MODEL,
        google_api_key=settings.GOOGLE_API_KEY,
        temperature=temperature,
    )

# core/vector_store.py - Abstração do Pinecone

from langchain_pinecone import PineconeVectorStore
from .embeddings import get_embeddings
from config import settings

def get_vector_store(namespace: str = "default"):
    """Factory para vector store"""
    return PineconeVectorStore(
        index_name=settings.PINECONE_INDEX_NAME,
        embedding=get_embeddings(),
        namespace=namespace
    )
```

**6.2 Techniques: Implementações RAG (techniques/)**

```python
# techniques/baseline_rag.py - OLHE O PADRÃO

from core import get_llm, get_vector_store
from typing import Dict, Any

def baseline_rag(
    query: str,
    top_k: int = 5,
    namespace: str = "default"
) -> Dict[str, Any]:
    """
    🎯 PATTERN: Técnica como função pura

    Input: query + parâmetros
    Output: dict padronizado

    Benefício: Fácil adicionar novas técnicas
    """
    # 1. Retrieve
    vector_store = get_vector_store(namespace)
    docs = vector_store.similarity_search(query, k=top_k)

    # 2. Generate
    llm = get_llm()
    context = "\n".join([doc.page_content for doc in docs])

    prompt = f"""Context: {context}

    Question: {query}

    Answer based only on the context above:"""

    answer = llm.invoke(prompt).content

    # 3. Return padronizado
    return {
        "query": query,
        "answer": answer,
        "sources": [{"content": doc.page_content} for doc in docs],
        "execution_details": {
            "technique": "baseline",
            "num_docs_retrieved": len(docs)
        }
    }
```

**Por que separar core/ e techniques/?**
```
core/        → Reutilizável (LLM, embeddings, vector store)
techniques/  → Específico (cada RAG technique usa core/)

Analogia: Cozinha
core/       = Ingredientes básicos (ovo, farinha, leite)
techniques/ = Receitas diferentes (bolo, panqueca, omelete)
```

---

### Passo 7: Rotas/Endpoints (api/routes.py)

**Por que agora?** Temos toda a lógica, só falta expor via HTTP.

```python
# api/routes.py - VEJA O PADRÃO COMPLETO DO RAG LAB

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from models.schemas import QueryRequest, QueryResponse
from techniques.baseline_rag import baseline_rag
from techniques.hyde_rag import hyde_rag
from db import get_db
from db.helpers import save_rag_result

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,  # ✅ Validação automática
    db: Session = Depends(get_db)  # ✅ Injeção de dependência
) -> QueryResponse:
    """
    🎯 PATTERN: Controller/Handler

    Responsabilidades:
    1. Receber request (HTTP)
    2. Validar dados (Pydantic faz automaticamente)
    3. Chamar lógica de negócio (techniques/)
    4. Persistir resultado (db/)
    5. Retornar response (HTTP)

    NÃO deve ter lógica de negócio aqui!
    """
    try:
        # Map technique name to function
        technique_map = {
            "baseline": baseline_rag,
            "hyde": hyde_rag,
        }

        technique_func = technique_map.get(
            request.technique,
            baseline_rag  # default
        )

        # Execute técnica (lógica em techniques/)
        result = technique_func(
            query=request.query,
            top_k=request.top_k,
            namespace=request.namespace
        )

        # Persistir (não bloqueia response)
        try:
            execution_id = save_rag_result(db, result, request.technique)
        except Exception as db_error:
            print(f"DB save failed: {db_error}")  # Log, mas não falha
            execution_id = None

        # Return response
        return QueryResponse(
            query=result["query"],
            answer=result["answer"],
            technique=request.technique,
            retrieved_docs=[doc["content"] for doc in result["sources"]],
            metadata={"execution_id": execution_id}
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query failed: {str(e)}"
        ) from e
```

**Padrão de Erro Handling:**
```python
# ✅ CERTO: Específico e informativo
try:
    result = technique_func(...)
except ValueError as e:
    raise HTTPException(status_code=400, detail=str(e))
except KeyError as e:
    raise HTTPException(status_code=404, detail=f"Not found: {e}")
except Exception as e:
    # Log para debug, mensagem genérica para cliente
    logger.error(f"Unexpected error: {e}", exc_info=True)
    raise HTTPException(status_code=500, detail="Internal error")

# ❌ ERRADO: Vago
try:
    ...
except:  # Nunca use bare except!
    return {"error": "something went wrong"}  # O quê??
```

---

### Passo 8: Main.py (Entry Point - Juntar Tudo)

**Por que por último?** É a cola que junta todos os componentes.

```python
# main.py - VEJA A ESTRUTURA COMPLETA DO RAG LAB

from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routes import router
from config import settings
from db import init_db, check_database_health

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    🎯 PATTERN: Application Lifecycle

    Executa na inicialização e encerramento do servidor
    """
    # Startup
    print(f"Starting RAG Lab v{settings.VERSION}")
    init_db()  # Cria tabelas

    health = check_database_health()
    print(f"Database: {health}")

    yield  # Aplicação roda aqui

    # Shutdown
    print("Shutting down...")

# Criar aplicação FastAPI
app = FastAPI(
    title="RAG Lab API",
    description="Backend for testing RAG techniques",
    version=settings.VERSION,
    lifespan=lifespan,  # Lifecycle manager
)

# CORS (permite frontend acessar)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers (endpoints)
app.include_router(router, prefix="/api/v1", tags=["rag"])

# Health check (sempre útil!)
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION
    }

# Entry point (python main.py)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG  # Hot reload em dev
    )
```

**Ordem de Execução:**
```
1. Python lê main.py
2. Importa módulos (api, config, db, etc)
3. Cria app FastAPI
4. Adiciona middleware (CORS)
5. Registra routers
6. Executa lifespan.startup (init_db)
7. Uvicorn inicia servidor HTTP
8. Aguarda requests...
9. Ctrl+C → lifespan.shutdown
```

---

### Passo 9: Testes

**Por que não no início?** TDD é avançado. Para aprender, teste depois de entender.

```python
# tests/test_baseline_rag.py

import pytest
from techniques.baseline_rag import baseline_rag

def test_baseline_rag_returns_answer():
    """Teste simples: função retorna estrutura esperada"""
    result = baseline_rag(query="What is Python?", top_k=3)

    assert "query" in result
    assert "answer" in result
    assert "sources" in result
    assert len(result["sources"]) <= 3

# Rodar: pytest tests/
```

---

### Passo 10: Deploy (Produção)

```bash
# Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]

# Rodar: docker build -t rag-lab . && docker run -p 8000:8000 rag-lab
```

---

## PARTE 3: Decisões de Arquitetura

### 3.1 Monolito vs Microserviços

```
Monolito ✅ (como RAG Lab)
├─ Um único backend
├─ Deploy simples
├─ Baixa latência (sem rede entre serviços)
└─ Melhor para: MVPs, times pequenos, domínio coeso

Microserviços 🟡
├─ Múltiplos backends independentes
├─ Deploy complexo (orquestração)
├─ Alta latência (comunicação via rede)
└─ Melhor para: escala gigante, times grandes, domínios distintos

RAG Lab → Monolito porque:
✅ Um domínio (RAG experiments)
✅ Time pequeno
✅ Não precisa escalar partes independentemente
```

### 3.2 Estrutura de Pastas

**Comparação de padrões:**

```python
# FLAT (simples, projetos pequenos)
backend/
├── main.py
├── models.py
├── database.py
├── routes.py
└── config.py

# MODULAR (organizado, projetos médios) ← RAG LAB USA
backend/
├── api/
│   └── routes.py
├── models/
│   └── schemas.py
├── core/
│   ├── llm.py
│   └── vector_store.py
├── techniques/
│   ├── baseline_rag.py
│   └── hyde_rag.py
├── db/
│   ├── models.py
│   └── crud.py
├── config.py
└── main.py

# FEATURE-BASED (complexo, projetos grandes)
backend/
├── features/
│   ├── documents/
│   │   ├── routes.py
│   │   ├── models.py
│   │   └── service.py
│   └── queries/
│       ├── routes.py
│       ├── models.py
│       └── service.py
└── shared/
    ├── config.py
    └── database.py
```

### 3.3 Padrões de Design

**Repository Pattern (usado em db/crud.py):**
```python
# Benefício: Abstrai persistência

# SEM Repository ❌
@app.get("/data")
def get_data(db: Session):
    return db.query(RAGExecution).filter(...).all()  # SQL vazando na rota!

# COM Repository ✅
@app.get("/data")
def get_data(db: Session):
    return crud.get_executions_by_technique(db, "baseline")  # Abstrato!
```

**Service Layer Pattern:**
```python
# Quando usar: Lógica complexa com múltiplas operações

# services/rag_service.py
class RAGService:
    def __init__(self, db: Session):
        self.db = db

    def execute_and_save(self, request: QueryRequest):
        # 1. Execute técnica
        result = technique_func(request.query)
        # 2. Avaliar qualidade
        metrics = evaluate(result)
        # 3. Persistir
        crud.create_execution(self.db, result, metrics)
        # 4. Notificar (webhooks, etc)
        notify_completion(result)
        return result

# Rota fica simples:
@app.post("/query")
def query(request: QueryRequest, db: Session = Depends(get_db)):
    service = RAGService(db)
    return service.execute_and_save(request)
```

---

## PARTE 4: Análise do RAG Lab

### O que foi feito certo ✅

**1. Configuração centralizada (config.py)**
```python
✅ Pydantic Settings
✅ Validação automática
✅ Type hints
✅ Valores default seguros
```

**2. Separação de camadas**
```python
✅ api/ (HTTP)
✅ models/ (DTOs)
✅ core/ (infraestrutura)
✅ techniques/ (lógica de negócio)
✅ db/ (persistência)
```

**3. Dependency Injection**
```python
✅ get_db() em rotas
✅ Factories (get_llm, get_vector_store)
✅ Configuração injetada
```

**4. Documentação automática**
```python
✅ OpenAPI em /docs
✅ Schemas Pydantic → JSON Schema
✅ Docstrings em endpoints
```

### O que poderia melhorar 🟡

**1. Falta Service Layer**
```python
# Atual: Rota tem lógica demais
@app.post("/query")
async def query_rag(request, db):
    technique_func = technique_map.get(...)  # Decisão na rota
    result = technique_func(...)
    save_rag_result(db, result)
    return response

# Melhor: Extrair para service
class RAGService:
    def execute_query(self, request: QueryRequest):
        # Toda a lógica aqui
        pass

@app.post("/query")
async def query_rag(request, db):
    service = RAGService(db)
    return service.execute_query(request)
```

**2. Tratamento de erros poderia ser mais específico**
```python
# Atual: Catch genérico
except Exception as e:
    raise HTTPException(500, f"Query failed: {str(e)}")

# Melhor: Erros específicos
except PineconeError as e:
    raise HTTPException(503, "Vector store unavailable")
except LLMError as e:
    raise HTTPException(502, "LLM service error")
except ValueError as e:
    raise HTTPException(400, str(e))
```

**3. Faltam testes**
```python
# Adicionar:
tests/
├── test_api/
│   └── test_routes.py
├── test_techniques/
│   └── test_baseline.py
└── test_db/
    └── test_crud.py
```

---

## PARTE 5: Checklist de Desenvolvimento

**Use para TODOS os projetos futuros:**

```markdown
## Fase 1: Planejamento (antes de codificar)
- [ ] Definir problema e requisitos
- [ ] Desenhar fluxo de dados
- [ ] Escolher tecnologias (framework, banco, APIs)
- [ ] Listar endpoints necessários
- [ ] Definir schemas de entrada/saída

## Fase 2: Setup
- [ ] Criar venv
- [ ] Criar .env e .gitignore
- [ ] Criar requirements.txt
- [ ] Definir estrutura de pastas

## Fase 3: Configuração
- [ ] config.py com Pydantic Settings
- [ ] Testar carregamento de .env

## Fase 4: Modelos de Dados
- [ ] Definir schemas Pydantic (models/)
- [ ] Definir modelos ORM (db/models.py)
- [ ] Testar validação

## Fase 5: Banco de Dados
- [ ] database.py (engine, sessionmaker)
- [ ] init_db() para criar tabelas
- [ ] crud.py com operações básicas
- [ ] Testar CRUD

## Fase 6: Lógica de Negócio
- [ ] Implementar core/ (LLM, embeddings, etc)
- [ ] Implementar lógica específica (techniques/)
- [ ] Testar funções isoladamente

## Fase 7: API Endpoints
- [ ] Criar routers (api/)
- [ ] Implementar endpoints
- [ ] Adicionar validação e error handling
- [ ] Testar via /docs

## Fase 8: Integração
- [ ] main.py com lifespan
- [ ] Configurar CORS
- [ ] Adicionar middleware (logging, etc)
- [ ] Health check endpoint

## Fase 9: Qualidade
- [ ] Escrever testes
- [ ] Configurar linter (ruff, black)
- [ ] Revisar error handling
- [ ] Documentar código

## Fase 10: Deploy
- [ ] Criar Dockerfile
- [ ] Configurar CI/CD
- [ ] Deploy para produção
- [ ] Monitoramento
```

---

## PARTE 6: Exercícios Práticos

### Exercício 1: Mini API de Tarefas (Básico)

**Objetivo:** Aplicar a ordem de desenvolvimento em um projeto simples.

```python
# Requisitos:
# - Criar tarefas (título, descrição)
# - Listar tarefas
# - Marcar como concluída
# - Deletar tarefas

# Passos:
1. Setup: venv, requirements.txt (fastapi, sqlalchemy)
2. Estrutura: api/, models/, db/, config.py, main.py
3. Config: Definir settings
4. Models: Task schema (Pydantic)
5. DB: Task model (SQLAlchemy), CRUD
6. API: Endpoints (POST /tasks, GET /tasks, etc)
7. Main: Juntar tudo
8. Teste: Via /docs
```

### Exercício 2: API de Blog (Intermediário)

**Objetivo:** Adicionar relacionamentos e autenticação.

```python
# Requisitos:
# - Usuários (registro, login)
# - Posts (criar, listar, editar)
# - Comentários em posts
# - Apenas dono pode editar

# Novos conceitos:
# - Relacionamentos (User → Posts → Comments)
# - JWT Authentication
# - Autorização (ownership check)
# - Paginação
```

### Exercício 3: Clone Simplificado do RAG Lab (Avançado)

**Objetivo:** Construir do zero seguindo a mesma arquitetura.

```python
# Requisitos:
# - Upload de arquivos PDF
# - Indexação em vector store
# - Query com duas técnicas (baseline + reranking)
# - Persistir execuções
# - Comparar técnicas

# Aplicar TUDO que aprendeu:
# - Estrutura modular
# - Separation of concerns
# - Dependency injection
# - Error handling
# - Testes
```

---

## PARTE 7: Recursos e Ferramentas

### Ferramentas Essenciais

```bash
# Formatação de código
pip install black ruff

# black: formata automaticamente
black .

# ruff: linter ultra-rápido
ruff check .

# Type checking
pip install mypy
mypy backend/

# Testes
pip install pytest pytest-cov
pytest tests/ --cov=backend
```

### Comandos Úteis

```bash
# Rodar servidor em dev (hot reload)
uvicorn main:app --reload

# Rodar com log detalhado
uvicorn main:app --log-level debug

# Gerar requirements.txt automaticamente
pip freeze > requirements.txt

# Ver rotas disponíveis
python -c "from main import app; print(app.routes)"
```

### Debug no VS Code

```json
// .vscode/launch.json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "module": "uvicorn",
            "args": [
                "main:app",
                "--reload"
            ],
            "jinja": true
        }
    ]
}
```

---

## Conclusão: O Processo de Pensamento

**Princípio fundamental:**

```
NÃO pense: "Vou fazer um backend"
PENSE: "Vou resolver [problema X] para [usuário Y]"

↓

Então pergunte:
1. Que dados preciso? → models/, db/
2. Que transformações? → core/, techniques/
3. Como expor? → api/
4. Como integrar? → main.py
```

**Ordem sempre importa:**

```
Fundação → Paredes → Telhado
(não o contrário!)

No código:
Dados → Lógica → Interface → Integração
```

**Aprenda com o RAG Lab:**

O projeto já tem uma arquitetura sólida. Estude:
1. Como `config.py` centraliza tudo
2. Como `models/schemas.py` define contratos
3. Como `techniques/` separa lógica
4. Como `api/routes.py` apenas orquestra

**Próximos Passos para Você:**

1. Implemente os exercícios na ordem
2. Compare com o RAG Lab
3. Experimente adicionar uma nova técnica RAG
4. Adicione testes ao projeto
5. Crie seu próprio projeto do zero

---

**Lembre-se:** Backend não é sobre decorar sintaxe. É sobre estruturar pensamento em camadas, separar responsabilidades, e construir sistemas que evoluem sem quebrar.

Boa sorte na jornada! 🚀
