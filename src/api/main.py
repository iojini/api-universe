import os
import time
from fastapi import FastAPI, Depends
from pydantic import BaseModel
from dotenv import load_dotenv
from src.search.semantic_search import search
from src.search.rag import ask
from src.agents.search_agent import run_agent
from src.metrics_db import get_db, get_metrics
from src.llm.router import router as llm_router
from src.api.auth import create_token, verify_token
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI(
    title="API Universe",
    description="AI-powered semantic search for API discovery",
    version="0.1.0",
)

app.add_middleware(                                  
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Track query metrics
query_log = []


class SearchRequest(BaseModel):
    query: str
    top_k: int = 5


class AskRequest(BaseModel):
    query: str
    top_k: int = 5


class AgentRequest(BaseModel):
    query: str


class TokenRequest(BaseModel):
    user_id: str


def log_query(query, endpoint, latency_ms, grounding_score=None):
    query_log.append({
        "query": query,
        "endpoint": endpoint,
        "latency_ms": latency_ms,
        "grounding_score": grounding_score,
        "timestamp": time.time(),
    })
    # Keep only last 1000 entries
    if len(query_log) > 1000:
        query_log.pop(0)


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.post("/token")
def get_token(request: TokenRequest):
    token = create_token(request.user_id)
    return {"access_token": token, "token_type": "bearer"}


@app.post("/search")
def search_endpoint(request: SearchRequest, user_id: str = Depends(verify_token)):
    start = time.time()
    results = search(request.query, top_k=request.top_k)
    latency = round((time.time() - start) * 1000)

    log_query(request.query, "/search", latency)

    return {
        "query": request.query,
        "user": user_id,
        "results": results,
        "count": len(results),
        "latency_ms": latency,
    }


@app.post("/ask")
def ask_endpoint(request: AskRequest, user_id: str = Depends(verify_token)):
    start = time.time()
    result = ask(request.query, top_k=request.top_k)
    latency = round((time.time() - start) * 1000)

    grounding_score = result.get("grounding", {}).get("score")
    log_query(request.query, "/ask", latency, grounding_score)

    result["user"] = user_id
    result["latency_ms"] = latency
    return result


@app.post("/agent")
def agent_endpoint(request: AgentRequest, user_id: str = Depends(verify_token)):
    start = time.time()
    result = run_agent(request.query)
    latency = round((time.time() - start) * 1000)

    grounding_score = result.get("grounding", {}).get("score")
    log_query(request.query, "/agent", latency, grounding_score)

    result["user"] = user_id
    result["latency_ms"] = latency

    # Update the latency in SQLite (agent logged 0, we have the real total)
    try:
        conn = get_db()
        conn.execute(
            "UPDATE agent_runs SET latency_ms = ? WHERE id = (SELECT MAX(id) FROM agent_runs)",
            (latency,)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Warning: failed to update latency in DB: {e}")

    return result


@app.get("/metrics")
def metrics(user_id: str = Depends(verify_token)):
    """Observability dashboard data from SQLite."""
    return get_metrics()