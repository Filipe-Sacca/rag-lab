"""
Database Usage Examples for RAG Lab

Demonstrates how to use the SQLAlchemy persistence layer
for storing and querying RAG execution results.
"""

import asyncio
from datetime import datetime, timedelta

from db import (
    SessionLocal,
    init_db,
    create_execution,
    get_execution,
    get_executions,
    get_executions_by_technique,
    get_recent_executions,
    get_technique_statistics,
)
from techniques.baseline_rag import baseline_rag


def example_1_basic_persistence():
    """Example 1: Basic execution persistence"""
    print("\n=== Example 1: Basic Persistence ===\n")

    # Initialize database
    init_db()

    # Create a session
    db = SessionLocal()

    try:
        # Simulate a RAG execution result
        mock_result = {
            "query": "What is Python?",
            "answer": "Python is a high-level programming language...",
            "sources": [
                {
                    "content": "Python is a programming language...",
                    "metadata": {"source": "doc1.pdf"},
                    "score": 0.92,
                },
                {
                    "content": "Python was created by Guido van Rossum...",
                    "metadata": {"source": "doc2.pdf"},
                    "score": 0.87,
                },
            ],
            "metrics": {
                "latency_ms": 850.5,
                "latency_seconds": 0.85,
                "tokens": {"input": 1200, "output": 350, "total": 1550},
                "cost": {
                    "input_usd": 0.0000225,
                    "output_usd": 0.00002625,
                    "total_usd": 0.00004875,
                },
                "chunks_retrieved": 2,
            },
            "execution_details": {
                "technique": "baseline_rag",
                "steps": [
                    {"step": "embed_query", "duration_ms": 150},
                    {"step": "similarity_search", "duration_ms": 200},
                    {"step": "llm_generation", "duration_ms": 500},
                ],
            },
        }

        # Save to database
        execution = create_execution(
            db,
            query=mock_result["query"],
            answer=mock_result["answer"],
            technique="baseline",
            sources=mock_result["sources"],
            metrics=mock_result["metrics"],
            execution_details=mock_result["execution_details"],
            top_k=5,
        )

        print(f"✅ Saved execution ID: {execution.id}")
        print(f"   Query: {execution.query_text}")
        print(f"   Technique: {execution.technique_name}")
        print(f"   Latency: {execution.metrics.latency_ms}ms")
        print(f"   Cost: ${execution.metrics.cost_total_usd:.6f}")

    finally:
        db.close()


def example_2_retrieve_executions():
    """Example 2: Retrieve executions with filtering"""
    print("\n=== Example 2: Retrieve Executions ===\n")

    db = SessionLocal()

    try:
        # Get all executions (limit 10)
        all_executions = get_executions(db, limit=10)
        print(f"📊 Total executions: {len(all_executions)}")

        # Get baseline executions only
        baseline_executions = get_executions_by_technique(db, "baseline", limit=10)
        print(f"🎯 Baseline executions: {len(baseline_executions)}")

        # Get recent executions (last 24 hours)
        recent = get_recent_executions(db, hours=24, limit=10)
        print(f"⏰ Recent executions (24h): {len(recent)}")

        # Display first execution
        if all_executions:
            exec = all_executions[0]
            print(f"\n📄 Latest execution:")
            print(f"   ID: {exec.id}")
            print(f"   Query: {exec.query_text[:50]}...")
            print(f"   Technique: {exec.technique_name}")
            print(f"   Latency: {exec.metrics.latency_ms}ms")
            print(f"   Created: {exec.created_at}")

    finally:
        db.close()


