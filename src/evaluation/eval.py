import os
import json
import time
from src.search.semantic_search import search
from src.search.rag import ask


GOLDEN_DATASET_PATH = "data/processed/golden_dataset.json"
EVAL_RESULTS_PATH = "data/processed/eval_results.json"


def create_sample_golden_dataset():
    """Create a starter golden dataset for evaluation."""
    dataset = [
        {"query": "API for strong authentication without passwords", "expected_api": "Authentiq", "expected_type": "overview"},
        {"query": "push sign-in login endpoint", "expected_api": "Authentiq", "expected_type": "endpoint"},
        {"query": "SMS transport configuration", "expected_api": "Alerter System", "expected_type": "endpoint"},
        {"query": "1Password secrets management REST API", "expected_api": "1Password", "expected_type": "overview"},
        {"query": "payment processing checkout", "expected_api": "Adyen", "expected_type": "endpoint"},
        {"query": "IP address geolocation lookup", "expected_api": "geolocation", "expected_type": "overview"},
        {"query": "create a webhook notification", "expected_api": None, "expected_type": "endpoint"},
        {"query": "balance platform transfer funds", "expected_api": "Adyen", "expected_type": "endpoint"},
        {"query": "send email transactional messages", "expected_api": None, "expected_type": "endpoint"},
        {"query": "cloud object storage bucket", "expected_api": "Amazon", "expected_type": "overview"},
        {"query": "machine learning model deployment", "expected_api": "Amazon SageMaker", "expected_type": "overview"},
        {"query": "DNS domain name resolution", "expected_api": "Route 53", "expected_type": "overview"},
        {"query": "video upload and streaming API", "expected_api": "api.video", "expected_type": "overview"},
        {"query": "serverless function execution", "expected_api": "Lambda", "expected_type": "overview"},
        {"query": "database backup and restore", "expected_api": None, "expected_type": "endpoint"},
        {"query": "container orchestration service", "expected_api": "Amazon", "expected_type": "overview"},
        {"query": "fraud detection payment verification", "expected_api": "Adyen", "expected_type": "endpoint"},
        {"query": "IoT device management telemetry", "expected_api": None, "expected_type": "overview"},
        {"query": "API key management and rotation", "expected_api": None, "expected_type": "endpoint"},
        {"query": "image recognition object detection", "expected_api": "Amazon Rekognition", "expected_type": "overview"},
    ]

    os.makedirs(os.path.dirname(GOLDEN_DATASET_PATH), exist_ok=True)
    with open(GOLDEN_DATASET_PATH, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"Created golden dataset with {len(dataset)} queries at {GOLDEN_DATASET_PATH}")
    return dataset


def precision_at_k(results, expected_api, k=5):
    """Calculate Precision@K for a single query."""
    if expected_api is None:
        return None

    top_k = results[:k]
    relevant = sum(
        1 for r in top_k
        if expected_api.lower() in r["metadata"]["api_name"].lower()
    )
    return relevant / k


def run_eval():
    """Run the full evaluation suite."""
    if not os.path.exists(GOLDEN_DATASET_PATH):
        create_sample_golden_dataset()

    with open(GOLDEN_DATASET_PATH, "r") as f:
        dataset = json.load(f)

    print(f"Running evaluation on {len(dataset)} queries...\n")

    results = []
    total_p_at_5 = 0
    total_p_at_3 = 0
    total_latency = 0
    scored_count = 0

    for i, item in enumerate(dataset):
        query = item["query"]
        expected = item.get("expected_api")

        start = time.time()
        search_results = search(query, top_k=5)
        latency = time.time() - start

        p5 = precision_at_k(search_results, expected, k=5)
        p3 = precision_at_k(search_results, expected, k=3)

        top_apis = [r["metadata"]["api_name"] for r in search_results[:3]]
        hit = expected and any(
            expected.lower() in api.lower() for api in top_apis
        )

        result = {
            "query": query,
            "expected_api": expected,
            "top_results": top_apis,
            "hit_at_3": hit,
            "precision_at_5": p5,
            "precision_at_3": p3,
            "latency_ms": round(latency * 1000),
        }
        results.append(result)

        status = "✓" if hit else "✗"
        print(f"  [{status}] {query}")
        print(f"      Expected: {expected} | Got: {top_apis[:2]} | P@5: {p5} | {result['latency_ms']}ms")

        if p5 is not None:
            total_p_at_5 += p5
            total_p_at_3 += (p3 or 0)
            scored_count += 1

        total_latency += latency

    # Summary
    avg_p5 = total_p_at_5 / scored_count if scored_count > 0 else 0
    avg_p3 = total_p_at_3 / scored_count if scored_count > 0 else 0
    avg_latency = (total_latency / len(dataset)) * 1000
    hit_rate = sum(1 for r in results if r["hit_at_3"]) / len(dataset)

    summary = {
        "total_queries": len(dataset),
        "avg_precision_at_5": round(avg_p5, 4),
        "avg_precision_at_3": round(avg_p3, 4),
        "hit_rate_at_3": round(hit_rate, 4),
        "avg_latency_ms": round(avg_latency),
        "results": results,
    }

    with open(EVAL_RESULTS_PATH, "w") as f:
        json.dump(summary, f, indent=2)

    print(f"\n{'='*50}")
    print(f"EVALUATION RESULTS")
    print(f"{'='*50}")
    print(f"Queries:           {summary['total_queries']}")
    print(f"Avg Precision@5:   {summary['avg_precision_at_5']}")
    print(f"Avg Precision@3:   {summary['avg_precision_at_3']}")
    print(f"Hit Rate@3:        {summary['hit_rate_at_3']}")
    print(f"Avg Latency:       {summary['avg_latency_ms']}ms")
    print(f"\nResults saved to {EVAL_RESULTS_PATH}")

    return summary


if __name__ == "__main__":
    run_eval()