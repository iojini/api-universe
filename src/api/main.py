import os
import time
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from src.search.semantic_search import search
from src.search.rag import ask
from src.api.auth import create_token, verify_token

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


class TokenRequest(BaseModel):
    user_id: str


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/token")
def get_token(request: TokenRequest):
    """Generate a JWT token for testing."""
    token = create_token(request.user_id)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/search")
def search_endpoint(request: SearchRequest, user_id: str = Depends(verify_token)):
    start = time.time()
    results = search(request.query, top_k=request.top_k)
    latency = time.time() - start

    return {
        "query": request.query,
        "user": user_id,
        "results": results,
        "count": len(results),
        "latency_ms": round(latency * 1000),
    }


@app.post("/ask")
def ask_endpoint(request: AskRequest, user_id: str = Depends(verify_token)):
    start = time.time()
    result = ask(request.query, top_k=request.top_k)
    latency = time.time() - start
    result["user"] = user_id
    result["latency_ms"] = round(latency * 1000)

    return result