# ◆ API Universe

**AI-powered semantic search platform for API discovery and knowledge retrieval.**

Developers describe what they need in plain English, and API Universe finds, compares, and explains the best APIs — with grounded citations and hallucination mitigation.

---

## Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                        FastAPI Service                       │
│                  JWT Auth · Rate Limiting                     │
├──────────┬──────────┬───────────┬───────────┬───────────────┤
│ /search  │  /ask    │  /agent   │ /metrics  │   /token      │
└────┬─────┴────┬─────┴─────┬─────┴─────┬─────┴───────────────┘
     │          │           │           │
     ▼          ▼           ▼           ▼
┌─────────┐ ┌─────────┐ ┌──────────┐ ┌──────────────────────┐
│Semantic │ │  RAG    │ │LangGraph │ │  Observability       │
│Search   │ │Pipeline │ │  Agent   │ │  Query Logs          │
│         │ │         │ │          │ │  Latency Tracking    │
│ FAISS   │ │ Search  │ │Classify  │ │  Grounding Scores    │
│ pgvector│ │ Ground  │ │Decompose │ │  LLM Routing Stats   │
│         │ │ Generate│ │Retrieve  │ │                      │
│         │ │ Verify  │ │Generate  │ │                      │
│         │ │         │ │Verify    │ │                      │
└─────────┘ └─────────┘ └──────────┘ └──────────────────────┘
     │          │           │
     ▼          ▼           ▼
┌─────────────────────────────────────────────────────────────┐
│              Multi-Cloud LLM Router                          │
│        OpenAI ──► Azure OpenAI ──► AWS Bedrock               │
│          Fault-tolerant fallback · Latency tracking          │
└─────────────────────────────────────────────────────────────┘
     │
     ▼
┌─────────────────────────────────────────────────────────────┐
│                   Data Layer                                  │
│  FAISS Index · Embeddings (text-embedding-3-large)           │
│  2,705 chunks from 100+ API specs (APIs.guru)                │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

- **Semantic Search** — Natural language queries against 2,705+ indexed API chunks using FAISS and OpenAI embeddings
- **RAG Pipeline** — Retrieval-Augmented Generation with grounded citations and hallucination verification
- **LangGraph Agent** — Multi-step reasoning with query classification, decomposition, and parallel retrieval
- **Grounding Checker** — Every response is verified claim-by-claim against source documents
- **Multi-Cloud LLM Router** — Automatic failover across OpenAI, Azure OpenAI, and AWS Bedrock
- **JWT Authentication** — Secure API access with token-based auth
- **Evaluation Framework** — Golden dataset with Precision@K, hit rate, and latency tracking
- **Observability** — Real-time metrics endpoint with query logs, grounding scores, and routing stats

---

## Quick Start
```bash
# Clone and setup
git clone https://github.com/YOUR_USERNAME/api-universe.git
cd api-universe
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Add your OPENAI_API_KEY to .env

# Ingest API specs
python3 src/ingestion/download_specs.py
python3 src/ingestion/chunker.py
python3 src/ingestion/embed.py
python3 src/search/vector_store.py

# Run the server
uvicorn src.api.main:app --reload --port 8000

# Open docs
# http://127.0.0.1:8000/docs
```

---

## API Endpoints

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/health` | GET | No | Health check |
| `/token` | POST | No | Generate JWT token |
| `/search` | POST | JWT | Semantic search across API specs |
| `/ask` | POST | JWT | RAG-powered question answering |
| `/agent` | POST | JWT | Multi-step agent for complex queries |
| `/metrics` | GET | JWT | Observability dashboard data |

---

## Evaluation Results

| Stage | Specs | Vectors | Precision@5 | Hit Rate@3 | Avg Latency |
|-------|-------|---------|-------------|------------|-------------|
| Baseline (no rerank) | 100 | 2,705 | 0.486 | 0.75 | 513ms |
| + Re-ranking | 500 | 16,877 | 0.56 | 0.70 | 2,225ms |
| Full scale | 2,529 | 125,655 | **0.738** | **0.80** | 2,378ms |

*52% Precision@5 improvement from baseline to full scale through cross-encoder re-ranking, dataset scaling, and adaptive chunking.*

---

## Tech Stack

- **Language:** Python
- **API Framework:** FastAPI
- **LLMs:** GPT-5.2, OpenAI Embeddings (text-embedding-3-large)
- **Orchestration:** LangChain, LangGraph
- **Vector Store:** FAISS, pgvector
- **Auth:** JWT (python-jose)
- **Cloud:** AWS (Lambda, ECS Fargate, API Gateway)
- **CI/CD:** GitHub Actions, Docker
- **Observability:** Custom metrics, LangSmith (planned)

---

## Project Structure
```
api-universe/
├── src/
│   ├── api/            # FastAPI service, auth
│   ├── agents/         # LangGraph search agent
│   ├── ingestion/      # Download, chunk, embed pipeline
│   ├── llm/            # Multi-cloud LLM router
│   ├── search/         # Semantic search, RAG, grounding
│   └── evaluation/     # Eval framework, golden dataset
├── tests/              # Unit and integration tests
├── data/               # Raw specs and processed indexes
├── infrastructure/     # Cloud deployment configs
├── docs/adr/           # Architecture Decision Records
├── frontend/           # UI (planned)
├── Dockerfile
├── requirements.txt
└── .github/workflows/  # CI/CD pipeline
```

---

## License

MIT