#!/bin/bash
# Script para iniciar Backend + Frontend do RAG Lab

echo "🚀 Iniciando RAG Lab..."
echo ""

# Cores para output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para limpar processos ao sair
cleanup() {
    echo ""
    echo "🛑 Encerrando servidores..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

# Captura Ctrl+C
trap cleanup SIGINT SIGTERM

# Iniciar Backend
echo -e "${BLUE}📦 Iniciando Backend (FastAPI)...${NC}"
cd backend

# Ativar venv se existir
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Iniciar uvicorn em background
uvicorn main:app --reload --host 0.0.0.0 --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

echo -e "${GREEN}✅ Backend rodando em http://localhost:8000${NC}"
echo -e "${GREEN}   Documentação: http://localhost:8000/docs${NC}"
echo ""

# Aguardar backend iniciar
sleep 3

# Iniciar Frontend
echo -e "${BLUE}🎨 Iniciando Frontend (Vite/React)...${NC}"
cd ../frontend

# Verificar se node_modules existe
if [ ! -d "node_modules" ]; then
    echo "📥 Instalando dependências do frontend..."
    npm install
fi

# Iniciar frontend em background
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo -e "${GREEN}✅ Frontend rodando${NC}"
echo ""

# Aguardar frontend iniciar e pegar a porta
sleep 5

# Tentar detectar a porta do frontend
FRONTEND_PORT=$(grep -oP 'localhost:\K\d+' ../frontend.log | head -1)
if [ -n "$FRONTEND_PORT" ]; then
    echo -e "${GREEN}🌐 Acesse a aplicação: http://localhost:${FRONTEND_PORT}${NC}"
else
    echo -e "${GREEN}🌐 Acesse a aplicação: http://localhost:5173${NC}"
fi

echo ""
echo "📋 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "⚠️  Pressione Ctrl+C para parar ambos os servidores"
echo ""

# Manter script rodando
wait
