# 🚀 Comandos Rápidos - RAG Lab

## Comandos Principais

### ⚡ Iniciar tudo (Backend + Frontend)
```bash
npm run dev
```
**O que faz:** Inicia backend (porta 8000) e frontend (porta 9091) simultaneamente com hot-reload

---

### 🛑 Parar todos os servidores
```bash
npm run kill
```
**O que faz:** Para backend e frontend de forma segura

---

### 🔄 Reiniciar tudo
```bash
npm run restart
```
**O que faz:** Para tudo, aguarda 2 segundos, e reinicia

---

## Comandos Individuais

### 🔧 Apenas Backend
```bash
npm run backend
```
Inicia FastAPI em http://localhost:8000

### 🎨 Apenas Frontend
```bash
npm run frontend
```
Inicia React/Vite (porta automática, geralmente 9091)

---

## Utilitários

### ✅ Verificar Status
```bash
npm run check
```
Testa se backend está respondendo

### 📋 Ver Logs
```bash
# Backend
npm run logs:backend

# Frontend
npm run logs:frontend
```

### 📦 Instalar Dependências
```bash
# Frontend (na raiz)
npm run install

# Backend (Python)
npm run install:backend
```

---

## URLs Importantes

| Serviço | URL |
|---------|-----|
| **Frontend** | http://localhost:9091 |
| **Backend API** | http://localhost:8000 |
| **Documentação** | http://localhost:8000/docs |
| **Health Check** | http://localhost:8000/health |

---

## Workflow Recomendado

### Primeiro uso:
```bash
# 1. Instalar dependências
npm install

# 2. Configurar .env (backend)
# Editar: backend/.env com suas API keys

# 3. Iniciar tudo
npm run dev

# 4. Acessar: http://localhost:9091
```

### Desenvolvimento diário:
```bash
# Iniciar
npm run dev

# Parar (Ctrl+C ou)
npm run kill
```

### Debug:
```bash
# Ver logs em tempo real
npm run logs:backend  # Terminal 1
npm run logs:frontend # Terminal 2

# Verificar status
npm run check

# Reiniciar se necessário
npm run restart
```

---

## Troubleshooting

### ❌ Erro "porta em uso"
```bash
npm run kill
npm run dev
```

### ❌ CORS error
```bash
# Verificar backend/.env
cat backend/.env | grep CORS

# Deve incluir: http://localhost:9091
```

### ❌ ModuleNotFoundError (Python)
```bash
npm run install:backend
```

### ❌ Dependências frontend
```bash
npm run install
```

---

## Atalhos

| Comando | Atalho |
|---------|--------|
| `npm run dev` | Iniciar tudo |
| `npm run kill` | Parar tudo |
| `npm run check` | Verificar backend |
| `Ctrl+C` | Parar dev (ambos) |

---

**Agora é só rodar `npm run dev` e começar a desenvolver! 🎉**
