import os
import json
import pytest
from src.ingestion.chunker import chunk_spec, extract_api_info, extract_endpoints


SAMPLE_SPEC = {
    "info": {
        "title": "Test API",
        "description": "A test API for unit testing",
        "version": "1.0.0",
    },
    "servers": [{"url": "https://api.test.com"}],
    "paths": {
        "/users": {
            "get": {
                "summary": "List all users",
                "description": "Returns a list of users",
                "tags": ["users"],
                "parameters": [{"name": "limit"}],
            },
            "post": {
                "summary": "Create a user",
                "description": "Creates a new user",
                "tags": ["users"],
                "parameters": [],
            },
        },
    },
}


def test_extract_api_info():
    info = extract_api_info(SAMPLE_SPEC)
    assert info["title"] == "Test API"
    assert info["description"] == "A test API for unit testing"
    assert info["version"] == "1.0.0"
    assert info["base_url"] == "https://api.test.com"


def test_extract_endpoints():
    endpoints = extract_endpoints(SAMPLE_SPEC)
    assert len(endpoints) == 2
    assert endpoints[0]["method"] == "GET"
    assert endpoints[0]["path"] == "/users"
    assert endpoints[1]["method"] == "POST"


def test_chunk_spec(tmp_path):
    spec_file = tmp_path / "test_api.json"
    spec_file.write_text(json.dumps(SAMPLE_SPEC))

    chunks = chunk_spec(str(spec_file))
    assert len(chunks) == 3  # 1 overview + 2 endpoints

    overview = chunks[0]
    assert overview["metadata"]["type"] == "overview"
    assert overview["metadata"]["api_name"] == "Test API"

    endpoint = chunks[1]
    assert endpoint["metadata"]["type"] == "endpoint"
    assert endpoint["metadata"]["method"] == "GET"


def test_chunk_spec_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.json"
    bad_file.write_text("not valid json or yaml {{{}}")

    chunks = chunk_spec(str(bad_file))
    assert chunks == []