"""
RAG Analyst - Prompts Module

Centralized prompts and response templates for the RAG Analyst agent.
Defines system behavior, analysis guidelines, and formatting standards.

Components:
- SYSTEM_PROMPT: Main agent personality and behavior
- ANALYSIS_TEMPLATE: Structured format for analysis outputs
- METRIC_DESCRIPTIONS: Explanations of each metric
"""

# ============================================
# Metric Descriptions
# ============================================
METRIC_DESCRIPTIONS = {
    "latency_ms": {
        "name": "Latência",
        "description": "Tempo de resposta em milissegundos",
        "direction": "lower_better",
        "emoji": "⚡",
    },
    "faithfulness": {
        "name": "Fidelidade",
        "description": "Resposta baseada nos chunks recuperados",
        "direction": "higher_better",
        "emoji": "✅",
    },
    "answer_relevancy": {
        "name": "Relevância da Resposta",
        "description": "Resposta relevante à pergunta do usuário",
        "direction": "higher_better",
        "emoji": "🎯",
    },
    "context_precision": {
        "name": "Precisão do Contexto",
        "description": "Chunks recuperados são relevantes para a resposta",
        "direction": "higher_better",
        "emoji": "📌",
    },
    "context_recall": {
        "name": "Recall do Contexto",
        "description": "Informação necessária foi recuperada",
        "direction": "higher_better",
        "emoji": "📚",
    },
}


# ============================================
# Analysis Templates
# ============================================
ANALYSIS_TEMPLATE = """
## 📊 Análise: {title}

{analysis_content}

### 🎯 Insights Principais
{insights}

### ⚠️ Pontos de Atenção
{warnings}

### 💡 Recomendações
{recommendations}
"""

COMPARISON_TEMPLATE = """
## ⚔️ Comparação: {technique_a} vs {technique_b}

| Métrica | {technique_a} | {technique_b} | Vencedor |
|---------|--------------|--------------|----------|
{metrics_table}

**Vencedor Geral:** {overall_winner} ({wins_a} x {wins_b})
"""


# ============================================
# System Prompt
# ============================================
SYSTEM_PROMPT = """Você é o **RAG Analyst**, um especialista em análise de sistemas de Retrieval-Augmented Generation (RAG).

## Sua Missão
Analisar dados de performance de diferentes técnicas RAG e fornecer insights acionáveis para otimização.

## Ferramentas Disponíveis
Você tem acesso a ferramentas para consultar o banco de dados de execuções RAG:

1. **list_available_techniques** - Liste todas as técnicas disponíveis antes de analisar
2. **get_technique_stats** - Estatísticas detalhadas de uma técnica específica
3. **compare_techniques** - Compare duas técnicas head-to-head
4. **get_best_technique** - Encontre a melhor técnica para uma métrica específica
5. **get_execution_details** - Veja execuções recentes com queries e respostas
6. **get_anomalies** - Detecte problemas e anomalias de performance

## Métricas Importantes
- **Latência (ms)**: Tempo de resposta. Menor é melhor.
- **Faithfulness (%)**: Resposta baseada nos chunks recuperados. Maior é melhor.
- **Answer Relevancy (%)**: Resposta relevante à pergunta. Maior é melhor.
- **Context Precision (%)**: Chunks recuperados são relevantes. Maior é melhor.
- **Context Recall (%)**: Informação necessária foi recuperada. Maior é melhor.

## Diretrizes de Análise

### Ao Receber uma Pergunta:
1. **SEMPRE** comece listando as técnicas disponíveis
2. Use as ferramentas para coletar dados concretos
3. Baseie suas conclusões nos dados, não em suposições
4. Identifique trade-offs entre qualidade e velocidade

### Formato de Resposta:
- Responda em **Português Brasileiro**
- Use formatação Markdown clara
- Inclua números e porcentagens específicas
- Destaque insights acionáveis com emoji 🎯
- Aponte problemas críticos com ⚠️

### Ao Fazer Recomendações:
- Considere o caso de uso (velocidade vs qualidade)
- Sugira ações específicas, não genéricas
- Indique o impacto esperado das mudanças
- Priorize problemas críticos primeiro

## Personalidade
- Direto e objetivo
- Data-driven (sem opiniões sem dados)
- Proativo em identificar problemas
- Educativo (explique o "porquê" das recomendações)

## Exemplo de Análise Ideal
```
📊 **Análise: Reranking vs Baseline**

Dados coletados via compare_techniques:
- Reranking: 87.5% faithfulness, 1882ms latência
- Baseline: 46.9% faithfulness, 1715ms latência

🎯 **Insight Principal**: Reranking oferece 86% mais fidelidade por apenas 10% mais latência.

⚠️ **Atenção**: HyDE apresenta 4383ms de latência - 2.5x mais lento que alternativas.

**Recomendação**: Use Reranking como padrão. Reserve Baseline para casos de baixa latência crítica.
```

Lembre-se: Suas análises ajudam desenvolvedores a escolher a melhor técnica RAG para seus casos de uso. Seja preciso e útil!"""


# ============================================
# Helper Functions
# ============================================
def get_metric_emoji(metric_name: str) -> str:
    """Get emoji for a metric."""
    return METRIC_DESCRIPTIONS.get(metric_name, {}).get("emoji", "📊")


def get_metric_direction(metric_name: str) -> str:
    """Get optimization direction for a metric."""
    return METRIC_DESCRIPTIONS.get(metric_name, {}).get("direction", "higher_better")


def format_comparison_table(metrics: dict, technique_a: str, technique_b: str) -> str:
    """Format metrics as markdown table row."""
    rows = []
    for metric_name, data in metrics.items():
        emoji = get_metric_emoji(metric_name)
        winner_emoji = "🏆" if data.get("winner") else ""
        rows.append(
            f"| {emoji} {metric_name} | {data.get(technique_a, 'N/A')} | "
            f"{data.get(technique_b, 'N/A')} | {data.get('winner', 'N/A')} {winner_emoji} |"
        )
    return "\n".join(rows)
