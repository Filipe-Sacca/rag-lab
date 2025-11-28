# RAG Lab Database - Quick Reference

## Installation

```bash
pip install sqlalchemy==2.0.23 alembic==1.13.1
```

## Database Location

```
/root/Filipe/Teste-Claude/rag-lab/backend/rag_lab.db
```

## Quick Start

### 1. Initialize Database

Automatic on app startup or manual:

```python
from db import init_db
init_db()
```

### 2. Use in FastAPI Endpoint

```python
from fastapi import Depends
from sqlalchemy.orm import Session
from db import get_db
from db.helpers import save_rag_result

@router.post("/query")
async def query_rag(request: QueryRequest, db: Session = Depends(get_db)):
    result = await baseline_rag(request.query)
    execution_id = save_rag_result(db, result, technique="baseline")
    return result
```

### 3. Query Executions

```python
from db import SessionLocal, get_executions, get_technique_statistics

db = SessionLocal()

# Get recent executions
executions = get_executions(db, limit=10)

# Get statistics
stats = get_technique_statistics(db, technique="baseline", days=7)

db.close()
```

## Common API Calls

```bash
# Health check
curl http://localhost:8000/api/v1/db/health

# Get execution by ID
curl http://localhost:8000/api/v1/db/executions/1

# List recent executions
curl "http://localhost:8000/api/v1/db/executions?limit=10"

# Filter by technique
curl "http://localhost:8000/api/v1/db/executions?technique=baseline"

# Last 24 hours
curl "http://localhost:8000/api/v1/db/executions?hours=24"

# Statistics (all techniques)
curl "http://localhost:8000/api/v1/db/statistics?days=7"

# Statistics (single technique)
curl "http://localhost:8000/api/v1/db/statistics/technique/baseline?days=7"

# Compare techniques
curl "http://localhost:8000/api/v1/db/statistics/comparison?techniques=baseline&techniques=hyde"

# Timeline data
curl "http://localhost:8000/api/v1/db/analytics/timeline?hours=24"
```

## Useful Queries

```python
from db import SessionLocal, get_executions_by_technique, get_recent_executions

db = SessionLocal()

# Baseline executions only
baseline = get_executions_by_technique(db, "baseline", limit=50)

# Last hour
last_hour = get_recent_executions(db, hours=1, limit=100)

# Last 7 days with date filter
from datetime import datetime, timedelta
start = datetime.utcnow() - timedelta(days=7)
week = get_executions(db, start_date=start, limit=1000)

db.close()
```

## Database Schema

### rag_executions
- `id` (PK)
- `query_text`
- `answer_text`
- `technique_name` (indexed)
- `top_k`
- `namespace` (indexed)
- `sources` (JSON)
- `execution_details` (JSON)
- `metadata` (JSON)
- `created_at` (indexed)

### rag_metrics (1-to-1 with executions)
- `id` (PK)
- `execution_id` (FK, unique)
- `latency_ms`, `latency_seconds`
- `tokens_input`, `tokens_output`, `tokens_total`
- `cost_input_usd`, `cost_output_usd`, `cost_total_usd`
- `context_precision`, `context_recall`, `faithfulness`, `answer_relevancy`
- `chunks_retrieved`

## CRUD Functions

```python
from db.crud import (
    create_execution,           # Save new execution
    get_execution,              # Get by ID
    get_executions,             # List with filters
    get_executions_by_technique,# Filter by technique
    get_recent_executions,      # Last N hours
    get_technique_statistics,   # Aggregated stats
    delete_old_executions,      # Cleanup
)
```

## Statistics Response Format

```json
{
    "technique": "baseline",
    "total_executions": 50,
    "latency": {
        "avg_ms": 850.5,
        "min_ms": 600.0,
        "max_ms": 1200.0
    },
    "cost": {
        "avg_usd": 0.002,
        "total_usd": 0.10
    },
    "tokens": {
        "avg": 1500,
        "total": 75000
    },
    "quality": {
        "context_precision": 0.85,
        "context_recall": 0.78,
        "faithfulness": 0.92,
        "answer_relevancy": 0.88
    },
    "period_days": 7
}
```

## Maintenance

```python
from db import reset_database, check_database_health
from db.crud import delete_old_executions

# Health check
health = check_database_health()
print(health["status"])

# Delete old data (90 days)
db = SessionLocal()
deleted = delete_old_executions(db, days=90)
db.close()

# Complete reset (WARNING: deletes all data)
reset_database()
```

## Examples & Tests

```bash
# Run examples
python examples/database_usage.py

# Run tests
pytest tests/test_database.py -v
```

## Troubleshooting

**Database locked**: Use context managers, enable WAL mode (automatic)

**Reset database**:
```bash
rm rag_lab.db
python -c "from db import init_db; init_db()"
```

**Check health**:
```python
from db import check_database_health
print(check_database_health())
```

## Environment

- **SQLAlchemy**: 2.0.23+
- **Database**: SQLite with WAL mode
- **Location**: `backend/rag_lab.db`
- **API Prefix**: `/api/v1/db`

## Full Documentation

See `DATABASE_README.md` for complete documentation.
