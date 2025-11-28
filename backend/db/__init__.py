"""
Database package for RAG Lab.

Provides SQLAlchemy ORM models and database session management
for persisting RAG execution results and metrics.
"""

from .database import get_db, init_db, SessionLocal, engine, check_database_health
from .models import RAGExecution, RAGMetric
from .crud import (
    create_execution,
    get_execution,
    get_executions,
    get_executions_by_technique,
    get_technique_statistics,
    get_recent_executions,
)

__all__ = [
    # Database
    "get_db",
    "init_db",
    "SessionLocal",
    "engine",
    "check_database_health",
    # Models
    "RAGExecution",
    "RAGMetric",
    # CRUD
    "create_execution",
    "get_execution",
    "get_executions",
    "get_executions_by_technique",
    "get_technique_statistics",
    "get_recent_executions",
]
