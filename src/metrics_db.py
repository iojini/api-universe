import sqlite3
import os
import time
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "metrics.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS agent_runs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            query TEXT NOT NULL,
            query_type TEXT,
            latency_ms INTEGER,
            grounding_score REAL,
            tokens INTEGER,
            classify_model TEXT,
            classify_ms INTEGER,
            decompose_model TEXT,
            decompose_ms INTEGER,
            retrieve_ms INTEGER,
            retrieve_count INTEGER,
            generate_model TEXT,
            generate_ms INTEGER,
            generate_tokens INTEGER,
            verify_model TEXT,
            verify_ms INTEGER
        )
    """)
    conn.commit()
    conn.close()

def log_agent_run(data: dict):
    conn = get_db()
    conn.execute("""
        INSERT INTO agent_runs (
            timestamp, query, query_type, latency_ms, grounding_score, tokens,
            classify_model, classify_ms, decompose_model, decompose_ms,
            retrieve_ms, retrieve_count, generate_model, generate_ms, generate_tokens,
            verify_model, verify_ms
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.utcnow().isoformat(),
        data.get("query", ""),
        data.get("query_type", ""),
        data.get("latency_ms", 0),
        data.get("grounding_score", 0),
        data.get("tokens", 0),
        data.get("classify_model", ""),
        data.get("classify_ms", 0),
        data.get("decompose_model", ""),
        data.get("decompose_ms", 0),
        data.get("retrieve_ms", 0),
        data.get("retrieve_count", 0),
        data.get("generate_model", ""),
        data.get("generate_ms", 0),
        data.get("generate_tokens", 0),
        data.get("verify_model", ""),
        data.get("verify_ms", 0),
    ))
    conn.commit()
    conn.close()

def get_metrics():
    conn = get_db()
    
    # Summary stats
    summary = conn.execute("""
        SELECT 
            COUNT(*) as total_queries,
            ROUND(AVG(latency_ms)) as avg_latency_ms,
            ROUND(AVG(grounding_score), 3) as avg_grounding,
            SUM(tokens) as total_tokens
        FROM agent_runs
    """).fetchone()
    
    # Last 10 runs for charts
    recent = conn.execute("""
        SELECT id, timestamp, query, query_type, latency_ms, grounding_score, tokens,
               classify_model, classify_ms, decompose_model, decompose_ms,
               retrieve_ms, retrieve_count, generate_model, generate_ms, generate_tokens,
               verify_model, verify_ms
        FROM agent_runs ORDER BY id DESC LIMIT 10
    """).fetchall()
    
    # Model usage stats
    model_stats = conn.execute("""
        SELECT 
            classify_model,
            COUNT(*) as classify_calls,
            ROUND(AVG(classify_ms)) as avg_classify_ms,
            generate_model,
            COUNT(*) as generate_calls,
            ROUND(AVG(generate_ms)) as avg_generate_ms,
            ROUND(AVG(verify_ms)) as avg_verify_ms
        FROM agent_runs
        GROUP BY classify_model, generate_model
    """).fetchall()
    
    conn.close()
    
    return {
        "summary": {
            "total_queries": summary["total_queries"] or 0,
            "avg_latency_ms": summary["avg_latency_ms"] or 0,
            "avg_grounding": summary["avg_grounding"] or 0,
            "total_tokens": summary["total_tokens"] or 0,
        },
        "recent_runs": [dict(r) for r in recent],
        "model_stats": [dict(r) for r in model_stats],
    }

# Initialize on import
init_db()
