# 🧪 Sistema de Testes RAG Lab

Sistema completo para testar e comparar as 8 técnicas RAG de forma objetiva.

## 📁 Arquivos

- **TESTE_PLAN.md** - Plano detalhado com 10 perguntas universais e instruções
- **TESTE_PLANILHA.csv** - Template de planilha para coleta manual
- **run_tests.py** - Script para execução automatizada via API
- **export_results.py** - Script para exportar resultados do banco para CSV

---

## 🚀 Opção 1: Testes Manuais (Frontend)

### Vantagens
- ✅ Visualiza respostas em tempo real
- ✅ Melhor para análise qualitativa
- ✅ Interface amigável

### Processo

1. **Abra o frontend**: http://localhost:9091

2. **Siga o TESTE_PLAN.md**:
   - 10 perguntas × 8 técnicas = 80 testes
   - Escolha abordagem: Por Pergunta (recomendado) ou Por Técnica

3. **Para cada teste**:
   - Selecione técnica no dropdown
   - Copie pergunta do TESTE_PLAN.md
   - Cole e envie
   - Aguarde resposta
   - Anote observações manualmente

4. **Após completar**:
   ```bash
   python export_results.py
   ```
   - Gera `TESTE_RESULTS.csv` com métricas automáticas
   - Preencha colunas manuais: Qualidade (1-5), Relevância (1-5), Observações

---

## ⚡ Opção 2: Testes Automatizados (Scripts)

### Vantagens
- ✅ Muito mais rápido (1-2h vs 3h)
- ✅ Consistente (sem erros de digitação)
- ✅ Rodável em background

### Processo

**Rodar todos os testes (80)**:
```bash
python run_tests.py
```

**Testar apenas uma técnica**:
```bash
python run_tests.py --technique baseline
python run_tests.py -t hyde
```

**Testar apenas uma pergunta**:
```bash
python run_tests.py --question 1  # Testa Q1 em todas técnicas
python run_tests.py -q 5          # Testa Q5 em todas técnicas
```

**Ajustar delay entre testes**:
```bash
python run_tests.py --delay 2.0   # 2 segundos entre testes
python run_tests.py -d 0.5        # 0.5 segundos (mais rápido)
```

**Exemplos combinados**:
```bash
# Testar apenas Agentic na Q1, sem delay
python run_tests.py -t agentic -q 1 -d 0

# Testar Baseline, HyDE e Reranking em todas perguntas, delay de 1.5s
python run_tests.py -t baseline && python run_tests.py -t hyde && python run_tests.py -t reranking -d 1.5
```

**Após completar**:
```bash
python export_results.py
```

---

## 📊 Análise de Resultados

### Exportar do Banco

```bash
python export_results.py
```

Gera `TESTE_RESULTS.csv` com:
- ✅ Métricas automáticas: latência, num_sources, scores
- ⏳ Colunas manuais vazias: qualidade, relevância, observações

### SQL Direto no Banco

**Estatísticas por Técnica**:
```bash
cd backend
sqlite3 rag_lab.db << 'EOF'
SELECT
    technique,
    COUNT(*) as total,
    ROUND(AVG(JSON_EXTRACT(metrics, '$.latency_ms')), 2) as avg_latency,
    ROUND(AVG(JSON_EXTRACT(metrics, '$.num_sources')), 2) as avg_sources
FROM rag_executions
GROUP BY technique
ORDER BY avg_latency;
EOF
```

**Head-to-Head de 2 Técnicas**:
```bash
sqlite3 rag_lab.db << 'EOF'
SELECT
    r1.query as pergunta,
    ROUND(r1.latency, 2) as baseline_ms,
    ROUND(r2.latency, 2) as hyde_ms,
    ROUND(r2.latency - r1.latency, 2) as diff_ms
FROM
    (SELECT query, JSON_EXTRACT(metrics, '$.latency_ms') as latency
     FROM rag_executions WHERE technique = 'baseline') r1
JOIN
    (SELECT query, JSON_EXTRACT(metrics, '$.latency_ms') as latency
     FROM rag_executions WHERE technique = 'hyde') r2
ON r1.query = r2.query
ORDER BY diff_ms DESC;
EOF
```

---

## 🎯 Workflow Recomendado

### Preparação
```bash
# 1. Limpar bancos (já feito!)
✅ rag_lab.db: 0 registros
✅ events.db: 0 eventos

# 2. Verificar servidores
curl http://localhost:8000/health  # Backend
curl http://localhost:9091         # Frontend

# 3. Verificar Pinecone
# Documentos já indexados? Se não, indexe primeiro
```

