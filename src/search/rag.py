import os
from openai import OpenAI
from dotenv import load_dotenv
from src.search.semantic_search import search

load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2-chat-latest")

SYSTEM_PROMPT = """You are API Universe, an AI-powered API discovery assistant.
Your job is to help developers find and understand APIs based on their needs.

Rules:
- Only use information from the provided search results to answer.
- Cite which API each piece of information comes from.
- If the search results don't contain relevant information, say so honestly.
- Be concise and practical. Developers want actionable answers.
- When comparing APIs, use a structured format.
"""


def build_context(results):
    """Format search results into context for the LLM."""
    context_parts = []
    for i, r in enumerate(results):
        meta = r["metadata"]
        part = f"[Source {i + 1}] API: {meta['api_name']}\n"
        part += f"Score: {r['score']:.3f}\n"
        if meta.get("type") == "endpoint":
            part += f"Endpoint: {meta.get('method', '')} {meta.get('path', '')}\n"
        part += f"Content: {r['text']}\n"
        context_parts.append(part)
    return "\n---\n".join(context_parts)


def ask(query, top_k=5):
    """Full RAG pipeline: search + generate."""
    results = search(query, top_k=top_k)
    context = build_context(results)

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Search results:\n{context}\n\nUser question: {query}"},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    answer = response.choices[0].message.content
    usage = response.usage

    return {
        "query": query,
        "answer": answer,
        "sources": [
            {
                "api_name": r["metadata"]["api_name"],
                "score": r["score"],
                "type": r["metadata"]["type"],
                "text": r["text"][:200],
            }
            for r in results
        ],
        "tokens": {
            "input": usage.prompt_tokens,
            "output": usage.completion_tokens,
        },
    }


if __name__ == "__main__":
    query = "I need an API to send SMS messages internationally"
    print(f"Query: {query}\n")

    result = ask(query)
    print(f"Answer:\n{result['answer']}\n")
    print(f"Sources:")
    for s in result["sources"]:
        print(f"  - {s['api_name']} (score: {s['score']:.3f})")
    print(f"\nTokens: {result['tokens']}")