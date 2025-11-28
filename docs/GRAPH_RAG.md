# Graph RAG - Retrieval Aumentado com Grafos de Conhecimento

## 📋 Definição

**Graph RAG** combina **RAG tradicional com Grafos de Conhecimento** (Knowledge Graphs) para capturar e explorar **relações estruturadas entre entidades**.

Ao invés de apenas buscar chunks de texto similares, Graph RAG navega por **conexões semânticas** entre entidades (pessoas, lugares, conceitos, eventos).

**Insight**: Conhecimento não é só texto isolado. É uma rede de entidades e relações. Graph RAG explora essa estrutura.

---

## 🔄 Como Funciona

### Pipeline Completo

```
1. INDEXAÇÃO (Setup - Mais Complexo)
   ├─ Carregar documentos
   ├─ Extrair entidades (NER - Named Entity Recognition)
   │  └─ Pessoas, Organizações, Locais, Datas, Conceitos
   ├─ Extrair relações entre entidades
   │  └─ "João Silva [TRABALHA_EM] XYZ Corp"
   │  └─ "XYZ Corp [LOCALIZADA_EM] São Paulo"
   ├─ Construir Grafo de Conhecimento (Neo4j)
   │  └─ Nós = Entidades
   │  └─ Arestas = Relações
   └─ Armazenar chunks originais no Vector DB

2. HYBRID RETRIEVAL (Runtime)
   ├─ Query: "Experiência do CFO da XYZ Corp"
   ├─ (A) Vector Search: Busca chunks similares
   │  └─ "CFO XYZ Corp: João Silva..."
   ├─ (B) Graph Traversal: Navega relações
   │  └─ Encontra "João Silva" no grafo
   │  └─ Segue arestas [TRABALHOU_EM], [FORMADO_EM]
   │  └─ "João Silva → Goldman Sachs (10 anos)"
   │  └─ "João Silva → Harvard MBA"
   └─ Combinar chunks (Vector + Graph)

3. GERAÇÃO
   ├─ Prompt com contexto híbrido
   ├─ LLM sintetiza resposta
   └─ Resposta com informações conectadas
```

### Comparação Visual

**Baseline RAG:**
```
Query → Vector Search → Chunks isolados
```

**Graph RAG:**
```
Query
  ↓
┌─────────────┬─────────────────┐
│ Vector DB   │ Knowledge Graph │
│ (chunks)    │ (relações)      │
├─────────────┼─────────────────┤
│ Chunk 1     │ João Silva      │
│ Chunk 2     │   ↓ [CFO_DE]    │
│ Chunk 3     │ XYZ Corp        │
│             │   ↓ [TRABALHOU] │
│             │ Goldman Sachs   │
└─────────────┴─────────────────┘
  ↓ [Combina contexto]
LLM → Resposta rica em conexões
```

---

## 💡 Por Que Funciona?

### Problema do RAG Tradicional

```python
Query: "Qual a experiência anterior do CFO da XYZ Corp?"

# Vector Search (chunks isolados):
Chunk 1: "CFO da XYZ Corp é João Silva"           ✅ (quem)
Chunk 2: "João Silva graduado em Harvard"        ✅ (educação)
Chunk 3: "Goldman Sachs contratou executivos"    ❌ (não conecta!)
Chunk 4: "Experiência em finanças corporativas"  ❌ (genérico)

# ❌ Chunks NÃO conectam "João Silva" → "Goldman Sachs"
# ❌ Informação está fragmentada
```

### Solução Graph RAG

```python
# Knowledge Graph (estruturado):

(João Silva)-[CFO_DE]->(XYZ Corp)
(João Silva)-[TRABALHOU_EM {anos: 10}]->(Goldman Sachs)
(João Silva)-[FORMADO_EM]->(Harvard)
(Goldman Sachs)-[TIPO]->(Banco de Investimento)

# Query executada:
MATCH (cfo)-[CFO_DE]->(empresa {nome: "XYZ Corp"})
MATCH (cfo)-[TRABALHOU_EM]->(experiencia_anterior)
RETURN cfo, experiencia_anterior

# Resultado:
{
  "cfo": "João Silva",
  "experiencias": [
    {"empresa": "Goldman Sachs", "anos": 10, "cargo": "VP Finanças"}
  ],
  "educacao": [
    {"instituicao": "Harvard", "grau": "MBA"}
  ]
}

# ✅ Informação CONECTADA e ESTRUTURADA
```

