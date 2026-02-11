import pytest
from unittest.mock import patch, MagicMock


def test_router_init():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        from src.llm.router import LLMRouter
        router = LLMRouter()
        names = [p["name"] for p in router.providers]
        assert "openai" in names


def test_router_get_stats():
    with patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"}):
        from src.llm.router import LLMRouter
        router = LLMRouter()
        stats = router.get_stats()
        assert "providers" in stats
        assert "total_requests" in stats
        assert stats["total_requests"] == 0
