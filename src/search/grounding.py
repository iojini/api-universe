import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()
MODEL = os.getenv("OPENAI_MODEL", "gpt-5.2-chat-latest")

GROUNDING_PROMPT = """You are a grounding verification system. Your job is to check whether each claim in an AI-generated answer is supported by the provided source documents.

For each claim in the answer, determine if it is:
- SUPPORTED: Directly backed by information in the sources
- UNSUPPORTED: Not found in the sources
- PARTIAL: Loosely related but not directly stated

Respond in this exact JSON format:
{
  "claims": [
    {"claim": "the claim text", "status": "SUPPORTED", "source": "which source"},
    {"claim": "the claim text", "status": "UNSUPPORTED", "source": null}
  ],
  "supported_count": 0,
  "total_count": 0,
  "grounding_score": 0.0
}
"""


def check_grounding(answer, sources):
    """Verify how well an answer is grounded in its sources."""
    source_text = "\n---\n".join(
        f"[Source {i+1}] {s.get('api_name', 'Unknown')}: {s.get('text', '')}"
        for i, s in enumerate(sources)
    )

    messages = [
        {"role": "system", "content": GROUNDING_PROMPT},
        {"role": "user", "content": f"Sources:\n{source_text}\n\nAnswer to verify:\n{answer}"},
    ]

    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
    )

    raw = response.choices[0].message.content

    try:
        import json
        clean = raw.strip()
        if clean.startswith("```"):
            clean = clean.split("\n", 1)[1].rsplit("```", 1)[0]
        result = json.loads(clean)
    except (json.JSONDecodeError, IndexError):
        result = {
            "claims": [],
            "supported_count": 0,
            "total_count": 0,
            "grounding_score": 0.0,
            "raw_response": raw,
        }

    return result


if __name__ == "__main__":
    test_answer = "The Authentiq API provides passwordless authentication using JWT tokens. It supports push-based sign-in via POST /login."
    test_sources = [
        {"api_name": "Authentiq API", "text": "Authentiq API\nStrong authentication, without the passwords."},
        {"api_name": "Authentiq API", "text": "POST /login\npush sign-in request\nSee: https://github.com/skion/authentiq/wiki/JWT-Examples"},
    ]

    result = check_grounding(test_answer, test_sources)
    print(f"Grounding Score: {result.get('grounding_score', 0)}")
    for claim in result.get("claims", []):
        print(f"  [{claim['status']}] {claim['claim']}")