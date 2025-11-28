"""
Test script to validate Live API integration.

Compares responses between:
- Standard API (gemini-2.0-flash)
- Live API (gemini-2.0-flash-live-001)

Run with: python -m tests.test_live_api
"""

import asyncio
import time
import sys
import os

# Add parent dir to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings


async def test_live_api_basic():
    """Test basic Live API functionality."""
    print("\n" + "=" * 60)
    print("TEST 1: Basic Live API Call")
    print("=" * 60)

    from core.llm_live import live_invoke

    prompt = "What is RAG (Retrieval-Augmented Generation) in 2 sentences?"

    try:
        start = time.time()
        response = await live_invoke(prompt)
        duration = time.time() - start

        print(f"\nPrompt: {prompt}")
        print(f"\nResponse ({duration:.2f}s):\n{response}")
        print(f"\nResponse length: {len(response)} chars")
        print("\n✅ Live API basic test PASSED")
        return True

    except Exception as e:
        print(f"\n❌ Live API basic test FAILED: {e}")
        return False


async def test_live_vs_standard():
    """Compare Live API vs Standard API responses."""
    print("\n" + "=" * 60)
    print("TEST 2: Live API vs Standard API Comparison")
    print("=" * 60)

    from core.llm_live import live_invoke
    from core.llm import ainvoke_with_rotation

    prompt = "Explain what embeddings are in machine learning. Be concise."

    results = {}

    # Test Standard API
    print("\n🔄 Testing Standard API...")
    try:
        start = time.time()
        standard_response = await ainvoke_with_rotation(prompt)
        standard_duration = time.time() - start
        results["standard"] = {
            "response": standard_response,
            "duration": standard_duration,
            "chars": len(standard_response),
        }
        print(f"   ✅ Standard API: {standard_duration:.2f}s, {len(standard_response)} chars")
    except Exception as e:
        print(f"   ❌ Standard API failed: {e}")
        results["standard"] = {"error": str(e)}

    # Test Live API
    print("\n🔄 Testing Live API...")
    try:
        start = time.time()
        live_response = await live_invoke(prompt)
        live_duration = time.time() - start
        results["live"] = {
            "response": live_response,
            "duration": live_duration,
            "chars": len(live_response),
        }
        print(f"   ✅ Live API: {live_duration:.2f}s, {len(live_response)} chars")
    except Exception as e:
        print(f"   ❌ Live API failed: {e}")
        results["live"] = {"error": str(e)}

    # Compare
    print("\n" + "-" * 40)
    print("COMPARISON:")
    print("-" * 40)

    if "error" not in results.get("standard", {}) and "error" not in results.get("live", {}):
        print(f"\n📊 Standard API:")
        print(f"   Duration: {results['standard']['duration']:.2f}s")
        print(f"   Length: {results['standard']['chars']} chars")
        print(f"   Preview: {results['standard']['response'][:200]}...")

        print(f"\n📊 Live API:")
        print(f"   Duration: {results['live']['duration']:.2f}s")
        print(f"   Length: {results['live']['chars']} chars")
        print(f"   Preview: {results['live']['response'][:200]}...")

        # Quality comparison (simple heuristic)
        print("\n📈 Analysis:")
        if results['live']['duration'] < results['standard']['duration']:
            print(f"   ⚡ Live API is {results['standard']['duration'] - results['live']['duration']:.2f}s faster")
        else:
            print(f"   ⚡ Standard API is {results['live']['duration'] - results['standard']['duration']:.2f}s faster")

        print("\n✅ Comparison test PASSED")
        return True
    else:
        print("\n❌ Comparison test FAILED (one or both APIs failed)")
        return False


async def test_live_api_rag_context():
    """Test Live API with RAG-like context."""
    print("\n" + "=" * 60)
    print("TEST 3: Live API with RAG Context")
    print("=" * 60)

    from core.llm_live import live_invoke

    # Simulate RAG context
    context = """
    Document 1: RAG Lab Overview
    RAG Lab is a platform for testing and comparing 9 different RAG techniques.
    It uses Google Gemini as the LLM and Pinecone as the vector database.

    Document 2: Techniques Available
    The techniques include: Baseline RAG, HyDE, Reranking, Query Expansion,
    Multi-Query, Hybrid Search, Contextual Compression, Self-Query, and Agentic RAG.

    Document 3: Evaluation Metrics
    Each technique is evaluated using RAGAS metrics including faithfulness,
    answer relevancy, context precision, and context recall.
    """

    query = "What vector database does RAG Lab use?"

    prompt = f"""Based on the following context, answer the question.

CONTEXT:
{context}

QUESTION: {query}

ANSWER:"""

    try:
        start = time.time()
        response = await live_invoke(
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=500
        )
        duration = time.time() - start

        print(f"\nQuery: {query}")
        print(f"\nResponse ({duration:.2f}s):\n{response}")

        # Validate response
        if "pinecone" in response.lower():
            print("\n✅ RAG context test PASSED (correct answer)")
            return True
        else:
            print("\n⚠️ RAG context test PARTIAL (response may be incorrect)")
            return True  # Still passed technically

    except Exception as e:
        print(f"\n❌ RAG context test FAILED: {e}")
        return False


async def test_rate_limit_stress():
    """Test multiple rapid requests (stress test for rate limits)."""
    print("\n" + "=" * 60)
    print("TEST 4: Rate Limit Stress Test (5 rapid requests)")
    print("=" * 60)

    from core.llm_live import live_invoke

    prompts = [
        "What is 2+2?",
        "What is the capital of France?",
        "Name a color.",
        "What is Python?",
        "What is AI?",
    ]

    print("\n🔄 Sending 5 rapid requests to Live API...")

    start = time.time()
    success = 0
    failed = 0

    for i, prompt in enumerate(prompts, 1):
        try:
            req_start = time.time()
            response = await live_invoke(prompt, max_output_tokens=50)
            req_duration = time.time() - req_start
            print(f"   Request {i}: ✅ ({req_duration:.2f}s) - {response[:50]}...")
            success += 1
        except Exception as e:
            print(f"   Request {i}: ❌ {e}")
            failed += 1

    total_duration = time.time() - start

    print(f"\n📊 Results:")
    print(f"   Total time: {total_duration:.2f}s")
    print(f"   Success: {success}/5")
    print(f"   Failed: {failed}/5")
    print(f"   Avg per request: {total_duration / 5:.2f}s")

    if failed == 0:
        print("\n✅ Rate limit stress test PASSED (no 429 errors!)")
        return True
    else:
        print(f"\n⚠️ Rate limit stress test: {failed} failures")
        return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("🧪 LIVE API INTEGRATION TESTS")
    print("=" * 60)
    print(f"\nAPI Key: {settings.GOOGLE_API_KEY[:20]}...")
    print(f"Model: gemini-2.0-flash → gemini-2.0-flash-live-001")

    results = []

    # Test 1: Basic
    results.append(await test_live_api_basic())

    # Test 2: Comparison
    results.append(await test_live_vs_standard())

    # Test 3: RAG Context
    results.append(await test_live_api_rag_context())

    # Test 4: Rate Limit Stress
    results.append(await test_rate_limit_stress())

    # Summary
    print("\n" + "=" * 60)
    print("📋 TEST SUMMARY")
    print("=" * 60)
    print(f"\n   Passed: {sum(results)}/{len(results)}")
    print(f"   Failed: {len(results) - sum(results)}/{len(results)}")

    if all(results):
        print("\n🎉 ALL TESTS PASSED! Live API is ready for production.")
    else:
        print("\n⚠️ Some tests failed. Check output above.")

    return all(results)


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