---

## 🔬 Exemplo Prático Detalhado

### Caso 1: Multi-Hop Query

**Query:**
```
"Quem são os colegas de João Silva que também trabalharam no Goldman Sachs?"
```

**Baseline RAG (Impossível):**
```python
# Vector search não consegue resolver:
# 1. Identificar colegas de João Silva
# 2. Filtrar só os que passaram por Goldman Sachs
# 3. Conectar as duas condições

❌ Retorna chunks genéricos sobre "colegas" ou "Goldman Sachs"
```

**Graph RAG (Resolve):**
```cypher
// Cypher query (Neo4j)
MATCH (joao:Pessoa {nome: "João Silva"})-[:TRABALHA_COM]->(colega:Pessoa)
MATCH (colega)-[:TRABALHOU_EM]->(gs:Empresa {nome: "Goldman Sachs"})
RETURN colega.nome, colega.cargo

// Resultado:
[
  {"nome": "Maria Santos", "cargo": "COO"},
  {"nome": "Pedro Lima", "cargo": "CTO"}
]

// Chunks adicionais buscados:
- Bio de Maria Santos
- Bio de Pedro Lima
```

**Resposta Final:**
```
"João Silva tem dois colegas que também trabalharam no Goldman Sachs:
Maria Santos (atual COO) trabalhou lá por 8 anos como Diretora...
Pedro Lima (atual CTO) foi VP de Tecnologia..."
```

---

### Caso 2: Inferência de Relações

**Query:**
```
"Produtos da empresa que João Silva fundou antes de entrar na XYZ Corp"
```

**Graph Traversal:**
```cypher
MATCH (joao:Pessoa {nome: "João Silva"})-[:FUNDOU]->(empresa_anterior:Empresa)
MATCH (empresa_anterior)-[:OFERECE]->(produto:Produto)
WHERE joao.entrada_xyz > empresa_anterior.fundacao
RETURN empresa_anterior.nome, produto.nome

// Resultado:
{
  "empresa": "TechStart Inc",
  "produtos": ["CloudSync", "DataFlow"]
}
```

**Vector RAG Sozinho:**
```
❌ Não consegue inferir timeline
❌ Não conecta fundação → entrada XYZ → produtos
```

---

## ⚙️ Configuração Padrão

| Parâmetro | Valor | Justificativa |
|-----------|-------|---------------|
| **Graph DB** | Neo4j | Mais maduro para KG |
| **Entity Extraction** | spaCy + LLM | Precisão NER |
| **Relation Extraction** | GPT-4 / Gemini | Complexo, precisa LLM |
| **Vector DB** | Pinecone | Chunks textuais |
| **Hybrid Weight** | 0.5 Vector + 0.5 Graph | Balance |
| **Max Graph Depth** | 2-3 hops | Evita explosão combinatória |

### Tipos de Entidades Comuns

| Tipo | Exemplos | Uso |
|------|----------|-----|
| **PESSOA** | João Silva, Maria Santos | Stakeholders |
| **EMPRESA** | XYZ Corp, Goldman Sachs | Organizações |
| **LOCAL** | São Paulo, Nova York | Geografia |
| **PRODUTO** | CloudSync, iPhone | Ofertas |
| **EVENTO** | IPO, Fusão, Lançamento | Marcos temporais |
| **CONCEITO** | Machine Learning, ROI | Domínios |

### Tipos de Relações Comuns

| Relação | Exemplo | Direção |
|---------|---------|---------|
| **TRABALHA_EM** | Pessoa → Empresa | Directed |
| **TRABALHOU_EM** | Pessoa → Empresa (passado) | Directed |
| **CFO_DE / CEO_DE** | Pessoa → Empresa | Directed |
| **REPORTA_PARA** | Pessoa → Pessoa | Directed |
| **OFERECE** | Empresa → Produto | Directed |
| **LOCALIZADA_EM** | Empresa → Local | Directed |
| **RELACIONADO_A** | Conceito ↔ Conceito | Undirected |

---

## ✅ Vantagens

