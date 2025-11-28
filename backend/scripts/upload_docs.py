"""
Documentation Upload Script

Upload RAG Lab documentation to Pinecone with intelligent chunking.

Usage:
    python -m scripts.upload_docs
    python -m scripts.upload_docs --clean  # Clean index first
"""

import asyncio
import sys
from pathlib import Path
from typing import Any

from langchain_core.documents import Document
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.embeddings import get_document_embedding_model
from core.vector_store import create_index_if_not_exists, get_pinecone_client
from utils.text_splitter import split_markdown_by_sections


# Documentation files to index
DOC_FILES = [
    "BASELINE_RAG.md",
    "HYDE.md",
    "RERANKING.md",
    "SUBQUERY.md",
    "FUSION.md",
    "GRAPH_RAG.md",
    "PARENT_DOCUMENT.md",
    "AGENTIC_RAG.md",
    "ADAPTIVE_RAG.md",
    "COMPARISON.md",
    "FUTURE_TECHNIQUES.md",
]


def read_markdown_file(file_path: Path) -> str:
    """Read markdown file content."""
    with open(file_path, encoding="utf-8") as f:
        return f.read()


def create_documents_from_chunks(
    file_path: Path,
    chunks: list[Any],
) -> list[Document]:
    """
    Convert markdown chunks to LangChain Documents with metadata.

    Args:
        file_path: Path to source file
        chunks: List of MarkdownChunk objects

    Returns:
        List of Document objects ready for indexing
    """
    documents = []

    for chunk in chunks:
        doc = Document(
            page_content=chunk.content,
            metadata={
                "source": file_path.name,
                "document": file_path.name,  # Add explicit 'document' field for frontend
                "section_title": chunk.section_title,
                "section_level": chunk.section_level,
                "chunk_index": chunk.chunk_index,
                "page": int(chunk.chunk_index) if chunk.chunk_index else 0,  # Use chunk_index as "page"
                "total_chunks": chunk.total_chunks,
                "file_path": str(file_path),
            },
        )
        documents.append(doc)

    return documents


async def upload_documentation(
    docs_dir: Path | None = None,
    namespace: str = "rag-docs",
    clean_index: bool = False,
    max_tokens: int = 512,
    overlap_tokens: int = 50,
) -> dict[str, Any]:
    """
    Upload RAG Lab documentation to Pinecone.

    Args:
        docs_dir: Documentation directory (defaults to ../docs)
        namespace: Pinecone namespace
        clean_index: Whether to clean the namespace first
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Token overlap between chunks

    Returns:
        Dictionary with upload statistics

    Example:
        >>> import asyncio
        >>> stats = asyncio.run(upload_documentation())
        >>> print(f"Uploaded {stats['total_chunks']} chunks")
    """
    # Setup paths
    if docs_dir is None:
        docs_dir = Path(__file__).parent.parent.parent / "docs"

    print(f"📚 RAG Lab Documentation Upload")
    print(f"📂 Source directory: {docs_dir}")
    print(f"🎯 Namespace: {namespace}")
    print(f"📊 Max tokens: {max_tokens}, Overlap: {overlap_tokens}")
    print("-" * 60)

    # Ensure index exists
    print("🔧 Ensuring Pinecone index exists...")
    create_index_if_not_exists()

    # Get Pinecone client and index
    pc = get_pinecone_client()
    from config import settings

    index = pc.Index(settings.PINECONE_INDEX_NAME)

    # Clean namespace if requested
    if clean_index:
        print(f"🧹 Cleaning namespace '{namespace}'...")
        try:
            index.delete(delete_all=True, namespace=namespace)
            print("✅ Namespace cleaned")
        except Exception as e:
            print(f"⚠️  Warning: Could not clean namespace: {e}")

    # Process each documentation file
    all_documents = []
    file_stats = {}

    print("\n📖 Processing documentation files:")
    for doc_file in tqdm(DOC_FILES, desc="Reading files"):
        file_path = docs_dir / doc_file

        if not file_path.exists():
            print(f"⚠️  Skipping missing file: {doc_file}")
            continue

        # Read and split markdown
        content = read_markdown_file(file_path)
        chunks = split_markdown_by_sections(
            content,
            max_tokens=max_tokens,
            overlap_tokens=overlap_tokens,
        )

        # Convert to Documents
        documents = create_documents_from_chunks(file_path, chunks)
        all_documents.extend(documents)

        # Track stats
        file_stats[doc_file] = {
            "chunks": len(chunks),
            "sections": len({chunk.section_title for chunk in chunks}),
        }

    print(f"\n✅ Processed {len(all_documents)} total chunks from {len(file_stats)} files")

    # Upload to Pinecone in batches
    print("\n⬆️  Uploading to Pinecone...")
    embeddings = get_document_embedding_model()

    batch_size = 100
    total_uploaded = 0

    for i in tqdm(range(0, len(all_documents), batch_size), desc="Uploading batches"):
        batch = all_documents[i : i + batch_size]

        # Generate embeddings for batch
        texts = [doc.page_content for doc in batch]
        vectors = embeddings.embed_documents(texts)

        # Prepare vectors for Pinecone
        pinecone_vectors = []
        for idx, (doc, vector) in enumerate(zip(batch, vectors)):
            vector_id = f"{doc.metadata['source']}_chunk_{i + idx}"
            pinecone_vectors.append(
                {
                    "id": vector_id,
                    "values": vector,
                    "metadata": {
                        **doc.metadata,
                        "text": doc.page_content[:1000],  # First 1000 chars
                    },
                }
            )

        # Upsert to Pinecone
        index.upsert(vectors=pinecone_vectors, namespace=namespace)
        total_uploaded += len(batch)

    # Compile statistics
    stats = {
        "total_files": len(file_stats),
        "total_chunks": len(all_documents),
        "namespace": namespace,
        "file_breakdown": file_stats,
        "avg_chunks_per_file": (
            len(all_documents) / len(file_stats) if file_stats else 0
        ),
    }

    print("\n" + "=" * 60)
    print("✅ Upload complete!")
    print(f"📊 Total files: {stats['total_files']}")
    print(f"📊 Total chunks: {stats['total_chunks']}")
    print(f"📊 Average chunks per file: {stats['avg_chunks_per_file']:.1f}")
    print("=" * 60)

    print("\n📋 File breakdown:")
    for file_name, file_stat in file_stats.items():
        print(f"  - {file_name}: {file_stat['chunks']} chunks, {file_stat['sections']} sections")

    return stats


async def main():
    """Main entry point for script."""
    import argparse

    parser = argparse.ArgumentParser(description="Upload RAG Lab documentation to Pinecone")
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean namespace before upload",
    )
    parser.add_argument(
        "--namespace",
        default="rag-docs",
        help="Pinecone namespace (default: rag-docs)",
    )
    parser.add_argument(
        "--max-tokens",
        type=int,
        default=512,
        help="Maximum tokens per chunk (default: 512)",
    )
    parser.add_argument(
        "--overlap",
        type=int,
        default=50,
        help="Token overlap (default: 50)",
    )

    args = parser.parse_args()

    try:
        stats = await upload_documentation(
            namespace=args.namespace,
            clean_index=args.clean,
            max_tokens=args.max_tokens,
            overlap_tokens=args.overlap,
        )

        return stats

    except Exception as e:
        print(f"\n❌ Error during upload: {e}")
        import traceback

        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