def example_3_statistics():
    """Example 3: Get aggregated statistics"""
    print("\n=== Example 3: Statistics & Analytics ===\n")

    db = SessionLocal()

    try:
        # Get statistics for all techniques (last 30 days)
        all_stats = get_technique_statistics(db, technique=None, days=30)

        if "techniques" in all_stats:
            print(f"📈 Statistics for last 30 days:\n")
            for technique, stats in all_stats["techniques"].items():
                print(f"   {technique.upper()}:")
                print(f"      Executions: {stats['total_executions']}")
                print(f"      Avg Latency: {stats['latency']['avg_ms']}ms")
                print(f"      Total Cost: ${stats['cost']['total_usd']:.6f}")
                print()

        # Get statistics for specific technique
        baseline_stats = get_technique_statistics(db, technique="baseline", days=7)
        if baseline_stats.get("total_executions", 0) > 0:
            print(f"\n🎯 Baseline RAG (last 7 days):")
            print(f"   Executions: {baseline_stats['total_executions']}")
            print(f"   Avg Latency: {baseline_stats['latency']['avg_ms']}ms")
            print(f"   Min Latency: {baseline_stats['latency']['min_ms']}ms")
            print(f"   Max Latency: {baseline_stats['latency']['max_ms']}ms")
            print(f"   Avg Cost: ${baseline_stats['cost']['avg_usd']:.6f}")

    finally:
        db.close()


async def example_4_real_execution():
    """Example 4: Execute real RAG query and persist"""
    print("\n=== Example 4: Real RAG Execution + Persistence ===\n")

    db = SessionLocal()

    try:
        # Execute real baseline RAG (requires Pinecone + Gemini setup)
        query = "What is RAG?"

        print(f"🔍 Executing query: '{query}'")
        print("   Technique: Baseline RAG")

        # This will fail if Pinecone/Gemini not configured
        # Uncomment to test with real setup:
        # result = await baseline_rag(query, top_k=3)
        #
        # execution = create_execution(
        #     db,
        #     query=result["query"],
        #     answer=result["answer"],
        #     technique="baseline",
        #     sources=result["sources"],
        #     metrics=result["metrics"],
        #     execution_details=result["execution_details"],
        #     top_k=3,
        # )
        #
        # print(f"✅ Execution saved with ID: {execution.id}")
        # print(f"   Answer: {result['answer'][:100]}...")

        print("   ⚠️  Skipped (requires Pinecone + Gemini configuration)")

    finally:
        db.close()


def example_5_advanced_queries():
    """Example 5: Advanced database queries"""
    print("\n=== Example 5: Advanced Queries ===\n")

    db = SessionLocal()

    try:
        # Get executions from last 7 days
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_executions = get_executions(
            db, start_date=seven_days_ago, limit=100
        )
        print(f"📅 Executions (last 7 days): {len(recent_executions)}")

        # Get specific execution by ID
        if recent_executions:
            exec_id = recent_executions[0].id
            execution = get_execution(db, exec_id)

            print(f"\n📄 Execution #{exec_id} details:")
            print(f"   Query: {execution.query_text}")
            print(f"   Answer length: {len(execution.answer_text)} chars")
            print(f"   Sources: {len(execution.sources)} chunks")
            print(f"   Metrics:")
            print(f"      Latency: {execution.metrics.latency_ms}ms")
            print(f"      Tokens: {execution.metrics.tokens_total}")
            print(f"      Cost: ${execution.metrics.cost_total_usd:.6f}")

            # Display execution steps
            if execution.execution_details and "steps" in execution.execution_details:
                print(f"   Steps:")
                for step in execution.execution_details["steps"]:
                    print(f"      - {step.get('step')}: {step.get('duration_ms')}ms")

    finally:
        db.close()


def run_all_examples():
    """Run all examples sequentially"""
    print("\n" + "=" * 60)
    print("  RAG Lab - Database Usage Examples")
    print("=" * 60)

    # Run examples
    example_1_basic_persistence()
    example_2_retrieve_executions()
    example_3_statistics()
    # example_4_real_execution()  # Async example
    example_5_advanced_queries()

    print("\n" + "=" * 60)
    print("  All examples completed!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    run_all_examples()

    # Run async example separately
    # asyncio.run(example_4_real_execution())
