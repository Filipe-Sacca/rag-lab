# 🧪 Plano de Testes RAG Lab - Comparação Head-to-Head

**Objetivo**: Testar as **mesmas 10 perguntas** em todas as 8 técnicas RAG para comparação objetiva

**Total de Queries**: 80 (10 perguntas × 8 técnicas)

---

## 📋 10 Perguntas Universais

Cada pergunta será testada em **todas as 8 técnicas** (Baseline, HyDE, Reranking, Agentic, Fusion, Sub-Query, Graph, Adaptive)

### 1️⃣ Pergunta Direta/Factual
**"O que é RAG (Retrieval Augmented Generation)?"**
- Tipo: Factual, definitória
- Esperado: Baseline deve ser rápido e preciso
- Desafio: Ver se técnicas avançadas agregam valor

---

### 2️⃣ Pergunta Conceitual
**"Por que RAG é mais confiável que usar apenas LLMs puros sem contexto?"**
- Tipo: Conceitual, explicativa
- Esperado: HyDE deve gerar resposta mais profunda
- Desafio: Ver como cada técnica lida com abstração

---

### 3️⃣ Pergunta de Precisão/Detalhes
**"Quais são os 3 componentes principais de um sistema RAG e suas funções específicas?"**
- Tipo: Lista exata, precisão
- Esperado: Reranking deve encontrar chunks mais relevantes
- Desafio: Ver qual técnica é mais precisa em detalhes

---

### 4️⃣ Pergunta Comparativa
**"Compare embeddings com keyword search: vantagens e desvantagens de cada abordagem"**
- Tipo: Comparação, múltiplos aspectos
- Esperado: Sub-Query pode decompor bem
- Desafio: Ver como cada técnica estrutura comparações

---

### 5️⃣ Pergunta Ambígua/Múltiplas Interpretações
**"Como melhorar a qualidade de um sistema RAG?"**
- Tipo: Aberta, múltiplas respostas válidas
- Esperado: Fusion deve combinar perspectivas
- Desafio: Ver como cada técnica lida com ambiguidade

---

### 6️⃣ Pergunta Sobre Relacionamentos
**"Qual a relação entre chunk size, embeddings e qualidade do retrieval?"**
- Tipo: Relacionamentos, conexões
- Esperado: Graph RAG deve explorar entidades
- Desafio: Ver como cada técnica conecta conceitos

---

### 7️⃣ Pergunta Técnica/Implementação
**"Como funciona o processo de chunking em RAG e quais são os parâmetros importantes?"**
- Tipo: Técnica, processo
- Esperado: Baseline/Reranking devem encontrar doc técnico
- Desafio: Ver qual técnica é melhor para docs técnicos

---

### 8️⃣ Pergunta Complexa/Composta
**"Explique o pipeline completo de RAG desde o upload do documento até a geração da resposta, incluindo todos os componentes e suas interações"**
- Tipo: Complexa, multi-parte
- Esperado: Sub-Query deve decompor bem
- Desafio: Ver como cada técnica lida com complexidade

---

### 9️⃣ Pergunta de Trade-offs
**"Quais são os trade-offs entre latência, custo e qualidade em diferentes técnicas RAG?"**
- Tipo: Trade-offs, balanceamento
- Esperado: Agentic pode iterar para melhor análise
- Desafio: Ver qual técnica analisa trade-offs melhor

---

### 🔟 Pergunta de Casos de Uso
**"Quando usar baseline RAG vs HyDE vs reranking? Dê exemplos de casos de uso para cada"**
- Tipo: Aplicação prática, cenários
- Esperado: Adaptive deve rotear inteligentemente
- Desafio: Ver qual técnica dá recomendações mais úteis

---

## 📊 Matriz de Testes

| Pergunta | Baseline | HyDE | Reranking | Agentic | Fusion | SubQuery | Graph | Adaptive |
|----------|----------|------|-----------|---------|--------|----------|-------|----------|
| Q1: O que é RAG | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q2: Por que RAG > LLM | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q3: 3 componentes | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q4: Compare embeddings | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q5: Como melhorar RAG | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q6: Relação chunk/embed | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q7: Processo chunking | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q8: Pipeline completo | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q9: Trade-offs | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |
| Q10: Quando usar | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ | ⏱️ |

**Total**: 80 testes

---

