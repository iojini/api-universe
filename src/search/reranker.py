from sentence_transformers import CrossEncoder

model = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


def rerank(query, results, top_k=5):
    """Re-rank search results using a cross-encoder."""
    if not results:
        return results

    pairs = [[query, r["text"]] for r in results]
    scores = model.predict(pairs)

    for i, score in enumerate(scores):
        results[i]["rerank_score"] = float(score)

    reranked = sorted(results, key=lambda r: r["rerank_score"], reverse=True)
    return reranked[:top_k]


if __name__ == "__main__":
    test_results = [
        {"text": "Send SMS messages internationally with Twilio", "metadata": {"api_name": "Twilio"}},
        {"text": "POST /login push sign-in request", "metadata": {"api_name": "Authentiq"}},
        {"text": "Create SMS transport configuration", "metadata": {"api_name": "Alerter System"}},
    ]

    query = "I need to send text messages globally"
    reranked = rerank(query, test_results)

    for i, r in enumerate(reranked):
        print(f"{i+1}. [{r['rerank_score']:.3f}] {r['metadata']['api_name']}: {r['text'][:80]}")