### 1. Multi-Hop Queries Nativas
```
✅ "Amigos de amigos que trabalham em tech"
✅ "Produtos de empresas fundadas por ex-alunos de Harvard"
✅ Queries com 3-4 níveis de conexão
```

### 2. Estrutura Explícita
```
Relações são EXPLÍCITAS, não inferidas:
- "João [TRABALHOU_EM] Goldman" (fato)
- Não precisa LLM adivinhar conexão
→ Reduz alucinação
```

### 3. Raciocínio Temporal
```
Grafo armazena timestamps:
- TRABALHOU_EM {inicio: 2010, fim: 2020}
- FUNDOU {data: 2022}

Query: "O que João fez ANTES de fundar empresa?"
→ Filtro temporal nativo
```

### 4. Agregações Complexas
```cypher
// Quantos funcionários da XYZ vieram do Goldman?
MATCH (p:Pessoa)-[:TRABALHOU_EM]->(gs {nome: "Goldman Sachs"})
MATCH (p)-[:TRABALHA_EM]->(xyz {nome: "XYZ Corp"})
RETURN count(p)

// ✅ Agregação impossível em Vector RAG
```

### 5. Explorabilidade
```
User pode "navegar" o grafo:
- Visualizar conexões
- Descobrir padrões inesperados
- Insights emergentes
```

### 6. Precisão Factual
```
Fatos estruturados = menos alucinação
"João Silva É CFO" (grafo)
vs
"João Silva parece ser CFO" (LLM inferindo de chunk)
```

---

## ❌ Desvantagens

### 1. Complexidade de Setup Extrema
```
Baseline: Carregar docs → Embed → Pinecone (30 min)

Graph RAG:
1. Carregar docs (5 min)
2. NER - extrair entidades (2h com LLM)
3. Relation extraction (4h com LLM)
4. Construir grafo no Neo4j (1h)
5. Validar/limpar relações (2h manual)
6. Integrar Vector + Graph (1h código)

Total: 8-10 horas vs 30 minutos
```

### 2. Custo de Indexação Massivo
```
# Relation Extraction com LLM:
- 1000 documentos
- ~500 parágrafos/doc = 500K parágrafos
- GPT-4: $0.01/1K tokens
- Avg 200 tokens/parágrafo

Custo: 500K × 0.2K × $0.01/1K = $1,000+ APENAS indexação
Baseline: ~$5-10
```

### 3. Manutenção do Grafo
```
Documentos atualizam:
- "João Silva agora é CEO (não mais CFO)"

❌ Precisa:
1. Detectar mudança
2. Atualizar relações no grafo
3. Manter consistência

Grafo pode ficar desatualizado rapidamente
```

### 4. Latência em Queries Complexas
```
Cypher query com 3-4 hops:
MATCH (a)-[r1]->(b)-[r2]->(c)-[r3]->(d)

Em grafo grande (>100K nós):
- Pode levar 2-5 segundos APENAS no grafo
- + Vector search (1s)
- + LLM generation (1s)

Total: 4-7 segundos
```

### 5. Erros em Entity/Relation Extraction
```
NER pode errar:
"Apple lançou iPhone" →
  ❌ "Apple" detectado como [FRUTA], não [EMPRESA]

Relation extraction pode errar:
"João trabalhou COM Maria" →
  ❌ Extrai: João [TRABALHOU_EM] Maria (relação errada!)

Erros propagam pelo grafo → Respostas incorretas
```

### 6. Não Funciona para Todo Domínio
```
✅ Bom para: Conhecimento factual estruturado
   - Org charts, relações corporativas
   - História, genealogia
   - Redes sociais profissionais

❌ Ruim para: Conhecimento conceitual abstrato
   - "Como funciona machine learning?"
   - Tutoriais, guias
   - Documentação técnica
```

### 7. Escalabilidade
```
Neo4j performance degrada com:
- >10M nós
- >100M arestas
- Queries multi-hop em grafo denso

Precisa sharding, otimizações complexas
```

---

## 📊 Métricas Esperadas

### RAGAS Scores vs Baseline

| Métrica | Baseline | Graph RAG | Δ | Contexto |
|---------|----------|-----------|---|----------|
| **Faithfulness** | 0.75-0.85 | 0.90-0.98 | +15-20% | Fatos estruturados |
| **Answer Relevancy** | 0.70-0.85 | 0.80-0.92 | +10-15% | Conexões explícitas |
| **Context Precision** | 0.60-0.75 | 0.75-0.88 | +15-20% | Relações filtradas |
| **Context Recall** | 0.50-0.70 | 0.70-0.90 | +30-40% | Multi-hop retrieval |

