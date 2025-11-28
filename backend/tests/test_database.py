"""
Unit tests for database persistence layer.

Tests SQLAlchemy models, CRUD operations, and database initialization.
"""

import pytest
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.models import Base, RAGExecution, RAGMetric
from db.crud import (
    create_execution,
    get_execution,
    get_executions,
    get_executions_by_technique,
    get_recent_executions,
    get_technique_statistics,
    delete_old_executions,
)
from db.database import init_db, drop_all_tables


# Test database setup (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def test_db():
    """Create a fresh test database for each test"""
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)

    # Create session
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestSessionLocal()

    yield db

    # Cleanup
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_execution_data():
    """Sample execution data for testing"""
    return {
        "query": "What is Python?",
        "answer": "Python is a high-level programming language...",
        "technique": "baseline",
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
        "top_k": 5,
    }


class TestDatabaseModels:
    """Test SQLAlchemy models"""

    def test_create_rag_execution(self, test_db, sample_execution_data):
        """Test creating RAGExecution record"""
        execution = create_execution(test_db, **sample_execution_data)

        assert execution.id is not None
        assert execution.query_text == "What is Python?"
        assert execution.technique_name == "baseline"
        assert execution.top_k == 5
        assert len(execution.sources) == 2
        assert execution.created_at is not None

    def test_create_rag_metric(self, test_db, sample_execution_data):
        """Test creating RAGMetric record with execution"""
        execution = create_execution(test_db, **sample_execution_data)

        assert execution.metrics is not None
        assert execution.metrics.latency_ms == 850.5
        assert execution.metrics.tokens_total == 1550
        assert execution.metrics.cost_total_usd == 0.00004875
        assert execution.metrics.chunks_retrieved == 2

    def test_execution_to_dict(self, test_db, sample_execution_data):
        """Test execution to_dict() method"""
        execution = create_execution(test_db, **sample_execution_data)
        data = execution.to_dict()

        assert data["id"] == execution.id
        assert data["query"] == "What is Python?"
        assert data["technique"] == "baseline"
        assert data["metrics"] is not None
        assert data["metrics"]["latency_ms"] == 850.5


class TestCRUDOperations:
    """Test CRUD operations"""

    def test_get_execution_by_id(self, test_db, sample_execution_data):
        """Test retrieving execution by ID"""
        created = create_execution(test_db, **sample_execution_data)
        retrieved = get_execution(test_db, created.id)

        assert retrieved is not None
        assert retrieved.id == created.id
        assert retrieved.query_text == created.query_text

    def test_get_execution_not_found(self, test_db):
        """Test retrieving non-existent execution"""
        retrieved = get_execution(test_db, 99999)
        assert retrieved is None

    def test_get_executions_pagination(self, test_db, sample_execution_data):
        """Test pagination in get_executions"""
        # Create 10 executions
        for i in range(10):
            data = sample_execution_data.copy()
            data["query"] = f"Query {i}"
            create_execution(test_db, **data)

        # Test pagination
        page1 = get_executions(test_db, skip=0, limit=5)
        page2 = get_executions(test_db, skip=5, limit=5)

        assert len(page1) == 5
        assert len(page2) == 5
        assert page1[0].id != page2[0].id

    def test_get_executions_by_technique(self, test_db, sample_execution_data):
        """Test filtering executions by technique"""
        # Create baseline executions
        for i in range(3):
            data = sample_execution_data.copy()
            data["query"] = f"Baseline query {i}"
            data["technique"] = "baseline"
            create_execution(test_db, **data)

        # Create hyde executions
        for i in range(2):
            data = sample_execution_data.copy()
            data["query"] = f"HyDE query {i}"
            data["technique"] = "hyde"
            create_execution(test_db, **data)

        baseline = get_executions_by_technique(test_db, "baseline")
        hyde = get_executions_by_technique(test_db, "hyde")

        assert len(baseline) == 3
        assert len(hyde) == 2
        assert all(e.technique_name == "baseline" for e in baseline)
        assert all(e.technique_name == "hyde" for e in hyde)

    def test_get_recent_executions(self, test_db, sample_execution_data):
        """Test retrieving recent executions"""
        # Create some executions
        for i in range(5):
            data = sample_execution_data.copy()
            data["query"] = f"Query {i}"
            create_execution(test_db, **data)

        # Get recent (default 24 hours)
        recent = get_recent_executions(test_db, hours=24)

        assert len(recent) == 5
        # All should be within last 24 hours
        cutoff = datetime.utcnow() - timedelta(hours=24)
        assert all(e.created_at > cutoff for e in recent)


