#!/usr/bin/env python3
"""
Export RAG test results from database to CSV
Usage: python export_results.py
"""

import sqlite3
import csv
import json
from pathlib import Path
from typing import List, Dict, Any

def get_test_results() -> List[Dict[str, Any]]:
    """Extract test results from database"""
    db_path = Path(__file__).parent / "backend" / "rag_lab.db"

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Query all executions with metrics
    cursor.execute("""
        SELECT
            id,
            query,
            technique,
            metrics,
            created_at
        FROM rag_executions
        ORDER BY created_at
    """)

    results = []
    for row in cursor.fetchall():
        exec_id, query, technique, metrics_json, created_at = row

        # Parse metrics JSON
        metrics = json.loads(metrics_json) if metrics_json else {}

        # Extract scores from sources (if available)
        scores = []
        if 'sources' in metrics:
            for source in metrics.get('sources', []):
                if 'score' in source:
                    scores.append(source['score'])

        results.append({
            'id': exec_id,
            'query': query,
            'technique': technique,
            'latency_ms': metrics.get('latency_ms', metrics.get('retrieval_latency_ms', 0)),
            'num_sources': metrics.get('num_sources', len(metrics.get('sources', []))),
            'score_min': min(scores) if scores else None,
            'score_max': max(scores) if scores else None,
            'score_avg': sum(scores) / len(scores) if scores else None,
            'created_at': created_at
        })

    conn.close()
    return results

def export_to_csv(results: List[Dict[str, Any]], output_file: str = "TESTE_RESULTS.csv"):
    """Export results to CSV"""
    output_path = Path(__file__).parent / output_file

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Teste', 'Pergunta', 'Técnica',
            'Latência_ms', 'Num_Sources',
            'Score_Min', 'Score_Max', 'Score_Avg',
            'Qualidade_1a5', 'Relevância_1a5', 'Observações'
        ])

        # Data rows
        for i, result in enumerate(results, 1):
            # Shorten query for readability
            query_short = result['query'][:50] + "..." if len(result['query']) > 50 else result['query']

            writer.writerow([
                i,
                query_short,
                result['technique'],
                f"{result['latency_ms']:.2f}" if result['latency_ms'] else '',
                result['num_sources'],
                f"{result['score_min']:.4f}" if result['score_min'] else '',
                f"{result['score_max']:.4f}" if result['score_max'] else '',
                f"{result['score_avg']:.4f}" if result['score_avg'] else '',
                '',  # Qualidade (manual)
                '',  # Relevância (manual)
                ''   # Observações (manual)
            ])

    print(f"✅ Results exported to: {output_path}")
    print(f"📊 Total tests: {len(results)}")

def print_summary(results: List[Dict[str, Any]]):
    """Print summary statistics"""
    from collections import defaultdict

    by_technique = defaultdict(list)
    for result in results:
        by_technique[result['technique']].append(result['latency_ms'])

    print("\n📈 Summary by Technique:")
    print("-" * 60)
    for technique, latencies in sorted(by_technique.items()):
        valid_latencies = [l for l in latencies if l]
        if valid_latencies:
            avg = sum(valid_latencies) / len(valid_latencies)
            print(f"{technique:12} | Tests: {len(latencies):2} | Avg Latency: {avg:7.2f}ms")
    print("-" * 60)

def main():
    print("🔍 Extracting test results from database...")
    results = get_test_results()

    if not results:
        print("⚠️  No test results found in database")
        print("💡 Run some tests in the frontend first!")
        return

    print_summary(results)
    export_to_csv(results)

    print("\n📝 Next steps:")
    print("1. Open TESTE_RESULTS.csv in Excel/Google Sheets")
    print("2. Fill in 'Qualidade_1a5' and 'Relevância_1a5' columns manually")
    print("3. Add observations in 'Observações' column")
    print("4. Use for final analysis!")

if __name__ == "__main__":
    main()