## 🔄 Processo de Teste (2 Abordagens)

### 🅰️ Abordagem 1: Por Pergunta (Recomendado)
**Testar cada pergunta em todas as técnicas antes de passar para próxima**

```
Q1: "O que é RAG?"
├─ Baseline
├─ HyDE
├─ Reranking
├─ Agentic
├─ Fusion
├─ SubQuery
├─ Graph
└─ Adaptive

Q2: "Por que RAG > LLM?"
├─ Baseline
├─ HyDE
...
```

**Vantagens**:
- ✅ Fácil comparar resultados imediatos
- ✅ Detecta diferenças lado a lado
- ✅ Melhor para análise qualitativa

---

### 🅱️ Abordagem 2: Por Técnica
**Testar todas as perguntas em uma técnica antes de mudar**

```
Baseline:
├─ Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10

HyDE:
├─ Q1, Q2, Q3, Q4, Q5, Q6, Q7, Q8, Q9, Q10
...
```

**Vantagens**:
- ✅ Mais rápido (menos troca de dropdown)
- ✅ Melhor para análise quantitativa
- ✅ Fácil manter ritmo de teste

---

## 📈 Métricas a Coletar

Para **cada teste** (80 no total), anote:

### Métricas Automáticas (do sistema)
- ⏱️ **Latência Total** (ms)
- 🔢 **Número de Sources** recuperados
- 📊 **Scores de Similaridade** (min/avg/max)
- 🔧 **Técnica Real Usada** (importante para Agentic/Adaptive)

### Métricas Manuais (sua avaliação)
- ✅ **Qualidade da Resposta** (1-5):
  - 1: Não responde
  - 2: Resposta parcial/incorreta
  - 3: Responde corretamente mas superficial
  - 4: Resposta boa e completa
  - 5: Resposta excelente, profunda e precisa

- 🎯 **Relevância dos Sources** (1-5):
  - 1: Nenhum source relevante
  - 2: Poucos sources relevantes
  - 3: Metade dos sources são relevantes
  - 4: Maioria dos sources são relevantes
  - 5: Todos sources são altamente relevantes

- 💬 **Observações**: Qualquer comportamento interessante/inesperado

---

## 📋 Template de Anotação

```
=== TESTE #X ===
Pergunta: [Número da pergunta]
Técnica: [Nome da técnica]
Timestamp: [HH:MM:SS]

Métricas Automáticas:
- Latência: _____ms
- Sources: _____
- Scores: min=___ avg=___ max=___
- Técnica Real: ________

Avaliação Manual:
- Qualidade Resposta: [ ] 1  [ ] 2  [ ] 3  [ ] 4  [ ] 5
- Relevância Sources: [ ] 1  [ ] 2  [ ] 3  [ ] 4  [ ] 5
- Observações: ____________________
```

---

## 🎯 Análise Pós-Teste

### SQL: Estatísticas por Técnica
```sql
-- Visão geral por técnica
SELECT
    technique,
    COUNT(*) as total_queries,
    ROUND(AVG(JSON_EXTRACT(metrics, '$.latency_ms')), 2) as avg_latency_ms,
    ROUND(MIN(JSON_EXTRACT(metrics, '$.latency_ms')), 2) as min_latency_ms,
    ROUND(MAX(JSON_EXTRACT(metrics, '$.latency_ms')), 2) as max_latency_ms,
    ROUND(AVG(JSON_EXTRACT(metrics, '$.num_sources')), 2) as avg_sources
FROM rag_executions
GROUP BY technique
ORDER BY avg_latency_ms;
```

### SQL: Estatísticas por Pergunta
```sql
-- Ver como cada pergunta se comportou
SELECT
    query,
    COUNT(DISTINCT technique) as techniques_tested,
    ROUND(AVG(JSON_EXTRACT(metrics, '$.latency_ms')), 2) as avg_latency_ms,
    ROUND(AVG(JSON_EXTRACT(metrics, '$.num_sources')), 2) as avg_sources
FROM rag_executions
GROUP BY query
ORDER BY avg_latency_ms DESC;
```

