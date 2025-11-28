#!/usr/bin/env python3
"""
Test script for comparison endpoint.

Populates database with sample data and tests the /api/v1/comparison-data endpoint.
"""

import sys
from datetime import datetime

from sqlalchemy.orm import Session

from db import SessionLocal, init_db
from db.models import RAGExecution, RAGMetric


def create_sample_data(db: Session) -> None:
    """Create sample RAG execution data for testing."""

    # Sample data for different techniques
    sample_executions = [
        {
            "query": "What is RAG?",
            "answer": "RAG (Retrieval-Augmented Generation) combines information retrieval with text generation...",
            "technique": "baseline",
            "metrics": {
                "context_precision": 0.85,
                "context_recall": 0.82,
                "faithfulness": 0.91,
                "answer_relevancy": 0.88,
                "latency_ms": 245.3,
                "latency_seconds": 0.245,
                "chunks_retrieved": 5,
            }
        },
        {
            "query": "What is RAG?",
            "answer": "RAG is a technique that enhances language model outputs by retrieving relevant context...",
            "technique": "hyde",
            "metrics": {
                "context_precision": 0.78,
                "context_recall": 0.89,
                "faithfulness": 0.94,
                "answer_relevancy": 0.91,
                "latency_ms": 312.1,
                "latency_seconds": 0.312,
                "chunks_retrieved": 5,
            }
        },
        {
            "query": "What is RAG?",
            "answer": "RAG (Retrieval-Augmented Generation) is an AI framework combining retrieval systems...",
            "technique": "reranking",
            "metrics": {
                "context_precision": 0.92,
                "context_recall": 0.88,
                "faithfulness": 0.93,
                "answer_relevancy": 0.90,
                "latency_ms": 389.7,
                "latency_seconds": 0.390,
                "chunks_retrieved": 10,  # Retrieved more, then reranked
            }
        },
        {
            "query": "What is RAG?",
            "answer": "After analyzing the question, RAG is a methodology that augments generative models...",
            "technique": "agentic",
            "metrics": {
                "context_precision": 0.88,
                "context_recall": 0.91,
                "faithfulness": 0.96,
                "answer_relevancy": 0.93,
                "latency_ms": 512.4,
                "latency_seconds": 0.512,
                "chunks_retrieved": 7,
            }
        },
    ]

    for data in sample_executions:
        # Create execution
        execution = RAGExecution(
            query_text=data["query"],
            answer_text=data["answer"],
            technique_name=data["technique"],
            top_k=data["metrics"]["chunks_retrieved"],
            namespace="test",
            created_at=datetime.utcnow(),
        )
        db.add(execution)
        db.flush()  # Get execution.id

        # Create metrics
        metrics = RAGMetric(
            execution_id=execution.id,
            **data["metrics"]
        )
        db.add(metrics)

    db.commit()
    print(f"✅ Created {len(sample_executions)} sample executions")


def test_endpoint() -> None:
    """Test the comparison endpoint."""
    import requests

    try:
        response = requests.get("http://localhost:8000/api/v1/comparison-data")
        response.raise_for_status()

        data = response.json()
        print(f"\n✅ Endpoint working! Retrieved {len(data)} executions")
        print(f"\nSample response:")
        if data:
            import json
            print(json.dumps(data[0], indent=2))

    except Exception as e:
        print(f"❌ Error testing endpoint: {e}")
        sys.exit(1)


def main():
    """Main test function."""
    print("🧪 Testing RAG Lab Comparison Endpoint\n")

    # Initialize database
    print("Initializing database...")
    init_db()

    # Create sample data
    db = SessionLocal()
    try:
        create_sample_data(db)
    finally:
        db.close()

    # Test endpoint
    print("\nTesting /api/v1/comparison-data endpoint...")
    test_endpoint()

    print("\n✅ All tests passed!")


if __name__ == "__main__":
    main()
