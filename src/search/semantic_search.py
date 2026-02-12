import os
import json
import numpy as np
import faiss
from openai import OpenAI
from dotenv import load_dotenv
from src.search.reranker import rerank

load_dotenv()
client = OpenAI()

EMBEDDING_MODEL = os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-large")
INDEX_PATH = "data/processed/faiss_index.bin"
METADATA_PATH = "data/processed/metadata.json"

# Load index and metadata once
index = faiss.read_index(INDEX_PATH)
with open(METADATA_PATH, "r") as f:
    metadata = json.load(f)


def search(query, top_k=5, use_reranker=True):
    """Search the vector store with a natural language query."""
    # Retrieve more candidates for re-ranking
    retrieve_k = top_k * 5 if use_reranker else top_k

    response = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[query],
    )
    query_embedding = np.array([response.data[0].embedding], dtype="float32")
    faiss.normalize_L2(query_embedding)

    scores, indices = index.search(query_embedding, retrieve_k)

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            continue
        result = metadata[idx].copy()
        result["score"] = float(score)
        results.append(result)

    if use_reranker and results:
        results = rerank(query, results, top_k=top_k * 2)

    # Deduplicate by API name, keeping highest score
    seen = set()
    deduped = []
    for r in results:
        name = r.get("metadata", {}).get("api_name", "")
        if name not in seen:
            seen.add(name)
            deduped.append(r)
    results = deduped

    return results[:top_k]


if __name__ == "__main__":
    query = "I need an API to send SMS messages internationally"
    print(f"Query: {query}\n")

    print("WITH re-ranking:")
    results = search(query, top_k=5, use_reranker=True)
    for i, r in enumerate(results):
        print(f"  {i+1}. [{r.get('rerank_score', 0):.3f}] {r['metadata']['api_name']}")
        print(f"     {r['text'][:100]}")

    print("\nWITHOUT re-ranking:")
    results = search(query, top_k=5, use_reranker=False)
    for i, r in enumerate(results):
        print(f"  {i+1}. [{r['score']:.3f}] {r['metadata']['api_name']}")
        print(f"     {r['text'][:100]}")