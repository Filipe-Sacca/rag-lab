#!/bin/bash
# Script para limpar CORRETAMENTE o banco de dados RAG Lab
# Limpa TODAS as tabelas para evitar registros órfãos

DB_PATH="backend/rag_lab.db"
EVENTS_DB="/root/Filipe/Teste-Claude/apps/server/events.db"

echo "🧹 Limpando bancos de dados..."
echo ""

# RAG Lab Database
echo "📊 RAG Lab (rag_lab.db):"
sqlite3 "$DB_PATH" << 'EOF'
DELETE FROM rag_metrics;
DELETE FROM rag_analyses;
DELETE FROM rag_executions;
VACUUM;
SELECT 'rag_executions: ' || COUNT(*) as count FROM rag_executions;
SELECT 'rag_metrics: ' || COUNT(*) as count FROM rag_metrics;
SELECT 'rag_analyses: ' || COUNT(*) as count FROM rag_analyses;
EOF

echo ""

# Observability Database
echo "📡 Observability (events.db):"
if [ -f "$EVENTS_DB" ]; then
    sqlite3 "$EVENTS_DB" << 'EOF'
DELETE FROM events;
VACUUM;
SELECT 'events: ' || COUNT(*) as count FROM events;
EOF
else
    echo "⚠️  events.db não encontrado (ok se não usa observability)"
fi

echo ""
echo "✅ Bancos de dados limpos!"
echo ""
echo "💡 Dica: Use este script sempre antes de começar novos testes"
echo "   ./clean_database.sh"
