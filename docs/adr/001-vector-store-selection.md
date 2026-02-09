# ADR 001: Vector Store Selection — FAISS + pgvector

## Status
Accepted

## Context
We need a vector database to store and search embeddings for 5,000+ API specifications. Key requirements:
- Sub-second similarity search at scale
- Low operational overhead during development
- Path to production-grade persistence
- Cost-effective for a portfolio project

Options considered:
1. **FAISS** — Facebook's in-memory vector search library
2. **pgvector** — PostgreSQL extension for vector similarity
3. **Pinecone** — Managed vector database SaaS
4. **Weaviate** — Open-source vector database

## Decision
Use **FAISS as the primary local index** with **pgvector as the production persistence layer**.

## Rationale

### Why FAISS for development
- Zero infrastructure — runs in-process, no external services
- Extremely fast for datasets under 100K vectors
- Well-documented, battle-tested at Meta scale
- Free

### Why pgvector for production
- Leverages existing PostgreSQL infrastructure
- ACID transactions for metadata alongside vectors
- No additional managed service cost
- Supports exact and approximate nearest neighbor search

### Why not Pinecone
- Adds vendor dependency and monthly cost
- Overkill for our dataset size (<100K vectors)
- Less control over indexing and search parameters
- Would complicate local development

### Why not Weaviate
- Additional infrastructure to manage
- Heavier than needed for our use case
- pgvector covers our persistence needs within existing PostgreSQL

## Consequences
- Local development uses FAISS file-based index (fast, simple)
- Production deployment uses pgvector in RDS PostgreSQL
- Migration path is straightforward: same embeddings, different storage backend
- We accept that FAISS index must be rebuilt on data changes (acceptable at our scale)