### Execução

**Opção A: Tudo automatizado**
```bash
python run_tests.py --delay 1.0
# ~2 horas, vai pra tomar café ☕
```

**Opção B: Por fases (recomendado)**
```bash
# Fase 1: Técnicas rápidas (baseline, hyde, reranking)
python run_tests.py -t baseline -d 0.5
python run_tests.py -t hyde -d 0.5
python run_tests.py -t reranking -d 1.0

# Fase 2: Técnicas médias (fusion, graph)
python run_tests.py -t fusion -d 1.5
python run_tests.py -t graph -d 1.5

# Fase 3: Técnicas complexas (subquery, agentic, adaptive)
python run_tests.py -t subquery -d 2.0
python run_tests.py -t agentic -d 2.0
python run_tests.py -t adaptive -d 1.0
```

**Opção C: Manual via frontend**
- Abra TESTE_PLAN.md
- Siga instruções passo a passo
- Mais controle, mas mais demorado

### Análise

```bash
# 1. Exportar resultados
python export_results.py

# 2. Abrir TESTE_RESULTS.csv em Excel/Google Sheets

# 3. Preencher colunas manuais:
#    - Qualidade (1-5)
#    - Relevância (1-5)
#    - Observações

# 4. Analisar:
#    - Ordenar por latência
#    - Filtrar por técnica
#    - Comparar qualidade vs latência
#    - Identificar padrões
```

---

## 🔍 Validando Hipóteses

Após coletar dados, valide as hipóteses do TESTE_PLAN.md:

**Performance**:
- [ ] H1: Baseline < HyDE < Reranking < Fusion < SubQuery?
- [ ] H2: Agentic tem latência variável?
- [ ] H3: Adaptive adiciona ~100-200ms overhead?

**Qualidade**:
- [ ] H4: HyDE melhor em Q2, Q5 (conceituais)?
- [ ] H5: Reranking melhor em Q3, Q7 (precisão)?
- [ ] H6: Fusion melhor em Q5 (ambíguas)?
- [ ] H7: SubQuery melhor em Q8 (complexas)?
- [ ] H8: Graph melhor em Q6 (relacionamentos)?

**Comportamento**:
- [ ] H9: Agentic roteia corretamente?
- [ ] H10: Adaptive classifica bem?
- [ ] H11: Agentic itera quando necessário?

**Scores**:
- [ ] H12: Reranking tem scores > Baseline?
- [ ] H13: HyDE pode ter scores menores mas respostas melhores?
- [ ] H14: Fusion normaliza scores via RRF?

---

## 📝 Observações Importantes

### Durante os Testes
- ⚠️ Use perguntas **exatamente** como estão (copie/cole)
- ⚠️ Aguarde resposta completa antes do próximo
- ⚠️ Se der erro, anote e considere repetir
- ⚠️ Latência pode variar com carga do servidor/Pinecone

### Análise
- Compare **mesma pergunta** entre técnicas (head-to-head)
- Latência ≠ Qualidade (nem sempre mais rápido é melhor)
- Scores altos não garantem boa resposta (veja relevância)
- Agentic/Adaptive podem escolher técnica diferente da selecionada

### Problemas Comuns

**Timeout/Erro 500**:
- Algumas técnicas (SubQuery, Graph) são mais lentas
- Aumente timeout no run_tests.py se necessário
- Verifique logs do backend

**Scores muito baixos (<0.5)**:
- Pode ser falta de docs relevantes no Pinecone
- Verifique se documentos foram indexados
- Considere indexar mais conteúdo

**Respostas genéricas**:
- LLM pode estar gerando sem usar sources
- Verifique se sources estão vazios
- Pode ser problema no prompt do LLM

---

## 🎯 Objetivos Finais

Após os 80 testes, você terá:

1. ✅ **Comparação objetiva** de todas técnicas
2. ✅ **Trade-offs claros**: latência vs qualidade vs custo
3. ✅ **Guia de uso**: quando usar cada técnica
4. ✅ **Dados para otimização**: ajustar prompts/config
5. ✅ **Baseline confiável**: para futuras melhorias

---

**Boa sorte nos testes! 🚀**

Para dúvidas, consulte:
- TESTE_PLAN.md (detalhes completos)
- Backend logs (erros/debug)
- Frontend console (client-side issues)
