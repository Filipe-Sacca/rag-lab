#!/bin/bash

echo "🔍 Verifying RAG Lab Frontend Setup..."
echo ""

# Check Node.js
echo "📦 Checking Node.js..."
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js installed: $NODE_VERSION"
else
    echo "❌ Node.js not found. Please install Node.js 18+"
    exit 1
fi

# Check npm
echo "📦 Checking npm..."
if command -v npm &> /dev/null; then
    NPM_VERSION=$(npm --version)
    echo "✅ npm installed: $NPM_VERSION"
else
    echo "❌ npm not found"
    exit 1
fi

# Check node_modules
echo ""
echo "📚 Checking dependencies..."
if [ -d "node_modules" ]; then
    echo "✅ node_modules exists"
    PACKAGE_COUNT=$(ls node_modules | wc -l)
    echo "   $PACKAGE_COUNT packages installed"
else
    echo "⚠️  node_modules not found. Run: npm install"
fi

# Check source files
echo ""
echo "📄 Checking source files..."
FILES=(
    "src/App.tsx"
    "src/main.tsx"
    "src/index.css"
    "src/api/client.ts"
    "src/api/rag.service.ts"
    "src/types/rag.types.ts"
    "src/components/TechniqueSelector.tsx"
    "src/components/QueryInput.tsx"
    "src/components/ResponseDisplay.tsx"
    "src/components/MetricsCard.tsx"
    "src/components/SourcesList.tsx"
    "src/components/RAGASChart.tsx"
)

MISSING=0
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "❌ $file (missing)"
        MISSING=$((MISSING + 1))
    fi
done

# Check config files
echo ""
echo "⚙️  Checking configuration files..."
CONFIGS=(
    "package.json"
    "tsconfig.json"
    "vite.config.ts"
    "tailwind.config.js"
    ".env"
)

for config in "${CONFIGS[@]}"; do
    if [ -f "$config" ]; then
        echo "✅ $config"
    else
        echo "❌ $config (missing)"
        MISSING=$((MISSING + 1))
    fi
done

# Test build
echo ""
echo "🔨 Testing TypeScript compilation..."
if npm run build &> /dev/null; then
    echo "✅ Build successful"
else
    echo "❌ Build failed. Run: npm run build"
    MISSING=$((MISSING + 1))
fi

# Check backend
echo ""
echo "🌐 Checking backend connection..."
if curl -s http://localhost:8000/api/health &> /dev/null; then
    echo "✅ Backend is online at http://localhost:8000"
else
    echo "⚠️  Backend is offline. Make sure to start the backend server."
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
if [ $MISSING -eq 0 ]; then
    echo "✅ All checks passed! You're ready to start."
    echo ""
    echo "To run the application:"
    echo "  npm run dev"
    echo "  or"
    echo "  ./start.sh"
    echo ""
    echo "Then open: http://localhost:5173"
else
    echo "⚠️  Some issues found. Please fix them before starting."
fi
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
