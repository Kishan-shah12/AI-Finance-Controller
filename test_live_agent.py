import requests
import json

queries = [
    "Why is today's settlement short?",
    "Show unresolved transactions above ₹10,000.",
    "Which records are safe to auto-close?",
    "hi"
]

for q in queries:
    r = requests.post(
        "https://reconai-backend-0aot.onrender.com/api/v1/agent/query",
        json={"query": q, "context": {}}
    )
    print(f"\n--- {q} ---")
    print(r.status_code)
    print(json.dumps(r.json(), indent=2))