class TestStatistics:
    """Test statistics and aggregation"""

    def test_technique_statistics_single(self, test_db, sample_execution_data):
        """Test statistics for single technique"""
        # Create baseline executions with different metrics
        for i in range(3):
            data = sample_execution_data.copy()
            data["query"] = f"Query {i}"
            data["technique"] = "baseline"
            data["metrics"]["latency_ms"] = 800 + (i * 100)  # 800, 900, 1000
            create_execution(test_db, **data)

        stats = get_technique_statistics(test_db, technique="baseline", days=30)

        assert stats["technique"] == "baseline"
        assert stats["total_executions"] == 3
        assert stats["latency"]["avg_ms"] == 900.0  # Average of 800, 900, 1000
        assert stats["latency"]["min_ms"] == 800.0
        assert stats["latency"]["max_ms"] == 1000.0

    def test_technique_statistics_all(self, test_db, sample_execution_data):
        """Test statistics for all techniques"""
        # Create executions for multiple techniques
        techniques = ["baseline", "hyde", "reranking"]

        for technique in techniques:
            for i in range(2):
                data = sample_execution_data.copy()
                data["query"] = f"{technique} query {i}"
                data["technique"] = technique
                create_execution(test_db, **data)

        stats = get_technique_statistics(test_db, technique=None, days=30)

        assert "techniques" in stats
        assert len(stats["techniques"]) == 3
        assert stats["total_techniques"] == 3

        for technique in techniques:
            assert technique in stats["techniques"]
            assert stats["techniques"][technique]["total_executions"] == 2

    def test_statistics_no_data(self, test_db):
        """Test statistics with no data"""
        stats = get_technique_statistics(test_db, technique="baseline", days=30)

        assert stats["technique"] == "baseline"
        assert stats["total_executions"] == 0
        assert "message" in stats


class TestDatabaseMaintenance:
    """Test database maintenance operations"""

    def test_delete_old_executions(self, test_db, sample_execution_data):
        """Test deleting old executions"""
        # Create some executions
        for i in range(5):
            data = sample_execution_data.copy()
            data["query"] = f"Query {i}"
            execution = create_execution(test_db, **data)

            # Manually set old created_at for some executions
            if i < 2:
                execution.created_at = datetime.utcnow() - timedelta(days=100)
                test_db.commit()

        # Delete executions older than 90 days
        deleted = delete_old_executions(test_db, days=90)

        assert deleted == 2  # Should delete 2 old executions

        # Verify remaining executions
        remaining = get_executions(test_db, limit=100)
        assert len(remaining) == 3


class TestJSONFields:
    """Test JSON field storage and retrieval"""

    def test_sources_json_field(self, test_db, sample_execution_data):
        """Test storing and retrieving sources as JSON"""
        execution = create_execution(test_db, **sample_execution_data)

        assert isinstance(execution.sources, list)
        assert len(execution.sources) == 2
        assert execution.sources[0]["content"] == "Python is a programming language..."
        assert execution.sources[0]["score"] == 0.92

    def test_execution_details_json_field(self, test_db, sample_execution_data):
        """Test storing and retrieving execution details as JSON"""
        execution = create_execution(test_db, **sample_execution_data)

        assert isinstance(execution.execution_details, dict)
        assert "steps" in execution.execution_details
        assert len(execution.execution_details["steps"]) == 3
        assert execution.execution_details["steps"][0]["step"] == "embed_query"

    def test_metadata_json_field(self, test_db, sample_execution_data):
        """Test storing and retrieving metadata as JSON"""
        sample_execution_data["metadata"] = {
            "user_id": "user123",
            "session_id": "session456",
            "custom_field": "custom_value",
        }

        execution = create_execution(test_db, **sample_execution_data)

        assert isinstance(execution.metadata, dict)
        assert execution.metadata["user_id"] == "user123"
        assert execution.metadata["session_id"] == "session456"


class TestRelationships:
    """Test SQLAlchemy relationships"""

    def test_execution_metrics_relationship(self, test_db, sample_execution_data):
        """Test one-to-one relationship between execution and metrics"""
        execution = create_execution(test_db, **sample_execution_data)

        # Access metrics through relationship
        assert execution.metrics is not None
        assert execution.metrics.execution_id == execution.id
        assert execution.metrics.execution == execution

    def test_cascade_delete(self, test_db, sample_execution_data):
        """Test cascade delete: deleting execution deletes metrics"""
        execution = create_execution(test_db, **sample_execution_data)
        metric_id = execution.metrics.id

        # Delete execution
        test_db.delete(execution)
        test_db.commit()

        # Verify metric was also deleted
        metric = test_db.query(RAGMetric).filter(RAGMetric.id == metric_id).first()
        assert metric is None


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
