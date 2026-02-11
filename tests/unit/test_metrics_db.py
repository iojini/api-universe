import os
import pytest
import sqlite3
from unittest.mock import patch


def test_init_db(tmp_path):
    db_path = str(tmp_path / "test_metrics.db")
    with patch("src.metrics_db.DB_PATH", db_path):
        from src.metrics_db import init_db, get_db
        init_db()
        conn = sqlite3.connect(db_path)
        cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        assert "agent_runs" in tables
        conn.close()


def test_log_and_get_metrics(tmp_path):
    db_path = str(tmp_path / "test_metrics.db")
    with patch("src.metrics_db.DB_PATH", db_path):
        from src.metrics_db import init_db, log_agent_run, get_metrics
        init_db()
        log_agent_run({
            "query": "test query",
            "query_type": "COMPARE",
            "latency_ms": 5000,
            "grounding_score": 0.8,
            "tokens": 200,
            "classify_model": "gpt-5-nano",
            "classify_ms": 100,
            "decompose_model": "gpt-5-nano",
            "decompose_ms": 200,
            "retrieve_ms": 300,
            "retrieve_count": 5,
            "generate_model": "gpt-5.2-chat-latest",
            "generate_ms": 3000,
            "generate_tokens": 200,
            "verify_model": "gpt-5.2-chat-latest",
            "verify_ms": 1000,
        })
        metrics = get_metrics()
        assert metrics["summary"]["total_queries"] == 1
        assert metrics["summary"]["avg_grounding"] == 0.8
        assert len(metrics["recent_runs"]) == 1
        assert metrics["recent_runs"][0]["query"] == "test query"


def test_get_metrics_empty(tmp_path):
    db_path = str(tmp_path / "test_metrics.db")
    with patch("src.metrics_db.DB_PATH", db_path):
        from src.metrics_db import init_db, get_metrics
        init_db()
        metrics = get_metrics()
        assert metrics["summary"]["total_queries"] == 0
