# RAG Lab - Useful Database Queries

Collection of SQL and Python queries for common analytics tasks.

## Direct SQL Queries

Use these with `sqlite3` CLI or database tools.

### Basic Statistics

```sql
-- Count executions by technique
SELECT
    technique_name,
    COUNT(*) as total_executions,
    AVG(latency_ms) as avg_latency_ms,
    MIN(latency_ms) as min_latency_ms,
    MAX(latency_ms) as max_latency_ms
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
GROUP BY technique_name
ORDER BY total_executions DESC;

-- Daily execution count
SELECT
    DATE(created_at) as date,
    COUNT(*) as executions,
    AVG(latency_ms) as avg_latency_ms
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
WHERE created_at >= datetime('now', '-30 days')
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Cost analysis by technique
SELECT
    technique_name,
    COUNT(*) as executions,
    SUM(cost_total_usd) as total_cost_usd,
    AVG(cost_total_usd) as avg_cost_usd,
    SUM(tokens_total) as total_tokens
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
GROUP BY technique_name
ORDER BY total_cost_usd DESC;
```

### Performance Analysis

```sql
-- Slowest executions
SELECT
    e.id,
    e.technique_name,
    e.query_text,
    m.latency_ms,
    m.tokens_total,
    e.created_at
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
ORDER BY m.latency_ms DESC
LIMIT 10;

-- Fastest executions by technique
SELECT
    technique_name,
    MIN(latency_ms) as fastest_ms,
    query_text as fastest_query
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
GROUP BY technique_name;

-- Latency distribution (buckets)
SELECT
    CASE
        WHEN latency_ms < 500 THEN '0-500ms'
        WHEN latency_ms < 1000 THEN '500-1000ms'
        WHEN latency_ms < 2000 THEN '1000-2000ms'
        ELSE '2000ms+'
    END as latency_bucket,
    COUNT(*) as count,
    AVG(latency_ms) as avg_latency
FROM rag_metrics
GROUP BY latency_bucket
ORDER BY MIN(latency_ms);
```

### Cost Tracking

```sql
-- Total cost by day
SELECT
    DATE(created_at) as date,
    SUM(cost_total_usd) as total_cost_usd,
    COUNT(*) as executions,
    AVG(cost_total_usd) as avg_cost_per_query
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
WHERE created_at >= datetime('now', '-30 days')
GROUP BY DATE(created_at)
ORDER BY date DESC;

-- Most expensive techniques
SELECT
    technique_name,
    COUNT(*) as executions,
    SUM(cost_total_usd) as total_cost,
    AVG(cost_total_usd) as avg_cost,
    MAX(cost_total_usd) as max_cost
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
GROUP BY technique_name
ORDER BY total_cost DESC;

-- Cost per 1000 tokens by technique
SELECT
    technique_name,
    AVG(cost_total_usd / (tokens_total / 1000.0)) as cost_per_1k_tokens,
    COUNT(*) as samples
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
WHERE tokens_total > 0
GROUP BY technique_name;
```

### Quality Metrics

```sql
-- Average quality scores by technique
SELECT
    technique_name,
    COUNT(*) as executions,
    AVG(context_precision) as avg_precision,
    AVG(context_recall) as avg_recall,
    AVG(faithfulness) as avg_faithfulness,
    AVG(answer_relevancy) as avg_relevancy
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
WHERE context_precision IS NOT NULL
GROUP BY technique_name;

-- Low quality executions (for review)
SELECT
    e.id,
    e.technique_name,
    e.query_text,
    m.context_precision,
    m.context_recall,
    m.faithfulness,
    m.answer_relevancy
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
WHERE
    (context_precision < 0.7 OR
     context_recall < 0.7 OR
     faithfulness < 0.8 OR
     answer_relevancy < 0.7)
    AND context_precision IS NOT NULL
ORDER BY context_precision ASC
LIMIT 20;

-- Quality vs Latency correlation
SELECT
    technique_name,
    AVG(context_precision) as avg_precision,
    AVG(latency_ms) as avg_latency,
    COUNT(*) as samples
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
WHERE context_precision IS NOT NULL
GROUP BY technique_name;
```

### Time-Based Analysis

```sql
-- Hourly patterns (when are queries made?)
SELECT
    strftime('%H', created_at) as hour,
    COUNT(*) as executions,
    AVG(latency_ms) as avg_latency
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
GROUP BY hour
ORDER BY hour;

-- Last 24 hours timeline
SELECT
    strftime('%Y-%m-%d %H:00', created_at) as hour,
    COUNT(*) as executions,
    AVG(latency_ms) as avg_latency,
    SUM(cost_total_usd) as total_cost
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
WHERE created_at >= datetime('now', '-24 hours')
GROUP BY hour
ORDER BY hour DESC;

-- Week-over-week comparison
SELECT
    technique_name,
    COUNT(*) as executions_this_week,
    AVG(latency_ms) as avg_latency_this_week
FROM rag_executions e
JOIN rag_metrics m ON e.id = m.execution_id
WHERE created_at >= datetime('now', '-7 days')
GROUP BY technique_name;
```

