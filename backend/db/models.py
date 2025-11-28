"""
SQLAlchemy ORM Models for RAG Lab.

Defines database schema for storing RAG execution results,
metrics, and performance data.
"""

from datetime import datetime
from typing import Dict, Any

from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    DateTime,
    Text,
    Index,
    ForeignKey,
)
from sqlalchemy.dialects.sqlite import JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class RAGExecution(Base):
    """
    Main table for RAG query executions.

    Stores each RAG query execution with its results, sources,
    and execution details. Related metrics are stored in RAGMetric table.

    Schema Design Rationale:
    - Main execution data in this table (query, answer, technique)
    - Metrics in separate table for normalization and easier aggregation
    - JSON fields for flexibility (sources, execution_details, metadata)
    - Indexes on technique and timestamp for common queries
    - Namespace for multi-tenant support
    """

    __tablename__ = "rag_executions"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Query Information
    query_text = Column(Text, nullable=False, index=True)
    answer_text = Column(Text, nullable=False)
    technique_name = Column(String(50), nullable=False, index=True)

    # Retrieval Configuration
    top_k = Column(Integer, default=5)
    namespace = Column(String(100), nullable=True, index=True)

    # JSON Fields for Flexibility
    sources = Column(JSON, nullable=True)  # List of retrieved chunks with scores
    execution_details = Column(JSON, nullable=True)  # Step-by-step execution info
    extra_metadata = Column(JSON, nullable=True)  # Additional metadata
    full_response = Column(JSON, nullable=True)  # Complete response object from RAG technique

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Relationships
    metrics = relationship(
        "RAGMetric",
        back_populates="execution",
        cascade="all, delete-orphan",
        uselist=False,
    )

    # Indexes for common queries
    __table_args__ = (
        Index("idx_technique_created", "technique_name", "created_at"),
        Index("idx_namespace_created", "namespace", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<RAGExecution(id={self.id}, "
            f"technique='{self.technique_name}', "
            f"created_at='{self.created_at}')>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "query": self.query_text,
            "answer": self.answer_text,
            "technique": self.technique_name,
            "top_k": self.top_k,
            "namespace": self.namespace,
            "sources": self.sources,
            "execution_details": self.execution_details,
            "metadata": self.extra_metadata,
            "full_response": self.full_response,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }


class RAGMetric(Base):
    """
    Performance metrics for RAG executions.

    Stores quantitative metrics for each execution in a separate table
    for easier aggregation and statistical analysis.

    Schema Design Rationale:
    - Separate table for normalization (1-to-1 relationship)
    - Numeric fields for efficient aggregation queries
    - Nullable fields to support partial metrics
    - Foreign key with cascade delete
    """

    __tablename__ = "rag_metrics"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Foreign Key to RAGExecution
    execution_id = Column(
        Integer,
        ForeignKey("rag_executions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # Performance Metrics
    latency_ms = Column(Float, nullable=False)
    latency_seconds = Column(Float, nullable=False)

    # Token Usage
    tokens_input = Column(Integer, nullable=True)
    tokens_output = Column(Integer, nullable=True)
    tokens_total = Column(Integer, nullable=True)

    # Cost Metrics
    cost_input_usd = Column(Float, nullable=True)
    cost_output_usd = Column(Float, nullable=True)
    cost_total_usd = Column(Float, nullable=True)

    # Quality Metrics (from RAGAS evaluation)
    context_precision = Column(Float, nullable=True)
    context_recall = Column(Float, nullable=True)
    faithfulness = Column(Float, nullable=True)
    answer_relevancy = Column(Float, nullable=True)

    # Retrieval Metrics
    chunks_retrieved = Column(Integer, nullable=True)

    # Relationships
    execution = relationship("RAGExecution", back_populates="metrics")

    def __repr__(self) -> str:
        return (
            f"<RAGMetric(id={self.id}, "
            f"execution_id={self.execution_id}, "
            f"latency_ms={self.latency_ms})>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "latency_ms": self.latency_ms,
            "latency_seconds": self.latency_seconds,
            "tokens": {
                "input": self.tokens_input,
                "output": self.tokens_output,
                "total": self.tokens_total,
            } if self.tokens_total else None,
            "cost": {
                "input_usd": self.cost_input_usd,
                "output_usd": self.cost_output_usd,
                "total_usd": self.cost_total_usd,
            } if self.cost_total_usd is not None else None,
            "context_precision": self.context_precision,
            "context_recall": self.context_recall,
            "faithfulness": self.faithfulness,
            "answer_relevancy": self.answer_relevancy,
            "chunks_retrieved": self.chunks_retrieved,
        }


class RAGAnalysis(Base):
    """
    Storage for RAG Analyst agent analyses.

    Stores each analysis generated by the RAG Analyst agent,
    including the question, response, tools used, and metadata.

    Schema Design Rationale:
    - Simple table for storing agent analyses
    - JSON fields for flexibility (tool_calls, analysis_data)
    - analysis_data stores full structured data (aggregated_data, rankings)
    - Timestamp index for filtering by date
    """

    __tablename__ = "rag_analyses"

    # Primary Key
    id = Column(Integer, primary_key=True, autoincrement=True)

    # Analysis Content
    question = Column(Text, nullable=False)
    response = Column(Text, nullable=False)

    # Full Analysis Data (aggregated_data, rankings, etc.)
    analysis_data = Column(JSON, nullable=True)

    # Execution Details
    tool_calls = Column(JSON, nullable=True)  # List of tools used
    iterations = Column(Integer, default=0)
    duration_ms = Column(Float, nullable=True)

    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)

    # Index for timestamp filtering
    __table_args__ = (
        Index("idx_analysis_created", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<RAGAnalysis(id={self.id}, "
            f"question='{self.question[:50]}...', "
            f"created_at='{self.created_at}')>"
        )

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": self.id,
            "question": self.question,
            "response": self.response,
            "analysis_data": self.analysis_data,
            "tool_calls": self.tool_calls,
            "iterations": self.iterations,
            "duration_ms": self.duration_ms,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
