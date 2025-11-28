"""
API Routes for RAG Lab

Endpoints for document upload, querying, and evaluation.
"""

from fastapi import APIRouter, HTTPException, status, Depends
from langchain.text_splitter import RecursiveCharacterTextSplitter
from sqlalchemy.orm import Session

from config import settings
from core import get_vector_store
from db import get_db
from db.helpers import save_rag_result
from models.schemas import (
    QueryRequest,
    QueryResponse,
    RAGMetrics,
    UploadRequest,
    UploadResponse,
)
from techniques.baseline_rag import baseline_rag
from techniques.hyde_rag import hyde_rag
from techniques.reranking_rag import reranking_rag
from techniques.agentic_rag import agentic_rag
from techniques.fusion import fusion_rag
from techniques.subquery import subquery_rag
from techniques.graph_rag import graph_rag
from techniques.adaptive import adaptive_rag
import asyncio

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@router.post("/upload", response_model=UploadResponse)
async def upload_document(request: UploadRequest) -> UploadResponse:
    """
    Upload and index a document in Pinecone.

    Args:
        request: Upload request with document text and metadata

    Returns:
        UploadResponse: Upload status and metadata

    Raises:
        HTTPException: If upload fails
    """
    try:
        # Split text into chunks
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=request.chunk_size,
            chunk_overlap=request.chunk_overlap,
            length_function=len,
        )
        chunks = text_splitter.split_text(request.text)

        if not chunks:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No chunks created from text",
            )

        # Get vector store
        vector_store = get_vector_store(namespace=request.namespace)

        # Enhance metadata for each chunk
        enhanced_metadatas = []
        for idx, chunk in enumerate(chunks):
            chunk_metadata = {
                **request.metadata,  # User-provided metadata
                "chunk_index": idx,
                "total_chunks": len(chunks),
            }
            # Add 'document' field if not present (use 'source' as fallback)
            if "document" not in chunk_metadata and "source" in chunk_metadata:
                chunk_metadata["document"] = chunk_metadata["source"]
            # Add 'page' field if not present (use chunk_index as fallback)
            if "page" not in chunk_metadata:
                chunk_metadata["page"] = idx
            enhanced_metadatas.append(chunk_metadata)

        # Add documents to vector store
        vector_store.add_texts(
            texts=chunks,
            metadatas=enhanced_metadatas,
        )

        return UploadResponse(
            success=True,
            num_chunks=len(chunks),
            namespace=request.namespace,
            message=f"Successfully indexed {len(chunks)} chunks",
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Upload failed: {str(e)}",
        ) from e


@router.post("/query", response_model=QueryResponse)
async def query_rag(
    request: QueryRequest,
    db: Session = Depends(get_db),
) -> QueryResponse:
    """
    Query the RAG system with a specific technique.

    Automatically saves execution results to database for tracking
    and analytics.

    Args:
        request: Query request with question and technique
        db: Database session (auto-injected)

    Returns:
        QueryResponse: Generated answer with retrieved docs and metrics

    Raises:
        HTTPException: If query fails
    """
    try:
        # Map de técnicas
        technique_map = {
            "baseline": baseline_rag,
            "hyde": hyde_rag,
            "reranking": reranking_rag,
            "agentic": agentic_rag,
            "fusion": fusion_rag,
            "subquery": subquery_rag,
            "graph": graph_rag,
            "adaptive": adaptive_rag,
        }

        technique_func = technique_map.get(request.technique, baseline_rag)

        # Preparar parâmetros para a técnica
        technique_params = {
            "query": request.query,
            "top_k": request.top_k,
            "namespace": request.namespace,
        }

        # Add Cohere API key for reranking technique
        if request.technique == "reranking":
            technique_params["cohere_api_key"] = settings.COHERE_API_KEY

        # Fusion RAG uses different parameter names
        if request.technique == "fusion":
            technique_params.pop("top_k", None)
            technique_params["final_top_k"] = request.top_k
            technique_params["top_k_per_query"] = request.top_k * 2  # Retrieve more for fusion

        # Sub-Query RAG uses top_k_per_subquery
        if request.technique == "subquery":
            technique_params.pop("top_k", None)
            technique_params["top_k_per_subquery"] = request.top_k

        # Graph RAG uses initial_top_k and final_top_k
        if request.technique == "graph":
            technique_params.pop("top_k", None)
            technique_params["initial_top_k"] = request.top_k * 2  # Retrieve more for expansion
            technique_params["final_top_k"] = request.top_k

        # Agentic RAG uses params dict for configuration
        if request.technique == "agentic":
            top_k = technique_params.pop("top_k", None)
            technique_params["params"] = {
                "default_technique": "baseline",
                "max_iterations": 10,
                "top_k": top_k,  # Pass top_k inside params dict
            }

        # Adaptive RAG uses top_k directly (not params dict)
        # No special handling needed - uses standard params

        # Executa técnica (async ou sync)
        if asyncio.iscoroutinefunction(technique_func):
            result = await technique_func(**technique_params)
        else:
            result = technique_func(**technique_params)

        # Save to database (non-blocking, won't fail request if DB error)
        try:
            execution_id = save_rag_result(
                db,
                result,
                technique=request.technique,
                namespace=request.namespace,
                top_k=request.top_k,
            )
        except Exception as db_error:
            print(f"Warning: Failed to save execution to database: {db_error}")
            execution_id = None

        # Transform sources to include proper metadata for frontend
        sources = []
        for doc in result.get("sources", []):
            # Extract metadata with fallbacks
            metadata = doc.get("metadata", {})

            # Get score with fallback chain: rerank_score → rrf_score → score → original_score → 0.0
            # This ensures compatibility with all RAG techniques
            score = doc.get("rerank_score") or doc.get("rrf_score") or doc.get("score") or doc.get("original_score") or 0.0

            # Handle original_score: can be a list (fusion) or single value (other techniques)
            orig_scores = doc.get("original_scores") or doc.get("original_score") or doc.get("score") or score
            if isinstance(orig_scores, list):
                original_score = max(orig_scores) if orig_scores else score  # Use max of original scores
            else:
                original_score = orig_scores

            # Map 'source' to 'document' and add missing fields
            source_obj = {
                "content": doc.get("content", ""),
                "score": float(score),
                "original_score": float(original_score),  # For progress bar tooltip
                "metadata": {
                    "document": metadata.get("source", metadata.get("document", "unknown")),
                    "page": metadata.get("page", metadata.get("page_number", 0)),
                    "chunk_id": metadata.get("chunk_id", f"chunk_{metadata.get('chunk_index', 0)}"),
                    # Preserve additional metadata
                    "section_title": metadata.get("section_title"),
                    "file_path": metadata.get("file_path"),
                }
            }
            sources.append(source_obj)

        return QueryResponse(
            query=result["query"],
            answer=result["answer"],
            technique=request.technique,
            retrieved_docs=[doc["content"] for doc in result.get("sources", [])],
            metrics=RAGMetrics(**result.get("metrics", {})) if result.get("metrics") else None,
            metadata={
                "top_k": request.top_k,
                "num_docs_retrieved": len(result.get("sources", [])),
                "execution_details": result.get("execution_details", {}),
                "execution_id": execution_id,  # Include DB ID in response
                "sources": sources,  # Add structured sources with scores and metadata
            },
        )

    except Exception as e:
        import traceback
        traceback.print_exc()  # Print full traceback to logs
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Query failed: {str(e)}",
        ) from e


