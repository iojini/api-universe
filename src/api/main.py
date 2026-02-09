import os
import time
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from dotenv import load_dotenv
from src.search.semantic_search import search
from src.search.rag import ask

load_dotenv()

app = FastAPI(
    title="API Universe",
    description="AI-powered semantic search for API discovery",
    version="0.1.0",
)


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class AskRequest(BaseModel):
    query: str
    top_k: int = 5


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/search")
def search_endpoint(request: SearchRequest):
    start = time.time()
    results = search(request.query, top_k=request.top_k)
    latency = time.time() - start

    return {
        "query": request.query,
        "results": results,
        "count": len(results),
        "latency_ms": round(latency * 1000),
    }


@app.post("/ask")
def ask_endpoint(request: AskRequest):
    start = time.time()
    result = ask(request.query, top_k=request.top_k)
    latency = time.time() - start
    result["latency_ms"] = round(latency * 1000)

    return result