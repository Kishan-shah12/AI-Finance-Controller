import requests

def test_query(query_text):
    print(f"\n--- QUERY: {query_text} ---")
    r = requests.post(
        "https://reconai-backend-0aot.onrender.com/api/v1/agent/query",
        json={"query": query_text, "context": {}}
    )
    print(f"Status: {r.status_code}")
    print(r.json())

test_query("Why is today's settlement short?")
test_query("Show unresolved transactions above ₹10,000.")
test_query("hi")
