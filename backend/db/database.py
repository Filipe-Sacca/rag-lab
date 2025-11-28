"""
Database session management and initialization.

Handles SQLite database connection, session lifecycle,
and database initialization/migration.
"""

import os
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session

from .models import Base

# Database file path (relative to backend directory)
DB_DIR = Path(__file__).parent.parent
DB_PATH = DB_DIR / "rag_lab.db"
DATABASE_URL = f"sqlite:///{DB_PATH}"

# SQLAlchemy engine with optimizations
engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False,  # Allow multi-threading
        "timeout": 30,  # Connection timeout in seconds
    },
    echo=False,  # Set to True for SQL query logging
    pool_pre_ping=True,  # Verify connections before using
    future=True,  # Use SQLAlchemy 2.0 style
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    future=True,  # SQLAlchemy 2.0 style
)


# SQLite optimization: Enable foreign keys
@event.listens_for(Engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    """
    Enable SQLite optimizations on connection.

    - Foreign key constraints
    - Write-Ahead Logging (WAL) mode for better concurrency
    - Synchronous mode for better performance
    """
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA cache_size=-64000")  # 64MB cache
    cursor.execute("PRAGMA temp_store=MEMORY")
    cursor.close()


def init_db() -> None:
    """
    Initialize database: create all tables if they don't exist.

    This function is idempotent - safe to call multiple times.
    Uses SQLAlchemy's declarative base metadata to create tables.

    Should be called:
    - On application startup
    - Before running tests
    - During deployment/migration

    Example:
        >>> from db import init_db
        >>> init_db()
        Database initialized: /path/to/rag_lab.db
    """
    # Create database directory if it doesn't exist
    DB_DIR.mkdir(parents=True, exist_ok=True)

    # Create all tables
    Base.metadata.create_all(bind=engine)

    print(f"Database initialized: {DB_PATH}")
    print(f"Tables created: {', '.join(Base.metadata.tables.keys())}")


def get_db() -> Generator[Session, None, None]:
    """
    Database session dependency for FastAPI.

    Yields a SQLAlchemy session and ensures proper cleanup.
    Use with FastAPI's Depends() for automatic session management.

    Example:
        @router.post("/query")
        async def query_rag(
            request: QueryRequest,
            db: Session = Depends(get_db)
        ):
            execution = create_execution(db, result)
            return execution

    Yields:
        Session: SQLAlchemy database session

    Ensures:
        - Session is always closed after use
        - Transactions are committed or rolled back properly
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def drop_all_tables() -> None:
    """
    Drop all database tables.

    WARNING: This will delete ALL data!
    Use only for testing or database reset.

    Example:
        >>> from db import drop_all_tables, init_db
        >>> drop_all_tables()  # Delete all data
        >>> init_db()  # Recreate tables
    """
    Base.metadata.drop_all(bind=engine)
    print(f"All tables dropped from: {DB_PATH}")


def reset_database() -> None:
    """
    Complete database reset: drop and recreate all tables.

    WARNING: This will delete ALL data!
    Use only for testing or complete database reset.

    Example:
        >>> from db import reset_database
        >>> reset_database()
        All tables dropped from: /path/to/rag_lab.db
        Database initialized: /path/to/rag_lab.db
        Tables created: rag_executions, rag_metrics
    """
    drop_all_tables()
    init_db()


# Database health check
def check_database_health() -> dict:
    """
    Check database connectivity and basic health.

    Returns:
        dict: Health status information

    Example:
        >>> health = check_database_health()
        >>> print(health)
        {'status': 'healthy', 'database': 'rag_lab.db', 'tables': 2}
    """
    try:
        with SessionLocal() as db:
            # Simple query to test connectivity
            db.execute("SELECT 1")

        return {
            "status": "healthy",
            "database": str(DB_PATH),
            "exists": DB_PATH.exists(),
            "tables": len(Base.metadata.tables),
            "table_names": list(Base.metadata.tables.keys()),
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "database": str(DB_PATH),
        }
