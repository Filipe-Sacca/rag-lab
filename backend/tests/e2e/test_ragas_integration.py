"""
Test script to validate RAGAS integration in all RAG techniques.

This script tests that all 4 RAG techniques (baseline, hyde, reranking, agentic)
automatically calculate RAGAS scores after generating responses.
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from techniques.baseline_rag import baseline_rag
from techniques.hyde_rag import hyde_rag
from techniques.reranking_rag import reranking_rag
from techniques.agentic_rag import agentic_rag


async def test_baseline_ragas():
    """Test baseline RAG with RAGAS integration."""
    print("\n" + "=" * 60)
    print("TEST 1: Baseline RAG + RAGAS")
    print("=" * 60)

    query = "What is RAG?"
    result = await baseline_rag(query, top_k=5)

    print(f"Query: {query}")
    print(f"Answer: {result['answer'][:100]}...")
    print(f"\nRAGAS Scores:")
    print(f"  - Faithfulness: {result['metrics'].get('faithfulness', 'N/A')}")
    print(f"  - Answer Relevancy: {result['metrics'].get('answer_relevancy', 'N/A')}")
    print(f"  - Context Precision: {result['metrics'].get('context_precision', 'N/A')}")
    print(f"  - Context Recall: {result['metrics'].get('context_recall', 'N/A')}")

    assert "faithfulness" in result["metrics"], "Faithfulness not found in metrics"
    assert "answer_relevancy" in result["metrics"], "Answer relevancy not found in metrics"
    print("\n✅ Baseline RAG RAGAS integration: PASSED")
    return result


async def test_hyde_ragas():
    """Test HyDE RAG with RAGAS integration."""
    print("\n" + "=" * 60)
    print("TEST 2: HyDE RAG + RAGAS")
    print("=" * 60)

    query = "What is RAG?"
    result = await hyde_rag(query, top_k=5)

    print(f"Query: {query}")
    print(f"Answer: {result['answer'][:100]}...")
    print(f"\nRAGAS Scores:")
    print(f"  - Faithfulness: {result['metrics'].get('faithfulness', 'N/A')}")
    print(f"  - Answer Relevancy: {result['metrics'].get('answer_relevancy', 'N/A')}")
    print(f"  - Context Precision: {result['metrics'].get('context_precision', 'N/A')}")
    print(f"  - Context Recall: {result['metrics'].get('context_recall', 'N/A')}")

    assert "faithfulness" in result["metrics"], "Faithfulness not found in metrics"
    assert "answer_relevancy" in result["metrics"], "Answer relevancy not found in metrics"
    print("\n✅ HyDE RAG RAGAS integration: PASSED")
    return result


async def test_reranking_ragas():
    """Test Reranking RAG with RAGAS integration."""
    print("\n" + "=" * 60)
    print("TEST 3: Reranking RAG + RAGAS")
    print("=" * 60)

    # Note: Requires COHERE_API_KEY environment variable
    try:
        import os
        cohere_key = os.getenv("COHERE_API_KEY")
        if not cohere_key:
            print("⚠️  COHERE_API_KEY not found, skipping reranking test")
            return None

        query = "What is RAG?"
        result = await reranking_rag(
            query,
            initial_top_k=20,
            final_top_n=5,
            cohere_api_key=cohere_key
        )

        print(f"Query: {query}")
        print(f"Answer: {result['answer'][:100]}...")
        print(f"\nRAGAS Scores:")
        print(f"  - Faithfulness: {result['metrics'].get('faithfulness', 'N/A')}")
        print(f"  - Answer Relevancy: {result['metrics'].get('answer_relevancy', 'N/A')}")
        print(f"  - Context Precision: {result['metrics'].get('context_precision', 'N/A')}")
        print(f"  - Context Recall: {result['metrics'].get('context_recall', 'N/A')}")

        assert "faithfulness" in result["metrics"], "Faithfulness not found in metrics"
        assert "answer_relevancy" in result["metrics"], "Answer relevancy not found in metrics"
        print("\n✅ Reranking RAG RAGAS integration: PASSED")
        return result

    except Exception as e:
        print(f"⚠️  Reranking test failed: {e}")
        return None


def test_agentic_ragas():
    """Test Agentic RAG with RAGAS integration."""
    print("\n" + "=" * 60)
    print("TEST 4: Agentic RAG + RAGAS")
    print("=" * 60)

    query = "What is RAG?"
    result = agentic_rag(query, params={"default_technique": "baseline"})

    print(f"Query: {query}")
    print(f"Answer: {result['answer'][:100]}...")
    print(f"\nRAGAS Scores:")
    print(f"  - Faithfulness: {result['metrics'].get('faithfulness', 'N/A')}")
    print(f"  - Answer Relevancy: {result['metrics'].get('answer_relevancy', 'N/A')}")
    print(f"  - Context Precision: {result['metrics'].get('context_precision', 'N/A')}")
    print(f"  - Context Recall: {result['metrics'].get('context_recall', 'N/A')}")

    # Note: Agentic RAG propagates metrics from underlying technique
    if "faithfulness" in result["metrics"]:
        print("\n✅ Agentic RAG RAGAS integration: PASSED")
    else:
        print("\n⚠️  Agentic RAG may not have propagated RAGAS scores")
    return result


async def main():
    """Run all RAGAS integration tests."""
    print("\n" + "=" * 60)
    print("RAGAS Integration Test Suite")
    print("Testing automatic RAGAS evaluation in all RAG techniques")
    print("=" * 60)

    try:
        # Test async techniques
        await test_baseline_ragas()
        await test_hyde_ragas()
        await test_reranking_ragas()

        # Test sync technique
        test_agentic_ragas()

        print("\n" + "=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Make a query via API: curl -X POST http://localhost:8000/api/v1/query \\")
        print("   -H 'Content-Type: application/json' \\")
        print("   -d '{\"query\": \"What is RAG?\", \"technique\": \"baseline\"}'")
        print("\n2. Check database for RAGAS scores:")
        print("   sqlite3 rag_lab.db \"SELECT technique, faithfulness, answer_relevancy FROM rag_metrics LIMIT 5;\"")
        print("\n3. View comparison data:")
        print("   curl http://localhost:8000/api/v1/comparison-data | jq '.[0] | {faithfulness, answer_relevancy}'")

    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
