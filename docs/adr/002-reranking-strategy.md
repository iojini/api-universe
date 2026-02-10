# ADR 002: Cross-Encoder Re-Ranking Strategy

## Status
Accepted

## Context
Initial semantic search using FAISS with cosine similarity returned relevant but imprecisely ranked results. With 125,655 vectors from 2,529 API specs, the top-K results often included loosely related chunks that diluted answer quality in the RAG pipeline.

We needed a re-ranking layer to improve precision without adding API costs.

Options considered:
1. **Cross-encoder re-ranking** (local model)
2. **Cohere Rerank API** (managed service)
3. **LLM-based re-ranking** (use GPT to score relevance)
4. **No re-ranking** (rely on embedding similarity alone)

## Decision
Use a local **cross-encoder model** (ms-marco-MiniLM-L-6-v2) to re-rank the top 25 FAISS results down to the final top 5.

## Rationale

### Why cross-encoder re-ranking
- Runs locally — zero API cost per query
- Adds ~200ms latency, acceptable for our use case
- Dramatically improves precision by scoring query-document pairs jointly
- Well-established model with strong benchmark performance on MS MARCO

### Why not Cohere Rerank
- Adds vendor dependency and per-query cost
- Requires network call, adding latency and a failure point
- Cross-encoder achieves comparable quality for our dataset size

### Why not LLM-based re-ranking
- Expensive: each re-ranking call would cost ~$0.01-0.05
- Slow: adds 1-2 seconds per query
- Overkill when cross-encoder handles the task effectively

### Pipeline design
1. FAISS retrieves top 25 candidates (5x the final K)
2. Cross-encoder scores each (query, document) pair
3. Results sorted by cross-encoder score, top 5 returned

## Results

| Metric | Without Re-ranking | With Re-ranking |
|--------|-------------------|-----------------|
| Avg Precision@5 | 0.486 | 0.738 |
| Hit Rate@3 | 0.75 | 0.80 |
| Avg Latency | 513ms | 2,378ms |

## Consequences
- Requires ~500MB RAM for the cross-encoder model
- First query has cold-start delay (~2s) while model loads
- Latency increased but remains under 3 seconds
- Precision improvement of 52% justifies the tradeoff
- Model runs on CPU; GPU would reduce latency further