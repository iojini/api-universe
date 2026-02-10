import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict
from src.search.semantic_search import search
from src.search.grounding import check_grounding

load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2-chat-latest")
FAST_MODEL = "gpt-5-nano"
MID_MODEL = "gpt-5-mini"

GROUNDING_THRESHOLD = 0.0
MAX_RETRIES = 0


class AgentState(TypedDict):
    query: str
    query_type: str
    sub_queries: list
    all_results: list
    answer: str
    grounding: dict
    trace: list
    retry_count: int


def classify_query(state: AgentState) -> AgentState:
    messages = [
        {"role": "system", "content": """Classify the user query into one of these types:
- SIMPLE: Single straightforward question about one API or topic
- COMPARE: Asks to compare multiple APIs or find the best option with multiple criteria
- EXPLORE: Open-ended exploration of what's available

Respond with ONLY the type in JSON: {"type": "SIMPLE"} or {"type": "COMPARE"} or {"type": "EXPLORE"}"""},
        {"role": "user", "content": state["query"]},
    ]

    response = client.chat.completions.create(model=FAST_MODEL, messages=messages)
    raw = response.choices[0].message.content.strip()

    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        result = json.loads(clean)
        query_type = result.get("type", "SIMPLE")
    except json.JSONDecodeError:
        query_type = "SIMPLE"

    state["query_type"] = query_type
    state["trace"].append({"step": "classify", "result": query_type})
    return state


def decompose_query(state: AgentState) -> AgentState:
    if state["query_type"] == "SIMPLE":
        state["sub_queries"] = [state["query"]]
        state["trace"].append({"step": "decompose", "result": "single query (simple)"})
        return state

    messages = [
        {"role": "system", "content": """Break this query into 2-3 short sub-queries for semantic search. Each sub-query must be under 8 words. Respond with ONLY a JSON array: ["sub query 1", "sub query 2"]"""},
        {"role": "user", "content": state["query"]},
    ]

    response = client.chat.completions.create(model=FAST_MODEL, messages=messages)
    raw = response.choices[0].message.content.strip()

    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        sub_queries = json.loads(clean)
    except json.JSONDecodeError:
        sub_queries = [state["query"]]

    state["sub_queries"] = sub_queries
    state["trace"].append({"step": "decompose", "result": sub_queries})
    return state


def retrieve(state: AgentState) -> AgentState:
    all_results = []
    seen = set()

    for sq in state["sub_queries"]:
        results = search(sq, top_k=5)
        for r in results:
            key = r["text"][:100]
            if key not in seen:
                seen.add(key)
                all_results.append(r)

    state["all_results"] = all_results
    state["trace"].append({
        "step": "retrieve",
        "sub_queries": len(state["sub_queries"]),
        "total_results": len(all_results),
    })
    return state


def generate(state: AgentState) -> AgentState:
    context_parts = []
    for i, r in enumerate(state["all_results"][:10]):
        meta = r["metadata"]
        part = f"[Source {i+1}] API: {meta['api_name']}\n"
        if meta.get("type") == "endpoint":
            part += f"Endpoint: {meta.get('method', '')} {meta.get('path', '')}\n"
        part += f"Content: {r['text']}\n"
        context_parts.append(part)

    context = "\n---\n".join(context_parts)

    system = """You are API Universe, an AI-powered API discovery assistant.
Rules:
- Only use information from the provided search results.
- Cite which source each claim comes from using [Source N].
- Be honest when information is missing.
- Be concise and practical.

For COMPARISON queries, use this exact format:
1. One intro sentence.
2. A markdown table with EXACTLY these 4 columns: | API | Key Capability | Support | Notes |
   - Keep each cell under 8 words.
   - Use Yes/No/Partial for the Support column.
3. A final section starting with **Recommendation:** giving a clear pick with caveats.

Do NOT include source numbers, endpoints, or URLs in the table. Keep it scannable."""

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Search results:\n{context}\n\nUser question: {state['query']}"},
    ]

    response = client.chat.completions.create(model=MODEL, messages=messages, max_completion_tokens=400)
    state["answer"] = response.choices[0].message.content
    state["trace"].append({"step": "generate", "tokens": response.usage.completion_tokens})
    return state


