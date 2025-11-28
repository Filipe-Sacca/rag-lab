#!/bin/bash
# Quick API test script

echo "🔍 Testing RAG Lab API..."
echo ""

# Check backend health
echo "1. Backend Health Check:"
curl -s http://localhost:8000/health | python3 -m json.tool
echo ""

# Check available techniques
echo "2. Available Techniques:"
curl -s http://localhost:8000/techniques | python3 -m json.tool | head -20
echo ""

# Quick test with baseline
echo "3. Quick Test (Baseline RAG):"
curl -s -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "O que é RAG?",
    "technique": "baseline",
    "top_k": 3,
    "namespace": null
  }' | python3 -m json.tool | head -30
echo ""

# Check database
echo "4. Database Check:"
cd backend && sqlite3 rag_lab.db "SELECT COUNT(*) as executions FROM rag_executions;" && cd ..
echo ""

echo "✅ API test complete!"
echo ""
echo "If all checks passed, you're ready to run:"
echo "  python run_tests.py"
echo "or"
echo "  Open http://localhost:9091 for manual testing"