### SQL: Head-to-Head de 2 Técnicas
```sql
-- Comparar Baseline vs HyDE nas mesmas queries
SELECT
    r1.query,
    ROUND(r1.latency_ms, 2) as baseline_latency,
    ROUND(r2.latency_ms, 2) as hyde_latency,
    ROUND(r2.latency_ms - r1.latency_ms, 2) as diff_ms,
    r1.num_sources as baseline_sources,
    r2.num_sources as hyde_sources
FROM
    (SELECT * FROM rag_executions WHERE technique = 'baseline') r1
JOIN
    (SELECT * FROM rag_executions WHERE technique = 'hyde') r2
ON r1.query = r2.query
ORDER BY diff_ms DESC;
```

---

## 📊 Hipóteses a Validar

### ⚡ Performance
- **H1**: Baseline < HyDE < Reranking < Fusion < SubQuery (latência)
- **H2**: Agentic tem latência variável (depende de iterações)
- **H3**: Adaptive adiciona overhead de classificação (~100-200ms)

### 🎯 Qualidade
- **H4**: HyDE é melhor em perguntas conceituais (Q2, Q5)
- **H5**: Reranking é melhor em perguntas de precisão (Q3, Q7)
- **H6**: Fusion é melhor em perguntas ambíguas (Q5)
- **H7**: SubQuery é melhor em perguntas complexas (Q8)
- **H8**: Graph é melhor em perguntas de relacionamento (Q6)

### 🤖 Comportamento de Agentes
- **H9**: Agentic roteia corretamente baseado no tipo de query
- **H10**: Adaptive classifica queries corretamente
- **H11**: Agentic itera quando primeiro resultado é insatisfatório

### 📈 Scores
- **H12**: Reranking tem scores mais altos que Baseline (cross-encoder > bi-encoder)
- **H13**: HyDE pode ter scores mais baixos mas respostas melhores
- **H14**: Fusion normaliza scores via RRF

---

## ✅ Checklist de Preparação

- [x] Banco de dados limpo (`rag_lab.db`: 0 registros)
- [x] Observability limpo (`events.db`: 0 eventos)
- [ ] Backend rodando (http://localhost:8000)
- [ ] Frontend rodando (http://localhost:9091)
- [ ] Documentos indexados no Pinecone
- [ ] Template de anotação impresso/aberto
- [ ] Cronômetro/timer disponível
- [ ] Papel ou planilha para anotações

---

## 🚀 Instruções de Execução

### Passo a Passo

1. **Escolha a abordagem** (Por Pergunta ou Por Técnica)

2. **Para cada teste**:
   - Selecione a técnica no dropdown
   - Copie a pergunta exatamente como está
   - Cole no frontend
   - ⏱️ Inicie o cronômetro (se quiser validar latência)
   - Clique em "Enviar"
   - Aguarde a resposta completa
   - Anote as métricas automáticas (latência, sources, scores)
   - Avalie manualmente (qualidade, relevância)
   - Anote observações interessantes

3. **Salve os dados**:
   - As métricas automáticas já estão no banco
   - Suas avaliações manuais devem ser registradas à parte

4. **Ao final dos 80 testes**:
   - Execute as queries SQL de análise
   - Compare resultados quantitativos vs qualitativos
   - Valide as hipóteses
   - Identifique pontos fortes/fracos de cada técnica

---

## 🎯 Objetivos do Teste

1. ✅ **Comparação Objetiva**: Mesmas perguntas = comparação justa
2. ✅ **Identificar Pontos Fortes**: Quando cada técnica brilha
3. ✅ **Detectar Fraquezas**: Quando cada técnica falha
4. ✅ **Validar Roteamento**: Agentic e Adaptive escolhem certo?
5. ✅ **Trade-off Analysis**: Latência vs Qualidade vs Custo
6. ✅ **Otimização**: Insights para melhorar prompts/config
7. ✅ **Documentação**: Guia de quando usar cada técnica

---

## 📝 Notas Importantes

- ⚠️ **Não mude as perguntas** entre técnicas - use exatamente o mesmo texto
- ⚠️ **Aguarde resposta completa** antes do próximo teste
- ⚠️ **Anote imediatamente** - não confie na memória depois
- ⚠️ **Se der erro**, anote o erro e considere se deve repetir o teste
- ⚠️ **Tempo total estimado**: ~2-3 horas (80 testes × 2min média)

---

**Data do Teste**: ___________
**Testador**: ___________
**Versão**: v2.0 (Head-to-Head)
**Abordagem Escolhida**: [ ] Por Pergunta  [ ] Por Técnica