def verify(state: AgentState) -> AgentState:
    sources = [
        {"api_name": r["metadata"]["api_name"], "text": r["text"][:200]}
        for r in state["all_results"][:10]
    ]

    grounding = check_grounding(state["answer"], sources)
    state["grounding"] = {
        "score": grounding.get("grounding_score", 0),
        "supported": grounding.get("supported_count", 0),
        "total": grounding.get("total_count", 0),
        "claims": grounding.get("claims", []),
    }
    state["trace"].append({"step": "verify", "grounding_score": state["grounding"]["score"]})
    return state


def refine_query(state: AgentState) -> AgentState:
    """Refine the query when grounding is low."""
    state["retry_count"] += 1

    unsupported = [
        c["claim"] for c in state["grounding"].get("claims", [])
        if c["status"] == "UNSUPPORTED"
    ]

    messages = [
        {"role": "system", "content": """The previous search didn't return well-grounded results.
Based on the unsupported claims, generate 2-3 refined search queries that might find better sources.
Respond with ONLY a JSON array: ["refined query 1", "refined query 2"]"""},
        {"role": "user", "content": f"Original query: {state['query']}\nUnsupported claims: {json.dumps(unsupported)}"},
    ]

    response = client.chat.completions.create(model=MODEL, messages=messages)
    raw = response.choices[0].message.content.strip()

    try:
        clean = raw.replace("```json", "").replace("```", "").strip()
        refined = json.loads(clean)
    except json.JSONDecodeError:
        refined = [state["query"]]

    state["sub_queries"] = refined
    state["trace"].append({
        "step": "refine",
        "reason": f"grounding score {state['grounding']['score']} below threshold {GROUNDING_THRESHOLD}",
        "refined_queries": refined,
        "retry": state["retry_count"],
    })
    return state


def should_retry(state: AgentState) -> str:
    """Decide whether to retry or finish."""
    score = state["grounding"].get("score", 0)
    if score < GROUNDING_THRESHOLD and state["retry_count"] < MAX_RETRIES:
        return "refine"
    return "end"


# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("classify", classify_query)
workflow.add_node("decompose", decompose_query)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.add_node("verify", verify)
workflow.add_node("refine", refine_query)

workflow.set_entry_point("classify")
workflow.add_edge("classify", "decompose")
workflow.add_edge("decompose", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "verify")
workflow.add_conditional_edges("verify", should_retry, {"refine": "refine", "end": END})
workflow.add_edge("refine", "retrieve")

agent = workflow.compile()


def run_agent(query: str) -> dict:
    initial_state = {
        "query": query,
        "query_type": "",
        "sub_queries": [],
        "all_results": [],
        "answer": "",
        "grounding": {},
        "trace": [],
        "retry_count": 0,
    }

    result = agent.invoke(initial_state)

    return {
        "query": result["query"],
        "query_type": result["query_type"],
        "answer": result["answer"],
        "grounding": result["grounding"],
        "trace": result["trace"],
        "retries": result["retry_count"],
        "sources": [
            {
                "api_name": r["metadata"]["api_name"],
                "score": r["score"],
                "type": r["metadata"]["type"],
            }
            for r in result["all_results"][:10]
        ],
    }


if __name__ == "__main__":
    query = "Which REST APIs support GraphQL subscriptions natively?"
    print(f"Query: {query}\n")

    result = run_agent(query)

    print(f"Type: {result['query_type']}")
    print(f"Retries: {result['retries']}")
    print(f"\nTrace:")
    for step in result["trace"]:
        print(f"  {step}")
    print(f"\nGrounding: {result['grounding']['score']}")
    print(f"\nAnswer:\n{result['answer']}")