@router.get("/techniques")
async def list_techniques() -> list[dict]:
    """
    List all available RAG techniques with metadata.

    Returns:
        list: List of RAG technique objects
    """
    return [
        {
            "id": "baseline",
            "name": "Baseline RAG",
            "description": "Traditional RAG: retrieve → generate",
            "complexity": "low",
            "avg_latency_ms": 850,
            "avg_cost_usd": 0.002,
            "implemented": True
        },
        {
            "id": "hyde",
            "name": "HyDE",
            "description": "Hypothetical Document Embeddings: generate answer → embed → retrieve",
            "complexity": "medium",
            "avg_latency_ms": 1200,
            "avg_cost_usd": 0.004,
            "implemented": True
        },
        {
            "id": "reranking",
            "name": "Reranking",
            "description": "Retrieve → rerank with cross-encoder → generate",
            "complexity": "medium",
            "avg_latency_ms": 1100,
            "avg_cost_usd": 0.003,
            "implemented": True
        },
        {
            "id": "agentic",
            "name": "Agentic RAG",
            "description": "LLM agent decides when and how to retrieve",
            "complexity": "high",
            "avg_latency_ms": 1800,
            "avg_cost_usd": 0.006,
            "implemented": True
        },
        {
            "id": "fusion",
            "name": "RAG Fusion",
            "description": "Multiple query variations + Reciprocal Rank Fusion",
            "complexity": "medium",
            "avg_latency_ms": 1600,
            "avg_cost_usd": 0.005,
            "implemented": True
        },
        {
            "id": "subquery",
            "name": "Sub-Query RAG",
            "description": "Decompose complex queries → multiple retrievals → aggregate",
            "complexity": "high",
            "avg_latency_ms": 1800,
            "avg_cost_usd": 0.006,
            "implemented": True
        },
        {
            "id": "graph",
            "name": "Graph RAG",
            "description": "Knowledge graph enhanced retrieval with entity expansion",
            "complexity": "high",
            "avg_latency_ms": 2000,
            "avg_cost_usd": 0.007,
            "implemented": True
        },
        {
            "id": "stepback",
            "name": "Step-Back Prompting",
            "description": "Ask broader question first → retrieve → specific answer",
            "complexity": "medium",
            "avg_latency_ms": 1300,
            "avg_cost_usd": 0.004,
            "implemented": False
        },
        {
            "id": "adaptive",
            "name": "Adaptive RAG",
            "description": "Classifica a query e roteia para a melhor técnica automaticamente",
            "complexity": "very_high",
            "avg_latency_ms": 2200,
            "avg_cost_usd": 0.009,
            "implemented": True
        }
    ]


@router.get("/stats")
async def get_stats(namespace: str | None = None) -> dict[str, int]:
    """
    Get statistics about the vector store.

    Args:
        namespace: Optional namespace to query stats for

    Returns:
        dict: Vector store statistics

    Note:
        This is a placeholder - Pinecone stats API may vary
    """
    try:
        # Placeholder - actual implementation depends on Pinecone API
        return {
            "total_vectors": 0,
            "namespace": namespace or "default",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Stats retrieval failed: {str(e)}",
        ) from e
