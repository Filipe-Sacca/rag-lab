"""
Test Documentation Upload

Quick test script to verify text splitting and upload logic.
"""

import asyncio
from pathlib import Path

from utils.text_splitter import estimate_tokens, split_markdown_by_sections


def test_text_splitter():
    """Test markdown splitting with sample content."""
    sample_markdown = """
# Main Title

This is intro content.

## Section 1: Introduction

This is the introduction section with some content.
It has multiple paragraphs.

Here's another paragraph in the introduction.

### Subsection 1.1

This is a subsection with detailed information.

## Section 2: Implementation

This section discusses implementation details.

### Subsection 2.1: Code Example

Here's some code and explanation.

### Subsection 2.2: Best Practices

Best practices for implementation.

## Section 3: Conclusion

Final thoughts and summary.
"""

    print("🧪 Testing Text Splitter")
    print("=" * 60)

    # Test token estimation
    tokens = estimate_tokens(sample_markdown)
    print(f"📊 Total estimated tokens: {tokens}")

    # Test markdown splitting
    chunks = split_markdown_by_sections(
        sample_markdown,
        max_tokens=100,  # Small for testing
        overlap_tokens=20,
    )

    print(f"📦 Total chunks: {len(chunks)}")
    print("\n📋 Chunk breakdown:")

    for idx, chunk in enumerate(chunks):
        print(f"\n  Chunk {idx + 1}:")
        print(f"    Section: {chunk.section_title}")
        print(f"    Level: H{chunk.section_level}")
        print(f"    Position: {chunk.chunk_index + 1}/{chunk.total_chunks}")
        print(f"    Tokens: ~{estimate_tokens(chunk.content)}")
        print(f"    Preview: {chunk.content[:100]}...")

    print("\n" + "=" * 60)
    print("✅ Text splitter test complete!")


async def test_upload_single_file():
    """Test upload logic with a single file."""
    from scripts.upload_docs import create_documents_from_chunks

    print("\n🧪 Testing Document Creation")
    print("=" * 60)

    # Read a sample file
    docs_dir = Path(__file__).parent.parent.parent / "docs"
    sample_file = docs_dir / "BASELINE_RAG.md"

    if not sample_file.exists():
        print(f"❌ Sample file not found: {sample_file}")
        return

    with open(sample_file, encoding="utf-8") as f:
        content = f.read()

    # Split into chunks
    chunks = split_markdown_by_sections(content, max_tokens=512, overlap_tokens=50)

    # Convert to documents
    documents = create_documents_from_chunks(sample_file, chunks)

    print(f"📄 File: {sample_file.name}")
    print(f"📦 Total chunks: {len(chunks)}")
    print(f"📝 Sample document metadata:")

    if documents:
        sample_doc = documents[0]
        print(f"  - Source: {sample_doc.metadata['source']}")
        print(f"  - Section: {sample_doc.metadata['section_title']}")
        print(f"  - Level: {sample_doc.metadata['section_level']}")
        print(f"  - Position: {sample_doc.metadata['chunk_index']}/{sample_doc.metadata['total_chunks']}")
        print(f"  - Content preview: {sample_doc.page_content[:200]}...")

    print("\n" + "=" * 60)
    print("✅ Document creation test complete!")


async def main():
    """Run all tests."""
    test_text_splitter()
    await test_upload_single_file()


if __name__ == "__main__":
    asyncio.run(main())
