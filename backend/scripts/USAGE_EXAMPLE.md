# Usage Examples - Upload Documentation

## Prerequisites

Install dependencies:
```bash
pip install -r requirements.txt
# or
uv pip install -r requirements.txt
```

Ensure `.env` is configured:
```bash
PINECONE_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
PINECONE_INDEX_NAME=rag-lab
PINECONE_ENVIRONMENT=us-east-1
```

## Basic Upload

Upload all documentation files to Pinecone:

```bash
cd /root/Filipe/Teste-Claude/rag-lab/backend
python3 -m scripts.upload_docs
```

Expected output:
```
📚 RAG Lab Documentation Upload
📂 Source directory: /root/Filipe/Teste-Claude/rag-lab/docs
🎯 Namespace: rag-docs
📊 Max tokens: 512, Overlap: 50
------------------------------------------------------------
🔧 Ensuring Pinecone index exists...
Pinecone index already exists: rag-lab

📖 Processing documentation files:
Reading files: 100%|████████████| 11/11 [00:02<00:00,  4.23it/s]

✅ Processed 143 total chunks from 11 files

⬆️  Uploading to Pinecone...
Uploading batches: 100%|████████████| 2/2 [00:05<00:00,  2.67s/it]

============================================================
✅ Upload complete!
📊 Total files: 11
📊 Total chunks: 143
📊 Average chunks per file: 13.0
============================================================

📋 File breakdown:
  - BASELINE_RAG.md: 12 chunks, 8 sections
  - HYDE.md: 15 chunks, 9 sections
  - RERANKING.md: 14 chunks, 10 sections
  - SUBQUERY.md: 13 chunks, 11 sections
  - FUSION.md: 11 chunks, 7 sections
  - GRAPH_RAG.md: 16 chunks, 12 sections
  - PARENT_DOCUMENT.md: 14 chunks, 9 sections
  - AGENTIC_RAG.md: 13 chunks, 10 sections
  - ADAPTIVE_RAG.md: 15 chunks, 11 sections
  - COMPARISON.md: 10 chunks, 6 sections
  - FUTURE_TECHNIQUES.md: 10 chunks, 5 sections
```

## Clean and Re-upload

Clear existing data before uploading:

```bash
python3 -m scripts.upload_docs --clean
```

## Custom Configuration

```bash
# Use custom namespace
python3 -m scripts.upload_docs --namespace custom-docs

# Adjust chunk size
python3 -m scripts.upload_docs --max-tokens 1024 --overlap 100

# Combine options
python3 -m scripts.upload_docs --clean --namespace rag-v2 --max-tokens 768
```

## Programmatic Usage

### Basic Upload

```python
import asyncio
from scripts.upload_docs import upload_documentation

async def main():
    stats = await upload_documentation()

    print(f"Uploaded {stats['total_chunks']} chunks")
    print(f"From {stats['total_files']} files")
    print(f"Average: {stats['avg_chunks_per_file']:.1f} chunks/file")

asyncio.run(main())
```

### Custom Configuration

```python
import asyncio
from pathlib import Path
from scripts.upload_docs import upload_documentation

async def main():
    # Custom docs directory
    docs_dir = Path("/custom/path/to/docs")

    stats = await upload_documentation(
        docs_dir=docs_dir,
        namespace="custom-namespace",
        clean_index=True,
        max_tokens=1024,
        overlap_tokens=100,
    )

    # Print detailed stats
    for filename, file_stats in stats['file_breakdown'].items():
        print(f"{filename}:")
        print(f"  Chunks: {file_stats['chunks']}")
        print(f"  Sections: {file_stats['sections']}")

asyncio.run(main())
```

## Query Uploaded Documents

After upload, query the documentation:

```python
from core.vector_store import get_vector_store

# Get vector store
vector_store = get_vector_store(namespace="rag-docs")

# Similarity search
results = vector_store.similarity_search(
    "What is HyDE and how does it work?",
    k=5
)

# Print results
for idx, doc in enumerate(results, 1):
    print(f"\n{idx}. {doc.metadata['source']}")
    print(f"   Section: {doc.metadata['section_title']} (H{doc.metadata['section_level']})")
    print(f"   Chunk: {doc.metadata['chunk_index'] + 1}/{doc.metadata['total_chunks']}")
    print(f"   Content: {doc.page_content[:200]}...")
    print("-" * 80)
```

Example output:
```
1. HYDE.md
   Section: Como Funciona (H2)
   Chunk: 1/3
   Content: HyDE (Hypothetical Document Embeddings) inverte o processo tradicional...
--------------------------------------------------------------------------------

2. HYDE.md
   Section: Implementação (H2)
   Chunk: 1/2
   Content: A implementação do HyDE segue estes passos...
--------------------------------------------------------------------------------

3. BASELINE_RAG.md
   Section: Comparação com Técnicas Avançadas (H2)
   Chunk: 1/1
   Content: Embora o RAG Baseline seja simples, técnicas como HyDE...
--------------------------------------------------------------------------------
```

## Verify Upload in Pinecone Console

1. Go to https://app.pinecone.io
2. Select your index (`rag-lab`)
3. Go to "Namespaces" tab
4. Select namespace (`rag-docs`)
5. Check vector count and metadata

## Test Text Splitter

Test the text splitting logic without uploading:

```bash
python3 -m scripts.test_upload
```

This will:
1. Test markdown splitting with sample content
2. Show chunk breakdown and metadata
3. Process a real documentation file
4. Display document structure

## Chunk Metadata Structure

Each uploaded chunk has this metadata:

```python
{
    "source": "HYDE.md",           # Source filename
    "section_title": "Como Funciona",  # Section heading
    "section_level": 2,             # Header level (2=H2, 3=H3)
    "chunk_index": 0,               # Position in section (0-indexed)
    "total_chunks": 3,              # Total chunks in this section
    "file_path": "/path/to/HYDE.md",  # Full file path
    "text": "Content preview..."    # First 1000 chars
}
```

## Troubleshooting

### No module named 'langchain_core'

```bash
pip install langchain-core langchain-pinecone
```

### API Key Error

Check your `.env`:
```bash
cat .env | grep -E "PINECONE|GOOGLE"
```

### Index Not Found

Create the index first:
```python
from core.vector_store import create_index_if_not_exists
create_index_if_not_exists()
```

### Rate Limiting

Reduce batch size in `upload_docs.py`:
```python
batch_size = 50  # Default is 100
```

### Memory Issues

Process files individually:
```python
from pathlib import Path
from utils.text_splitter import split_markdown_by_sections

docs_dir = Path("/root/Filipe/Teste-Claude/rag-lab/docs")

for doc_file in docs_dir.glob("*.md"):
    with open(doc_file) as f:
        content = f.read()

    chunks = split_markdown_by_sections(content)
    print(f"{doc_file.name}: {len(chunks)} chunks")
```

## Advanced: Custom Chunking Strategy

Create your own chunking logic:

```python
from utils.text_splitter import MarkdownChunk, estimate_tokens

def custom_split(text: str, max_tokens: int = 512) -> list[MarkdownChunk]:
    """Custom chunking logic."""
    # Your implementation here
    pass

# Use in upload
from scripts.upload_docs import create_documents_from_chunks

chunks = custom_split(markdown_text)
documents = create_documents_from_chunks(file_path, chunks)
```

## Performance Expectations

- **Processing time**: ~2-5 seconds for 11 files
- **Upload time**: ~5-10 seconds (depends on API rate limits)
- **Total time**: ~10-15 seconds for complete upload
- **Chunk count**: ~140-150 chunks from 11 files
- **Average chunk size**: ~300-400 tokens

## Next Steps

After uploading documentation:

1. **Test retrieval**: Query the vector store
2. **Integrate with RAG**: Use in your RAG techniques
3. **Build chatbot**: Create a documentation chatbot
4. **Evaluate**: Test retrieval quality with RAGAS
5. **Iterate**: Adjust chunk size/overlap based on results