## Python Queries

Use these with SQLAlchemy session.

### Custom Aggregations

```python
from sqlalchemy import func, case
from db import SessionLocal, RAGExecution, RAGMetric

db = SessionLocal()

# Latency percentiles
from sqlalchemy import func

result = db.query(
    RAGExecution.technique_name,
    func.count(RAGMetric.id).label('count'),
    func.avg(RAGMetric.latency_ms).label('avg_latency'),
    func.percentile_cont(0.5).within_group(RAGMetric.latency_ms).label('median_latency'),
    func.percentile_cont(0.95).within_group(RAGMetric.latency_ms).label('p95_latency'),
).join(RAGMetric).group_by(RAGExecution.technique_name).all()

for row in result:
    print(f"{row.technique_name}:")
    print(f"  Count: {row.count}")
    print(f"  Avg: {row.avg_latency:.2f}ms")
    print(f"  Median: {row.median_latency:.2f}ms")
    print(f"  P95: {row.p95_latency:.2f}ms")

db.close()
```

### Cost Analysis

```python
from datetime import datetime, timedelta

db = SessionLocal()

# Daily cost breakdown
start_date = datetime.utcnow() - timedelta(days=7)

daily_costs = (
    db.query(
        func.date(RAGExecution.created_at).label('date'),
        RAGExecution.technique_name,
        func.sum(RAGMetric.cost_total_usd).label('total_cost'),
        func.count(RAGExecution.id).label('executions'),
    )
    .join(RAGMetric)
    .filter(RAGExecution.created_at >= start_date)
    .group_by(func.date(RAGExecution.created_at), RAGExecution.technique_name)
    .order_by(func.date(RAGExecution.created_at).desc())
    .all()
)

for row in daily_costs:
    print(f"{row.date} - {row.technique_name}: ${row.total_cost:.4f} ({row.executions} queries)")

db.close()
```

### Query Pattern Analysis

```python
# Most common query patterns (first 3 words)
db = SessionLocal()

executions = db.query(RAGExecution.query_text).all()

from collections import Counter

patterns = Counter()
for exec in executions:
    # Extract first 3 words
    words = exec.query_text.split()[:3]
    pattern = ' '.join(words)
    patterns[pattern] += 1

print("Most common query patterns:")
for pattern, count in patterns.most_common(10):
    print(f"  {pattern}: {count}")

db.close()
```

### Performance Outliers

```python
# Find performance outliers (>2 std deviations from mean)
from sqlalchemy import func
import statistics

db = SessionLocal()

# Get all latencies for a technique
technique = "baseline"
latencies = (
    db.query(RAGMetric.latency_ms)
    .join(RAGExecution)
    .filter(RAGExecution.technique_name == technique)
    .all()
)

latency_values = [l[0] for l in latencies]
mean = statistics.mean(latency_values)
std = statistics.stdev(latency_values)

print(f"Mean: {mean:.2f}ms, Std Dev: {std:.2f}ms")
print(f"Outlier threshold: {mean + 2*std:.2f}ms")

# Find outliers
outliers = (
    db.query(RAGExecution, RAGMetric)
    .join(RAGMetric)
    .filter(
        RAGExecution.technique_name == technique,
        RAGMetric.latency_ms > mean + 2*std
    )
    .all()
)

print(f"\nFound {len(outliers)} outliers:")
for exec, metric in outliers:
    print(f"  ID {exec.id}: {metric.latency_ms:.2f}ms - {exec.query_text[:50]}")

db.close()
```

### Comparative Analysis

```python
# Compare techniques across multiple dimensions
from db import get_technique_statistics

db = SessionLocal()

techniques = ["baseline", "hyde", "reranking"]
comparison = {}

for technique in techniques:
    stats = get_technique_statistics(db, technique=technique, days=7)
    if stats.get("total_executions", 0) > 0:
        comparison[technique] = {
            "latency": stats["latency"]["avg_ms"],
            "cost": stats["cost"]["avg_usd"],
            "quality": stats.get("quality", {}).get("context_precision"),
        }

# Print comparison table
print(f"{'Technique':<15} {'Latency (ms)':<15} {'Cost (USD)':<15} {'Precision':<10}")
print("-" * 60)
for technique, data in comparison.items():
    print(
        f"{technique:<15} "
        f"{data['latency']:<15.2f} "
        f"{data['cost']:<15.6f} "
        f"{data['quality'] or 'N/A':<10}"
    )

db.close()
```

### Export to CSV

```python
import csv
from db import SessionLocal, get_executions

db = SessionLocal()

# Export last 1000 executions to CSV
executions = get_executions(db, limit=1000)

with open('executions_export.csv', 'w', newline='') as f:
    writer = csv.writer(f)

    # Header
    writer.writerow([
        'ID', 'Query', 'Technique', 'Latency (ms)',
        'Cost (USD)', 'Tokens', 'Created At'
    ])

    # Data
    for exec in executions:
        writer.writerow([
            exec.id,
            exec.query_text[:100],  # Truncate long queries
            exec.technique_name,
            exec.metrics.latency_ms if exec.metrics else None,
            exec.metrics.cost_total_usd if exec.metrics else None,
            exec.metrics.tokens_total if exec.metrics else None,
            exec.created_at,
        ])

print(f"Exported {len(executions)} executions to executions_export.csv")
db.close()
```

