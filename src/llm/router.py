import os
import time
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class LLMRouter:
    """Routes LLM calls across providers with fallback."""

    def __init__(self):
        self.providers = []
        self.stats = {}

        # Primary: OpenAI
        if os.getenv("OPENAI_API_KEY"):
            self.providers.append({
                "name": "openai",
                "client": OpenAI(),
                "model": os.getenv("OPENAI_MODEL", "gpt-5.2-chat-latest"),
                "priority": 1,
            })

        # Secondary: Azure OpenAI
        if os.getenv("AZURE_OPENAI_KEY"):
            self.providers.append({
                "name": "azure",
                "client": OpenAI(
                    api_key=os.getenv("AZURE_OPENAI_KEY"),
                    base_url=f"{os.getenv('AZURE_OPENAI_ENDPOINT')}/openai/deployments/{os.getenv('AZURE_OPENAI_DEPLOYMENT', 'gpt-4')}/",
                    default_headers={"api-key": os.getenv("AZURE_OPENAI_KEY")},
                ),
                "model": os.getenv("AZURE_OPENAI_DEPLOYMENT", "gpt-4"),
                "priority": 2,
            })

        # Initialize stats
        for p in self.providers:
            self.stats[p["name"]] = {
                "requests": 0,
                "failures": 0,
                "total_latency": 0,
                "avg_latency": 0,
            }

    def chat(self, messages, **kwargs):
        """Send a chat request with automatic fallback."""
        errors = []

        for provider in sorted(self.providers, key=lambda p: p["priority"]):
            try:
                start = time.time()
                response = provider["client"].chat.completions.create(
                    model=provider["model"],
                    messages=messages,
                    **kwargs,
                )
                latency = time.time() - start

                # Update stats
                stats = self.stats[provider["name"]]
                stats["requests"] += 1
                stats["total_latency"] += latency
                stats["avg_latency"] = stats["total_latency"] / stats["requests"]

                return {
                    "response": response,
                    "provider": provider["name"],
                    "model": provider["model"],
                    "latency": round(latency, 3),
                }

            except Exception as e:
                self.stats[provider["name"]]["failures"] += 1
                errors.append({"provider": provider["name"], "error": str(e)})
                continue

        raise Exception(f"All providers failed: {json.dumps(errors)}")

    def get_stats(self):
        """Return routing statistics."""
        total_requests = sum(s["requests"] for s in self.stats.values())
        return {
            "providers": {
                name: {
                    **stats,
                    "traffic_pct": round(stats["requests"] / total_requests * 100, 1)
                        if total_requests > 0 else 0,
                    "avg_latency": round(stats["avg_latency"], 3),
                }
                for name, stats in self.stats.items()
            },
            "total_requests": total_requests,
        }


# Global router instance
router = LLMRouter()


if __name__ == "__main__":
    print(f"Configured providers: {[p['name'] for p in router.providers]}\n")

    result = router.chat([
        {"role": "user", "content": "Say hello in one sentence."},
    ])

    print(f"Provider: {result['provider']}")
    print(f"Model: {result['model']}")
    print(f"Latency: {result['latency']}s")
    print(f"Response: {result['response'].choices[0].message.content}")
    print(f"\nStats: {json.dumps(router.get_stats(), indent=2)}")