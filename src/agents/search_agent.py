import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
from src.search.semantic_search import search
from src.search.grounding import check_grounding

load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2-chat-latest")


class AgentState(TypedDict):
    query: str
    query_type: str
    sub_queries: list
    all_results: list
    answer: str
    grounding: dict
    trace: list


def classify_query(state: AgentState) -> AgentState:
    """Determine if the query is simple or complex."""
    messages = [
        {"role": "system", "content": """Classify the user query into one of these types:
- SIMPLE: Single straightforward question about one API or topic
- COMPARE: Asks to compare multiple APIs or find the best option with multiple criteria
- EXPLORE: Open-ended exploration of what's available

Respond with ONLY the type in JSON: {"type": "SIMPLE"} or {"type": "COMPARE"} or {"type": "EXPLORE"}"""},
        {"role": "user", "content": state["query"]},
    ]

    response = client.chat.completions.create(model=MODEL, messages=messages)
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
    """Break complex queries into sub-queries."""
    if state["query_type"] == "SIMPLE":
        state["sub_queries"] = [state["query"]]
        state["trace"].append({"step": "decompose", "result": "single query (simple)"})
        return state

    messages = [
        {"role": "system", "content": """Break this query into 2-4 focused sub-queries for semantic search.
Each sub-query should target one specific aspect.
Respond with ONLY a JSON array: ["sub query 1", "sub query 2"]"""},
        {"role": "user", "content": state["query"]},
    ]

    response = client.chat.completions.create(model=MODEL, messages=messages)
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
    """Run semantic search for each sub-query."""
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
    """Generate answer from retrieved results."""
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
- Cite which source each claim comes from.
- For comparisons, use structured tables.
- Be honest when information is missing.
- Be concise and practical."""

    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": f"Search results:\n{context}\n\nUser question: {state['query']}"},
    ]

    response = client.chat.completions.create(model=MODEL, messages=messages)
    state["answer"] = response.choices[0].message.content
    state["trace"].append({"step": "generate", "tokens": response.usage.completion_tokens})
    return state


def verify(state: AgentState) -> AgentState:
    """Run grounding check on the answer."""
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


def route_after_classify(state: AgentState) -> str:
    """Route based on query type."""
    return "decompose"


# Build the graph
workflow = StateGraph(AgentState)
workflow.add_node("classify", classify_query)
workflow.add_node("decompose", decompose_query)
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.add_node("verify", verify)

workflow.set_entry_point("classify")
workflow.add_edge("classify", "decompose")
workflow.add_edge("decompose", "retrieve")
workflow.add_edge("retrieve", "generate")
workflow.add_edge("generate", "verify")
workflow.add_edge("verify", END)

agent = workflow.compile()


def run_agent(query: str) -> dict:
    """Run the full agent pipeline."""
    initial_state = {
        "query": query,
        "query_type": "",
        "sub_queries": [],
        "all_results": [],
        "answer": "",
        "grounding": {},
        "trace": [],
    }

    result = agent.invoke(initial_state)

    return {
        "query": result["query"],
        "query_type": result["query_type"],
        "answer": result["answer"],
        "grounding": result["grounding"],
        "trace": result["trace"],
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
    query = "Compare authentication APIs that support passwordless login"
    print(f"Query: {query}\n")

    result = run_agent(query)

    print(f"Type: {result['query_type']}")
    print(f"\nTrace:")
    for step in result["trace"]:
        print(f"  {step}")
    print(f"\nAnswer:\n{result['answer']}")
    print(f"\nGrounding: {result['grounding']['score']}")