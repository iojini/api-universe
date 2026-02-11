import pytest
from src.api.auth import create_token, SECRET_KEY, ALGORITHM
from jose import jwt


def test_create_token_returns_string():
    token = create_token("test-user")
    assert isinstance(token, str)
    assert len(token) > 20


def test_create_token_contains_user_id():
    token = create_token("demo-user")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert payload["sub"] == "demo-user"


def test_create_token_has_expiry():
    token = create_token("test-user")
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert "exp" in payload
    assert "iat" in payload


def test_create_token_different_users():
    token1 = create_token("user-1")
    token2 = create_token("user-2")
    assert token1 != token2
    p1 = jwt.decode(token1, SECRET_KEY, algorithms=[ALGORITHM])
    p2 = jwt.decode(token2, SECRET_KEY, algorithms=[ALGORITHM])
    assert p1["sub"] == "user-1"
    assert p2["sub"] == "user-2"