**Nota**: Métricas APENAS para queries que se beneficiam de grafo (multi-hop, relações).

### Performance

| Métrica | Baseline | Graph RAG |
|---------|----------|-----------|
| **Latência (query simples)** | 1.2-2.5s | 2.0-4.0s |
| **Latência (multi-hop)** | N/A | 3.0-7.0s |
| **Custo/Query** | $0.001-0.003 | $0.002-0.005 |
| **Indexação (1K docs)** | $5-10 | $500-1500 |
| **Indexação (tempo)** | 30 min | 6-10 horas |

---

## 🎯 Quando Usar Graph RAG

### ✅ Casos Ideais

**1. Queries Multi-Hop e Relacionais**
```
✅ "Quem são colegas de X que trabalharam em Y?"
✅ "Produtos de empresas fundadas por ex-funcionários"
✅ "Cadeia de comando: quem reporta para quem?"
```

**2. Conhecimento Factual Estruturado**
```
✅ Org charts corporativos
✅ Genealogia / árvores familiares
✅ Redes de citações acadêmicas
✅ Supply chain / fornecedores
```

**3. Análise de Redes**
```
✅ "Qual a pessoa mais conectada?" (centrality)
✅ "Identificar comunidades/clusters"
✅ "Caminhos mais curtos entre entidades"
```

**4. Raciocínio Temporal**
```
✅ "O que aconteceu ANTES de X?"
✅ "Sequência de eventos que levaram a Y"
✅ "Timeline de carreira de uma pessoa"
```

**5. Domínios com Relacionamentos Ricos**
```
✅ Legal (jurisprudência, citações de leis)
✅ Biomedicina (proteínas, genes, doenças)
✅ Finanças (investimentos, acionistas)
```

---

### ❌ Quando NÃO Usar

**1. Conhecimento Não-Estruturado**
```
❌ Tutoriais "como fazer"
❌ Documentação técnica conceitual
❌ Literatura, artigos opinativos
→ Use Baseline ou HyDE
```

**2. Budget Limitado**
```
❌ Indexação custa 100-300x baseline
❌ Precisa time de engenharia dedicado
❌ Manutenção contínua do grafo
```

**3. Dados Voláteis**
```
❌ Informação muda diariamente
❌ Atualização de grafo = custosa
→ Use Vector RAG (re-index mais fácil)
```

**4. Queries Simples**
```
❌ Lookup direto ("Qual o telefone?")
❌ FAQs básicas
→ Overhead de grafo não compensa
```

**5. Sem Infraestrutura**
```
❌ Neo4j = complexo (vs Pinecone SaaS simples)
❌ Precisa expertise em Cypher
❌ Monitoramento de DB adicional
```

**6. Prototipagem Rápida**
```
❌ Precisa validar ideia em 1 semana
❌ MVP com 0 custo
→ Comece com Baseline, adicione Graph depois
```

---

## 🔬 Experimentos Recomendados

### 1. Hybrid Weight Tuning
```python
# Testar: 0.3 vector + 0.7 graph, 0.5/0.5, 0.7/0.3
# Medir: Precision vs Recall
# Hipótese: Depende do tipo de query
```

### 2. Graph Depth Limit
```cypher
# Testar: max_depth = 1, 2, 3, 4
# Medir: Recall vs Latência
# Hipótese: depth=2 suficiente para 90% queries
```

### 3. Entity Extraction Quality
```python
# Comparar:
# - spaCy (rápido, impreciso)
# - GPT-4 (lento, preciso)
# - Fine-tuned BERT (balance)
# Medir: F1 de entidades vs Custo
```

### 4. Relation Extraction Prompting
```python
# Testar diferentes prompts para LLM
# Medir: Precisão de relações extraídas
# Validação manual em sample de 100 relações
```

---

## 💻 Estrutura de Código

