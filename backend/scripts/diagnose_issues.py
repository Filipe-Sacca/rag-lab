"""
Diagnostic Script for RAG Lab Issues

Investigates:
1. Zero similarity scores
2. Missing metadata (document name, page number)
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.vector_store import get_vector_store, get_pinecone_client
from core.embeddings import get_query_embedding_model
from config import settings


def diagnose_pinecone_index():
    """Check Pinecone index configuration and stats."""
    print("=" * 80)
    print("PINECONE INDEX DIAGNOSTICS")
    print("=" * 80)

    pc = get_pinecone_client()
    index = pc.Index(settings.PINECONE_INDEX_NAME)

    # Get index stats
    stats = index.describe_index_stats()

    print(f"\n📊 Index Name: {settings.PINECONE_INDEX_NAME}")
    print(f"📊 Total Vectors: {stats.total_vector_count}")
    print(f"📊 Dimension: {stats.dimension}")

    print(f"\n📂 Namespaces:")
    for namespace, ns_stats in stats.namespaces.items():
        print(f"  - {namespace}: {ns_stats.vector_count} vectors")

    # Check if dimension matches our embeddings
    embeddings = get_query_embedding_model()
    test_embedding = embeddings.embed_query("test")
    print(f"\n🧮 Expected Dimension: {len(test_embedding)}")
    print(f"🧮 Index Dimension: {stats.dimension}")

    if len(test_embedding) != stats.dimension:
        print("❌ DIMENSION MISMATCH! This causes zero scores.")
        print(f"   Expected: {len(test_embedding)}, Got: {stats.dimension}")
    else:
        print("✅ Dimension matches correctly")

    return stats


def test_vector_retrieval():
    """Test vector retrieval and inspect metadata."""
    print("\n" + "=" * 80)
    print("VECTOR RETRIEVAL TEST")
    print("=" * 80)

    vector_store = get_vector_store(namespace=settings.PINECONE_NAMESPACE)

    # Test query
    test_query = "What is RAG?"
    print(f"\n🔍 Test Query: '{test_query}'")

    # Retrieve with scores
    results = vector_store.similarity_search_with_score(test_query, k=3)

    print(f"\n📦 Retrieved {len(results)} documents")

    for i, (doc, score) in enumerate(results, 1):
        print(f"\n--- Document {i} ---")
        print(f"Score: {score:.4f} ({score * 100:.2f}%)")
        print(f"Content preview: {doc.page_content[:100]}...")
        print(f"Metadata: {doc.metadata}")

        # Check for expected metadata fields
        if "document" not in doc.metadata and "source" not in doc.metadata:
            print("⚠️  Missing document name field")
        if "page" not in doc.metadata:
            print("⚠️  Missing page number field")

    return results


def check_raw_vectors():
    """Fetch raw vectors from Pinecone to inspect structure."""
    print("\n" + "=" * 80)
    print("RAW VECTOR INSPECTION")
    print("=" * 80)

    pc = get_pinecone_client()
    index = pc.Index(settings.PINECONE_INDEX_NAME)

    # Fetch a few vectors directly
    try:
        # Query for any vectors in the namespace
        query_response = index.query(
            namespace=settings.PINECONE_NAMESPACE,
            vector=[0.0] * 768,  # Dummy vector
            top_k=3,
            include_metadata=True
        )

        print(f"\n📦 Found {len(query_response.matches)} vectors")

        for i, match in enumerate(query_response.matches, 1):
            print(f"\n--- Vector {i} ---")
            print(f"ID: {match.id}")
            print(f"Score: {match.score:.4f}")
            print(f"Metadata: {match.metadata}")

            # Check metadata structure
            metadata = match.metadata
            has_text = 'text' in metadata
            has_source = 'source' in metadata or 'document' in metadata
            has_page = 'page' in metadata or 'page_number' in metadata

            print(f"✅ Has text: {has_text}")
            print(f"{'✅' if has_source else '❌'} Has source/document: {has_source}")
            print(f"{'✅' if has_page else '❌'} Has page: {has_page}")

    except Exception as e:
        print(f"❌ Error fetching raw vectors: {e}")


def diagnose_similarity_scores():
    """Investigate why similarity scores are 0.0."""
    print("\n" + "=" * 80)
    print("SIMILARITY SCORE DIAGNOSTICS")
    print("=" * 80)

    embeddings = get_query_embedding_model()
    pc = get_pinecone_client()
    index = pc.Index(settings.PINECONE_INDEX_NAME)

    # Generate test embedding
    test_query = "What is baseline RAG?"
    query_embedding = embeddings.embed_query(test_query)

    print(f"\n🔍 Query: '{test_query}'")
    print(f"🧮 Embedding dimension: {len(query_embedding)}")
    print(f"🧮 Embedding sample (first 5): {query_embedding[:5]}")

    # Query Pinecone directly
    try:
        results = index.query(
            namespace=settings.PINECONE_NAMESPACE,
            vector=query_embedding,
            top_k=3,
            include_metadata=True,
            include_values=False
        )

        print(f"\n📦 Retrieved {len(results.matches)} results")

        for i, match in enumerate(results.matches, 1):
            print(f"\n--- Match {i} ---")
            print(f"Score: {match.score:.6f} ({match.score * 100:.2f}%)")
            print(f"ID: {match.id}")

            if match.score == 0.0:
                print("❌ ZERO SCORE DETECTED!")
                print("   Possible causes:")
                print("   1. Dimension mismatch")
                print("   2. Empty/invalid vectors in index")
                print("   3. Wrong similarity metric")

    except Exception as e:
        print(f"❌ Error during similarity search: {e}")


def main():
    """Run all diagnostics."""
    print("\n" + "🔬" * 40)
    print("RAG LAB DIAGNOSTICS REPORT")
    print("🔬" * 40 + "\n")

    try:
        # 1. Check Pinecone index configuration
        stats = diagnose_pinecone_index()

        # 2. Test vector retrieval with LangChain
        results = test_vector_retrieval()

        # 3. Check raw vectors in Pinecone
        check_raw_vectors()

        # 4. Diagnose similarity scores
        diagnose_similarity_scores()

        # Summary
        print("\n" + "=" * 80)
        print("SUMMARY")
        print("=" * 80)

        if stats.total_vector_count == 0:
            print("\n❌ CRITICAL: No vectors in index!")
            print("   Action: Upload documents first")

        if results and all(score == 0.0 for _, score in results):
            print("\n❌ CRITICAL: All similarity scores are 0.0")
            print("   Action: Check dimension mismatch or re-index with proper embeddings")

        if results:
            doc, _ = results[0]
            if "source" not in doc.metadata and "document" not in doc.metadata:
                print("\n❌ CRITICAL: Missing document metadata")
                print("   Action: Re-upload documents with proper metadata extraction")

        print("\n✅ Diagnostics complete")

    except Exception as e:
        print(f"\n❌ Error during diagnostics: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
