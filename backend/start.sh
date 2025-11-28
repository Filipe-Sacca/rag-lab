#!/bin/bash
# RAG Lab Backend Startup Script
# Carrega variáveis de ambiente e inicia servidor

set -e

# Diretório do script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "🚀 Starting RAG Lab Backend..."

# Verificar se .env existe
if [[ ! -f .env ]]; then
    echo "❌ Error: .env file not found"
    echo "Copy .env.example to .env and configure your API keys"
    exit 1
fi

# Carregar variáveis do .env
echo "📋 Loading environment variables from .env..."
set -a
source .env
set +a

# Verificar API keys obrigatórias
if [[ -z "$GOOGLE_API_KEY" ]]; then
    echo "❌ Error: GOOGLE_API_KEY not set in .env"
    exit 1
fi

if [[ -z "$PINECONE_API_KEY" ]]; then
    echo "❌ Error: PINECONE_API_KEY not set in .env"
    exit 1
fi

if [[ -z "$COHERE_API_KEY" ]]; then
    echo "❌ Error: COHERE_API_KEY not set in .env"
    exit 1
fi

echo "✅ Environment variables loaded"
echo "   - GOOGLE_API_KEY: ${GOOGLE_API_KEY:0:20}..."
echo "   - PINECONE_API_KEY: ${PINECONE_API_KEY:0:20}..."
echo "   - COHERE_API_KEY: ${COHERE_API_KEY:0:20}..."

# Ativar ambiente virtual
if [[ -d "venv" ]]; then
    echo "🐍 Activating virtual environment..."
    source venv/bin/activate
else
    echo "❌ Error: venv not found. Run: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# Iniciar servidor
echo "🌐 Starting Uvicorn server on ${BACKEND_HOST:-0.0.0.0}:${BACKEND_PORT:-8000}..."
echo ""

uvicorn main:app \
    --host "${BACKEND_HOST:-0.0.0.0}" \
    --port "${BACKEND_PORT:-8000}" \
    --reload
