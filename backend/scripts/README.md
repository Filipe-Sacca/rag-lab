# RAG Lab Scripts

Utility scripts for data management and operations.

## Upload Documentation

Upload RAG Lab documentation to Pinecone with intelligent chunking.

### Quick Start

```bash
# Basic upload
python -m scripts.upload_docs

# Clean and re-upload
python -m scripts.upload_docs --clean

# Custom configuration
python -m scripts.upload_docs --namespace custom-docs --max-tokens 1024 --overlap 100
```

### Options

- `--clean` - Clean namespace before upload
- `--namespace NAME` - Pinecone namespace (default: `rag-docs`)
- `--max-tokens N` - Maximum tokens per chunk (default: `512`)
- `--overlap N` - Token overlap between chunks (default: `50`)

### What Gets Uploaded

11 documentation files from `/docs`:
- BASELINE_RAG.md
- HYDE.md
- RERANKING.md
- SUBQUERY.md
- FUSION.md
- GRAPH_RAG.md
- PARENT_DOCUMENT.md
- AGENTIC_RAG.md
- ADAPTIVE_RAG.md
- COMPARISON.md
- FUTURE_TECHNIQUES.md

### Chunking Strategy

1. **Section-aware splitting**: Splits by H2 (`##`) and H3 (`###`) headers
2. **Token limits**: Chunks respect max token limits (default 512)
3. **Overlap**: Maintains context with token overlap (default 50)
4. **Metadata**: Rich metadata for each chunk:
   - `source`: Filename
   - `section_title`: Section heading
   - `section_level`: Header level (2 or 3)
   - `chunk_index`: Position in section
   - `total_chunks`: Total chunks in section

### Output Example

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
  ...
```

### Programmatic Usage

```python
import asyncio
from scripts.upload_docs import upload_documentation

# Basic upload
stats = asyncio.run(upload_documentation())
print(f"Uploaded {stats['total_chunks']} chunks")

# Custom configuration
stats = asyncio.run(
    upload_documentation(
        namespace="custom-docs",
        clean_index=True,
        max_tokens=1024,
        overlap_tokens=100,
    )
)
```

### Verification

After upload, verify in Pinecone console or query:

```python
from core.vector_store import get_vector_store

vector_store = get_vector_store(namespace="rag-docs")
results = vector_store.similarity_search("What is HyDE?", k=3)

for doc in results:
    print(f"Source: {doc.metadata['source']}")
    print(f"Section: {doc.metadata['section_title']}")
    print(f"Content: {doc.page_content[:200]}...")
    print("-" * 60)
```

## Troubleshooting

### Missing Dependencies

```bash
# Install required packages
uv pip install tqdm langchain-core langchain-pinecone langchain-google-genai
```

### Import Errors

Ensure you run from the backend directory:
```bash
cd /root/Filipe/Teste-Claude/rag-lab/backend
python -m scripts.upload_docs
```

### API Key Issues

Check your `.env` file:
```bash
PINECONE_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
```

### Rate Limits

If you hit rate limits, reduce batch size in the script:
```python
batch_size = 50  # Reduce from 100
```
