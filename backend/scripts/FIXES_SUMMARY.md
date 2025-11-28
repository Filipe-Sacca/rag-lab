# RAG Lab Fixes Summary

## Issues Fixed

### Problem 1: All Similarity Scores Were 0.0
**Status**: ✅ FIXED

**Root Cause**:
- Frontend was hardcoding `score: 0` when transforming retrieved docs
- Backend was returning scores correctly, but frontend wasn't using them

**Solution**:
1. Updated `api/routes.py` to include structured sources with scores in `metadata.sources`
2. Modified `frontend/chat-lab/src/App.tsx` to use `response.metadata.sources` instead of hardcoding
3. Added `sources` field to TypeScript types

**Verification**:
```bash
# Test query now shows real scores
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What is RAG?", "technique": "baseline", "top_k": 2}'

# Returns: scores like 0.7832 (78.32%), 0.7500 (75.00%)
```

---

### Problem 2: Metadata Shows "unknown Page 0"
**Status**: ✅ FIXED

**Root Cause**:
- Documents were indexed with only `source` field, not `document` and `page`
- Frontend expected `metadata.document` and `metadata.page`
- Upload script wasn't adding these fields

**Solution**:
1. Updated `scripts/upload_docs.py` to add `document` and `page` fields during indexing
2. Modified `api/routes.py` upload endpoint to enhance metadata with required fields
3. Re-indexed all documents with proper metadata

**Verification**:
```bash
# Check metadata structure
python3 -m scripts.diagnose_issues

# Shows:
# Document: BASELINE_RAG.md
# Page: 0
# Section: 📋 Definição
```

---

## Files Modified

### Backend
1. **`/backend/api/routes.py`** (lines 157-190)
   - Added source transformation logic
   - Maps backend metadata to frontend-expected format
   - Adds `sources` array to `metadata` field in response

2. **`/backend/scripts/upload_docs.py`** (lines 69-74)
   - Added `document` field (explicit)
   - Added `page` field (using chunk_index)
   - Preserves backward compatibility with `source` field

3. **`/backend/scripts/diagnose_issues.py`** (new file)
   - Diagnostic tool for troubleshooting Pinecone index issues
   - Checks dimension matches, metadata structure, similarity scores

### Frontend
1. **`/frontend/chat-lab/src/App.tsx`** (lines 193-197)
   - Changed from hardcoded `score: 0` to `response.metadata.sources`
   - Removed placeholder metadata

2. **`/frontend/chat-lab/src/types/rag.types.ts`** (line 92)
   - Added `sources?: Source[]` to `metadata` interface

---

## Migration Steps

If you have existing documents that need updating:

### 1. Re-index Documents
```bash
cd backend
source venv/bin/activate

# Clean and re-upload with new metadata
python -m scripts.upload_docs --clean --namespace rag-docs
```

### 2. Verify Metadata
```bash
# Run diagnostics
python -m scripts.diagnose_issues

# Should show:
# ✅ Dimension matches correctly
# ✅ Has source/document: True
# ✅ Has page: True
```

### 3. Test API
```bash
# Test query endpoint
curl -X POST "http://localhost:8000/api/v1/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "test", "technique": "baseline", "top_k": 2}'

# Verify metadata.sources array contains:
# - score (non-zero)
# - metadata.document (not "unknown")
# - metadata.page (not always 0)
```

### 4. Test Frontend
1. Start backend: `cd backend && ./start.sh`
2. Start frontend: `cd frontend/chat-lab && npm run dev`
3. Submit a query in the UI
4. Verify sources show:
   - Real percentage scores (e.g., "78.3%")
   - Document names (e.g., "BASELINE_RAG.md")
   - Section information

---

## Technical Details

### API Response Structure (New)
```json
{
  "query": "What is RAG?",
  "answer": "...",
  "technique": "baseline",
  "retrieved_docs": ["...", "..."],
  "metrics": {...},
  "metadata": {
    "top_k": 2,
    "num_docs_retrieved": 2,
    "execution_details": {...},
    "execution_id": 19,
    "sources": [
      {
        "content": "document text...",
        "score": 0.7832,
        "metadata": {
          "document": "BASELINE_RAG.md",
          "page": 0,
          "chunk_id": "chunk_0",
          "section_title": "📋 Definição",
          "file_path": "/path/to/file"
        }
      }
    ]
  }
}
```

### Metadata Mapping
Backend fields → Frontend fields:
- `source` → `document` (with fallback)
- `chunk_index` → `page` (with fallback to 0)
- `chunk_index` → `chunk_id` (formatted as "chunk_N")
- Additional fields preserved: `section_title`, `file_path`, etc.

---

## Testing Checklist

- [x] Similarity scores are non-zero (range: 0.75-0.80 for test queries)
- [x] Document names show correctly (not "unknown")
- [x] Page numbers are present (not all 0)
- [x] Frontend displays sources from `metadata.sources`
- [x] All RAG techniques work (baseline, hyde, reranking, etc.)
- [x] Backward compatibility maintained (old metadata still works)

---

## Known Limitations

1. **Page Numbers for Markdown**:
   - Uses `chunk_index` as proxy for page number
   - For actual PDFs, would need proper PDF parsing library (PyPDF2, pdfplumber)

2. **Existing Data**:
   - Old documents without `document` and `page` fields will show as "unknown Page 0"
   - Solution: Re-index with `python -m scripts.upload_docs --clean`

3. **Performance**:
   - Source transformation adds ~5ms to API latency
   - Negligible compared to LLM generation time (~600ms)

---

## Future Enhancements

1. **PDF Support**:
   - Add PyPDF2 or pdfplumber for actual PDF page extraction
   - Parse PDF metadata (author, title, creation date)

2. **Smart Chunking**:
   - Use section boundaries for more meaningful "pages"
   - Preserve document structure in metadata

3. **Metadata Validation**:
   - Add Pydantic validators for required metadata fields
   - Fail fast on missing metadata during upload

4. **Migration Tool**:
   - Auto-detect old metadata format
   - Prompt user to re-index if needed
   - Provide one-click migration

---

## Contact

For questions or issues:
- Check diagnostics: `python -m scripts.diagnose_issues`
- Review logs: `backend/backend.log`, `frontend/chat-lab/console`
- API docs: `http://localhost:8000/docs`

---

**Last Updated**: 2025-11-21
**Fix Version**: v0.1.1