```python
# graph_rag.py

from neo4j import GraphDatabase
import spacy

class GraphRAG:
    """
    RAG com Knowledge Graph para queries relacionais.

    Pipeline:
    1. Hybrid retrieval (Vector + Graph)
    2. Merge contextos
    3. LLM generation
    """

    def __init__(self, pinecone_index, embeddings, llm, neo4j_uri, neo4j_user, neo4j_password):
        # Vector DB
        self.index = pinecone_index
        self.embeddings = embeddings
        self.llm = llm

        # Graph DB
        self.graph_driver = GraphDatabase.driver(
            neo4j_uri,
            auth=(neo4j_user, neo4j_password)
        )

        # NER
        self.nlp = spacy.load("pt_core_news_lg")

        self.k_vector = 5
        self.k_graph = 5
        self.hybrid_weight = 0.5  # 50% vector, 50% graph

    def extract_entities(self, query: str) -> List[str]:
        """
        Extrai entidades da query (NER).
        """
        doc = self.nlp(query)
        entities = [ent.text for ent in doc.ents]
        return entities

    def vector_search(self, query: str, k: int) -> List[Document]:
        """
        Busca vetorial tradicional.
        """
        query_vector = self.embeddings.embed_query(query)

        results = self.index.query(
            vector=query_vector,
            top_k=k,
            include_metadata=True
        )

        return self._parse_results(results)

    def graph_search(self, entities: List[str], query: str) -> List[Dict]:
        """
        Busca no grafo de conhecimento.
        """
        if not entities:
            return []

        # Cypher query dinâmica
        cypher = f"""
        MATCH (e:Entity)
        WHERE e.name IN {entities}
        OPTIONAL MATCH (e)-[r]-(connected:Entity)
        RETURN e, r, connected
        LIMIT {self.k_graph}
        """

        with self.graph_driver.session() as session:
            result = session.run(cypher)
            graph_data = []

            for record in result:
                entity = record.get("e")
                relation = record.get("r")
                connected = record.get("connected")

                if entity and connected and relation:
                    graph_data.append({
                        "entity": dict(entity),
                        "relation": type(relation).__name__,
                        "connected": dict(connected)
                    })

        return graph_data

    def graph_to_text(self, graph_data: List[Dict]) -> str:
        """
        Converte dados do grafo em texto para LLM.
        """
        text_parts = []

        for item in graph_data:
            entity = item["entity"]["name"]
            relation = item["relation"]
            connected = item["connected"]["name"]

            text_parts.append(
                f"{entity} {relation} {connected}"
            )

        return "\n".join(text_parts)

    def hybrid_retrieval(self, query: str) -> Tuple[List[Document], str]:
        """
        Combina Vector + Graph retrieval.
        """
        # 1. Extrair entidades da query
        entities = self.extract_entities(query)

        # 2. Vector search
        vector_chunks = self.vector_search(query, self.k_vector)

        # 3. Graph search
        graph_data = self.graph_search(entities, query)
        graph_context = self.graph_to_text(graph_data)

        return vector_chunks, graph_context

    def generate(self, query: str, vector_chunks: List[Document], graph_context: str) -> str:
        """
        Geração com contexto híbrido.
        """
        # Montar contexto combinado
        context_parts = []

        # Contexto do grafo (relações estruturadas)
        if graph_context:
            context_parts.append("Relações conhecidas:")
            context_parts.append(graph_context)
            context_parts.append("")

        # Contexto vetorial (chunks de texto)
        context_parts.append("Informações adicionais:")
        for chunk in vector_chunks:
            context_parts.append(chunk.page_content)
            context_parts.append("")

        full_context = "\n".join(context_parts)

        # Prompt
        prompt = f"""
Contexto:
{full_context}

Pergunta: {query}

Responda baseado no contexto acima, priorizando as relações estruturadas.
"""

        response = self.llm.invoke(prompt, temperature=0.0)
        return response.content

    def query(self, query: str) -> Dict:
        """
        Pipeline completo Graph RAG.
        """
        start_time = time.time()

        # 1. Hybrid retrieval
        t1 = time.time()
        vector_chunks, graph_context = self.hybrid_retrieval(query)
        retrieval_time = time.time() - t1

        # 2. Generation
        t2 = time.time()
        response = self.generate(query, vector_chunks, graph_context)
        generation_time = time.time() - t2

        total_latency = time.time() - start_time

        return {
            "response": response,
            "vector_chunks": vector_chunks,
            "graph_context": graph_context,
            "metrics": {
                "latency_total": total_latency,
                "latency_retrieval": retrieval_time,
                "latency_generation": generation_time,
                "chunks_vector": len(vector_chunks),
                "graph_relations": len(graph_context.split('\n')) if graph_context else 0,
                "technique": "graph_rag"
            }
        }

    def close(self):
        """
        Fechar conexão com Neo4j.
        """
        self.graph_driver.close()
```

