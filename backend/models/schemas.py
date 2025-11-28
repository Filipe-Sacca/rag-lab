"""
Pydantic Models for RAG Lab API

Request and response schemas for all API endpoints.
"""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class RAGTechnique(str, Enum):
    """Available RAG techniques."""

    BASELINE = "baseline"
    HYDE = "hyde"
    RERANKING = "reranking"
    AGENTIC = "agentic"
    MULTIQUERY = "multiquery"
    FUSION = "fusion"
    DECOMPOSITION = "decomposition"
    SUBQUERY = "subquery"  # Sub-Query decomposition
    GRAPH = "graph"  # Graph RAG with entity expansion
    STEPBACK = "stepback"
    ADAPTIVE = "adaptive"
    CORRECTIVE = "corrective"
    SELFQUERY = "selfquery"


class QueryRequest(BaseModel):
    """Request model for RAG query endpoint."""

    query: str = Field(..., description="User question to answer", min_length=1)
    technique: RAGTechnique = Field(
        default=RAGTechnique.BASELINE,
        description="RAG technique to use",
    )
    top_k: int = Field(
        default=5,
        description="Number of documents to retrieve",
        ge=1,
        le=20,
    )
    enable_evaluation: bool = Field(
        default=False,
        description="Enable RAGAS evaluation",
    )
    namespace: str | None = Field(
        default=None,
        description="Pinecone namespace to query",
    )


class TokenMetrics(BaseModel):
    """Token usage metrics."""

    input: int = Field(default=0, description="Input tokens used")
    output: int = Field(default=0, description="Output tokens used")
    total: int = Field(default=0, description="Total tokens used")


class CostMetrics(BaseModel):
    """Cost breakdown metrics."""

    input_usd: float = Field(default=0.0, description="Input cost in USD")
    output_usd: float = Field(default=0.0, description="Output cost in USD")
    total_usd: float = Field(default=0.0, description="Total cost in USD")
    llm_usd: float | None = Field(default=None, description="LLM cost in USD")
    rerank_usd: float | None = Field(default=None, description="Reranking cost in USD")


class RAGMetrics(BaseModel):
    """Complete RAG metrics including performance and RAGAS evaluation."""

    # Performance metrics
    latency_ms: float = Field(default=0.0, description="Total latency in milliseconds")
    latency_seconds: float = Field(default=0.0, description="Total latency in seconds")

    # Token metrics
    tokens: TokenMetrics = Field(default_factory=TokenMetrics, description="Token usage")

    # Cost metrics
    cost: CostMetrics = Field(default_factory=CostMetrics, description="Cost breakdown")

    # Retrieval metrics
    chunks_retrieved: int = Field(default=0, description="Number of chunks retrieved")
    technique: str | None = Field(default=None, description="Technique used")

    # RAGAS evaluation metrics
    faithfulness: float | None = Field(
        default=None,
        description="How factually accurate the answer is",
        ge=0.0,
        le=1.0,
    )
    answer_relevancy: float | None = Field(
        default=None,
        description="How relevant the answer is to the question",
        ge=0.0,
        le=1.0,
    )
    context_precision: float | None = Field(
        default=None,
        description="How precise the retrieved context is",
        ge=0.0,
        le=1.0,
    )
    context_recall: float | None = Field(
        default=None,
        description="How much relevant context was retrieved",
        ge=0.0,
        le=1.0,
    )


class QueryResponse(BaseModel):
    """Response model for RAG query endpoint."""

    query: str = Field(..., description="Original user query")
    answer: str = Field(..., description="Generated answer")
    technique: RAGTechnique = Field(..., description="RAG technique used")
    retrieved_docs: list[str] = Field(
        default_factory=list,
        description="Retrieved document chunks",
    )
    metrics: RAGMetrics | None = Field(
        default=None,
        description="RAGAS evaluation metrics (if enabled)",
    )
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional metadata (latency, token count, etc)",
    )


class UploadRequest(BaseModel):
    """Request model for document upload endpoint."""

    text: str = Field(..., description="Document text to upload", min_length=1)
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="Document metadata",
    )
    namespace: str | None = Field(
        default=None,
        description="Pinecone namespace for organization",
    )
    chunk_size: int = Field(
        default=1000,
        description="Text chunk size",
        ge=100,
        le=4000,
    )
    chunk_overlap: int = Field(
        default=200,
        description="Overlap between chunks",
        ge=0,
        le=500,
    )


class UploadResponse(BaseModel):
    """Response model for document upload endpoint."""

    success: bool = Field(..., description="Upload success status")
    num_chunks: int = Field(..., description="Number of chunks created")
    namespace: str | None = Field(default=None, description="Namespace used")
    message: str = Field(..., description="Status message")


class HealthResponse(BaseModel):
    """Response model for health check endpoint."""

    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    environment: str = Field(..., description="Environment (dev/prod)")
