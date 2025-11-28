#!/bin/bash
# Script para verificar se serviços estão rodando

echo "🔍 Verificando serviços do RAG Lab..."
echo ""

# Verificar Backend
echo "📦 Backend (FastAPI):"
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "   ✅ Rodando em http://localhost:8000"
    echo "   📄 Docs: http://localhost:8000/docs"
    curl -s http://localhost:8000/health | python3 -m json.tool 2>/dev/null || echo ""
else
    echo "   ❌ NÃO está rodando"
    echo "   💡 Inicie com: cd backend && uvicorn main:app --reload"
fi

echo ""

# Verificar Frontend
echo "🎨 Frontend:"
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "   ✅ Rodando em http://localhost:5173"
elif curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "   ✅ Rodando em http://localhost:3000"
else
    echo "   ❌ NÃO está rodando"
    echo "   💡 Inicie com: cd frontend && npm run dev"
fi

echo ""

# Verificar processos
echo "🔧 Processos ativos:"
ps aux | grep -E "(uvicorn|vite|node.*dev)" | grep -v grep | awk '{print "   " $11 " " $12 " " $13}'

echo ""