---

## 🎓 Construção do Knowledge Graph

### Entity Extraction
```python
def extract_entities_with_llm(document: str) -> List[Dict]:
    """
    Extrai entidades usando LLM.
    """
    prompt = f"""
Analise o texto abaixo e extraia todas as entidades.

Para cada entidade, identifique:
- Nome
- Tipo (PESSOA, EMPRESA, LOCAL, PRODUTO, EVENTO, CONCEITO)

Texto:
{document}

Retorne JSON:
[{{"nome": "...", "tipo": "..."}}]
"""

    response = llm.invoke(prompt)
    entities = json.loads(response.content)
    return entities
```

### Relation Extraction
```python
def extract_relations_with_llm(document: str, entities: List[Dict]) -> List[Dict]:
    """
    Extrai relações entre entidades.
    """
    entities_str = ", ".join([e["nome"] for e in entities])

    prompt = f"""
Identifique relações entre estas entidades no texto:
{entities_str}

Texto:
{document}

Para cada relação, especifique:
- entidade_origem
- tipo_relacao (TRABALHA_EM, CEO_DE, FUNDOU, etc)
- entidade_destino

Retorne JSON:
[{{"origem": "...", "relacao": "...", "destino": "..."}}]
"""

    response = llm.invoke(prompt)
    relations = json.loads(response.content)
    return relations
```

### Graph Construction
```python
def build_knowledge_graph(documents: List[str]):
    """
    Constrói grafo de conhecimento.
    """
    graph = GraphDatabase.driver(neo4j_uri, auth=(user, password))

    for doc in documents:
        # 1. Extrair entidades
        entities = extract_entities_with_llm(doc)

        # 2. Criar nós no grafo
        with graph.session() as session:
            for entity in entities:
                session.run(
                    "MERGE (e:Entity {name: $name, type: $type})",
                    name=entity["nome"],
                    type=entity["tipo"]
                )

        # 3. Extrair relações
        relations = extract_relations_with_llm(doc, entities)

        # 4. Criar arestas no grafo
        with graph.session() as session:
            for rel in relations:
                session.run(f"""
                    MATCH (origem:Entity {{name: $origem}})
                    MATCH (destino:Entity {{name: $destino}})
                    MERGE (origem)-[r:{rel["relacao"]}]->(destino)
                """,
                    origem=rel["origem"],
                    destino=rel["destino"]
                )
```

---

## 📚 Referências

**Papers:**
- Microsoft GraphRAG (2024) - "From Local to Global: A Graph RAG Approach"
- Yasunaga et al. (2022) - "Deep Bidirectional Language-Knowledge Graph Pretraining"

**Frameworks:**
- Neo4j + LangChain integration
- LlamaIndex Knowledge Graph Index
- Microsoft GraphRAG (open source)

**Benchmarks:**
- WebQSP (multi-hop): +22% accuracy vs RAG
- ComplexWebQuestions: +15% F1

---

## 🎯 Aprendizados Chave

1. **Estrutura > Texto**: Relações explícitas reduzem alucinação
2. **Multi-Hop Nativo**: Grafo resolve queries impossíveis para RAG
3. **Trade-off Brutal**: 100x custo de setup para 20-30% melhoria
4. **Domínio-Específico**: Não é silver bullet, funciona para conhecimento factual
5. **Hybrid é Essential**: Graph sozinho = incompleto. Precisa Vector também

---

## 📈 Progressão de Complexidade

```
Baseline RAG (chunks isolados)
    ↓
Sub-Query (múltiplas buscas)
    ↓
Fusion (múltiplas estratégias)
    ↓
Graph RAG (você está aqui) = Conhecimento estruturado
    ↓
Microsoft GraphRAG (global + local communities)
```

---

**Técnica Anterior**: [Fusion](./FUSION.md)
**Resumo Comparativo**: [COMPARISON.md](./COMPARISON.md) *(próximo)*