### Real-Time Monitoring

```python
# Monitor recent activity
import time
from datetime import datetime, timedelta

db = SessionLocal()

print("Real-time execution monitor (Ctrl+C to stop)")
print("-" * 80)

last_check = datetime.utcnow()

while True:
    time.sleep(5)  # Check every 5 seconds

    # Get new executions since last check
    new_executions = (
        db.query(RAGExecution, RAGMetric)
        .join(RAGMetric)
        .filter(RAGExecution.created_at > last_check)
        .all()
    )

    for exec, metric in new_executions:
        print(
            f"[{exec.created_at.strftime('%H:%M:%S')}] "
            f"{exec.technique_name:<10} "
            f"{metric.latency_ms:>7.2f}ms "
            f"${metric.cost_total_usd:.6f} "
            f"- {exec.query_text[:40]}"
        )

    last_check = datetime.utcnow()
    db.commit()  # Refresh session
```

## CLI Commands

### Using sqlite3 CLI

```bash
# Open database
sqlite3 /root/Filipe/Teste-Claude/rag-lab/backend/rag_lab.db

# Quick queries
.tables                              # List tables
.schema rag_executions               # View schema
SELECT COUNT(*) FROM rag_executions; # Total count
SELECT technique_name, COUNT(*) FROM rag_executions GROUP BY technique_name;

# Export to CSV
.headers on
.mode csv
.output executions.csv
SELECT * FROM rag_executions LIMIT 1000;
.output stdout

# Pretty formatting
.mode column
.headers on
SELECT * FROM rag_executions LIMIT 10;
```

### Using Python REPL

```bash
python

>>> from db import SessionLocal, get_executions, get_technique_statistics
>>> db = SessionLocal()

>>> # Quick stats
>>> stats = get_technique_statistics(db, technique="baseline", days=7)
>>> print(f"Avg latency: {stats['latency']['avg_ms']}ms")

>>> # Recent executions
>>> recent = get_executions(db, limit=5)
>>> for e in recent:
...     print(f"{e.technique_name}: {e.query_text[:30]}")

>>> db.close()
```

## Analytics Recipes

### Daily Report

```python
from datetime import datetime, timedelta
from db import SessionLocal, get_technique_statistics

def daily_report():
    db = SessionLocal()

    print("=" * 80)
    print(f"RAG Lab Daily Report - {datetime.utcnow().date()}")
    print("=" * 80)

    techniques = ["baseline", "hyde", "reranking", "agentic"]

    for technique in techniques:
        stats = get_technique_statistics(db, technique=technique, days=1)

        if stats.get("total_executions", 0) > 0:
            print(f"\n{technique.upper()}:")
            print(f"  Executions: {stats['total_executions']}")
            print(f"  Avg Latency: {stats['latency']['avg_ms']:.2f}ms")
            print(f"  Total Cost: ${stats['cost']['total_usd']:.4f}")
            print(f"  Total Tokens: {stats['tokens']['total']:,}")

    db.close()

daily_report()
```

### Technique Recommendation

```python
def recommend_technique(quality_threshold=0.8, latency_threshold=1000, cost_threshold=0.005):
    """Recommend best technique based on criteria"""
    db = SessionLocal()

    techniques = ["baseline", "hyde", "reranking", "agentic"]
    scores = {}

    for technique in techniques:
        stats = get_technique_statistics(db, technique=technique, days=7)

        if stats.get("total_executions", 0) < 10:
            continue  # Need more data

        # Simple scoring (lower is better)
        score = 0
        latency = stats["latency"]["avg_ms"]
        cost = stats["cost"]["avg_usd"]
        quality = stats.get("quality", {}).get("context_precision", 0.5)

        # Weighted score
        score += (latency / latency_threshold) * 0.4  # 40% weight
        score += (cost / cost_threshold) * 0.3        # 30% weight
        score += (1 - quality) * 0.3                  # 30% weight

        scores[technique] = {
            "score": score,
            "latency": latency,
            "cost": cost,
            "quality": quality,
        }

    # Sort by score
    ranked = sorted(scores.items(), key=lambda x: x[1]["score"])

    print("Technique Recommendations (best to worst):")
    for i, (technique, data) in enumerate(ranked, 1):
        print(f"{i}. {technique}:")
        print(f"   Score: {data['score']:.3f}")
        print(f"   Latency: {data['latency']:.2f}ms")
        print(f"   Cost: ${data['cost']:.6f}")
        print(f"   Quality: {data['quality']:.3f}")

    db.close()

    return ranked[0][0] if ranked else None

recommend_technique()
```

---

For more query examples, see:
- `DATABASE_README.md` - Advanced queries section
- `examples/database_usage.py` - Python examples
- `tests/test_database.py` - Test queries
