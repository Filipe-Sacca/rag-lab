#!/usr/bin/env python3
"""
Automated RAG test runner
Usage: python run_tests.py [--technique TECHNIQUE]
"""

import requests
import time
import argparse
from typing import List, Dict, Any

# Test questions
QUESTIONS = [
    "O que é RAG (Retrieval Augmented Generation)?",
    "Por que RAG é mais confiável que usar apenas LLMs puros sem contexto?",
    "Quais são os 3 componentes principais de um sistema RAG e suas funções específicas?",
    "Compare embeddings com keyword search: vantagens e desvantagens de cada abordagem",
    "Como melhorar a qualidade de um sistema RAG?",
    "Qual a relação entre chunk size, embeddings e qualidade do retrieval?",
    "Como funciona o processo de chunking em RAG e quais são os parâmetros importantes?",
    "Explique o pipeline completo de RAG desde o upload do documento até a geração da resposta, incluindo todos os componentes e suas interações",
    "Quais são os trade-offs entre latência, custo e qualidade em diferentes técnicas RAG?",
    "Quando usar baseline RAG vs HyDE vs reranking? Dê exemplos de casos de uso para cada"
]

# All techniques
TECHNIQUES = [
    "baseline",
    "hyde",
    "reranking",
    "agentic",
    "fusion",
    "subquery",
    "graph",
    "adaptive"
]

API_URL = "http://localhost:8000/query"

def run_test(question: str, technique: str, top_k: int = 5) -> Dict[str, Any]:
    """Run a single test"""
    payload = {
        "query": question,
        "technique": technique,
        "top_k": top_k,
        "namespace": None
    }

    try:
        start = time.time()
        response = requests.post(API_URL, json=payload, timeout=60)
        elapsed = (time.time() - start) * 1000

        if response.status_code == 200:
            data = response.json()
            return {
                "success": True,
                "latency_ms": elapsed,
                "answer": data.get("answer", ""),
                "metrics": data.get("metrics", {}),
                "metadata": data.get("metadata", {})
            }
        else:
            return {
                "success": False,
                "error": f"HTTP {response.status_code}: {response.text}"
            }
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def run_all_tests(techniques: List[str] = None, delay: float = 1.0):
    """Run all tests for specified techniques"""
    if techniques is None:
        techniques = TECHNIQUES

    total_tests = len(QUESTIONS) * len(techniques)
    current = 0

    print("🧪 Starting RAG Tests")
    print("=" * 60)
    print(f"Questions: {len(QUESTIONS)}")
    print(f"Techniques: {', '.join(techniques)}")
    print(f"Total tests: {total_tests}")
    print(f"Delay between tests: {delay}s")
    print("=" * 60)
    print()

    results = []

    for q_idx, question in enumerate(QUESTIONS, 1):
        print(f"\n📝 Question {q_idx}/{len(QUESTIONS)}:")
        print(f"   {question[:80]}{'...' if len(question) > 80 else ''}")
        print()

        for tech in techniques:
            current += 1
            progress = (current / total_tests) * 100

            print(f"   [{current}/{total_tests}] ({progress:.1f}%) Testing {tech:12}... ", end="", flush=True)

            result = run_test(question, tech)

            if result["success"]:
                latency = result["latency_ms"]
                num_sources = result["metadata"].get("num_docs_retrieved", 0)
                print(f"✅ {latency:6.0f}ms | {num_sources} sources")

                results.append({
                    "question": question,
                    "question_num": q_idx,
                    "technique": tech,
                    "success": True,
                    "latency_ms": latency,
                    "num_sources": num_sources
                })
            else:
                print(f"❌ {result['error']}")
                results.append({
                    "question": question,
                    "question_num": q_idx,
                    "technique": tech,
                    "success": False,
                    "error": result['error']
                })

            # Delay between tests
            if delay > 0 and current < total_tests:
                time.sleep(delay)

    return results

def print_summary(results: List[Dict[str, Any]]):
    """Print test summary"""
    from collections import defaultdict

    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)

    # Overall stats
    total = len(results)
    successes = sum(1 for r in results if r["success"])
    failures = total - successes

    print(f"\n✅ Successful: {successes}/{total} ({(successes/total)*100:.1f}%)")
    print(f"❌ Failed: {failures}/{total} ({(failures/total)*100:.1f}%)")

    # By technique
    by_technique = defaultdict(list)
    for r in results:
        if r["success"]:
            by_technique[r["technique"]].append(r["latency_ms"])

    print("\n⏱️  Average Latency by Technique:")
    print("-" * 60)
    for tech, latencies in sorted(by_technique.items(), key=lambda x: sum(x[1])/len(x[1])):
        avg = sum(latencies) / len(latencies)
        min_lat = min(latencies)
        max_lat = max(latencies)
        print(f"{tech:12} | {avg:7.0f}ms (min: {min_lat:6.0f}ms, max: {max_lat:6.0f}ms)")
    print("-" * 60)

    # Failed tests
    if failures > 0:
        print("\n❌ Failed Tests:")
        print("-" * 60)
        for r in results:
            if not r["success"]:
                print(f"Q{r['question_num']} | {r['technique']:12} | {r['error']}")
        print("-" * 60)

def main():
    parser = argparse.ArgumentParser(description="Run RAG tests")
    parser.add_argument(
        "--technique",
        "-t",
        choices=TECHNIQUES,
        help="Test only specific technique (default: all)"
    )
    parser.add_argument(
        "--delay",
        "-d",
        type=float,
        default=1.0,
        help="Delay between tests in seconds (default: 1.0)"
    )
    parser.add_argument(
        "--question",
        "-q",
        type=int,
        help="Test only specific question number (1-10)"
    )

    args = parser.parse_args()

    # Determine techniques to test
    techniques = [args.technique] if args.technique else TECHNIQUES

    # Determine questions to test
    if args.question:
        if 1 <= args.question <= len(QUESTIONS):
            questions_to_test = [QUESTIONS[args.question - 1]]
        else:
            print(f"❌ Invalid question number. Must be 1-{len(QUESTIONS)}")
            return
    else:
        questions_to_test = QUESTIONS

    # Override QUESTIONS global for the test
    global QUESTIONS
    original_questions = QUESTIONS
    QUESTIONS = questions_to_test

    try:
        # Run tests
        results = run_all_tests(techniques=techniques, delay=args.delay)

        # Print summary
        print_summary(results)

        # Export suggestion
        print("\n📝 Next Steps:")
        print("1. Review results in database")
        print("2. Run: python export_results.py")
        print("3. Analyze exported CSV")

    finally:
        QUESTIONS = original_questions

if __name__ == "__main__":
    main()
