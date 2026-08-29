import requests
import time

def run():
    print("=== Provider Status ===")
    res = requests.get("http://localhost:8000/api/v1/providers/razorpay/status")
    print(res.json())

    print("\n=== Trigger Run ===")
    res = requests.post("http://localhost:8000/api/v1/reconciliation/run", json={
        "provider": "RAZORPAY_TEST",
        "mode": "run",
        "size": 100
    })
    run_id = res.json().get("run_id")
    print("Run Triggered:", res.json())

    if run_id:
        time.sleep(2)
        print("\n=== Run Status ===")
        res = requests.get(f"http://localhost:8000/api/v1/reconciliation/runs/{run_id}")
        print(res.json())

        print("\n=== Exceptions ===")
        res = requests.get(f"http://localhost:8000/api/v1/exceptions/run/{run_id}/highest-priority")
        print("Highest priority:", res.status_code, res.text)
        
        res = requests.get(f"http://localhost:8000/api/v1/exceptions", params={"run_id": run_id})
        # print first few if any
        items = res.json()
        print("Exceptions count:", len(items) if isinstance(items, list) else items)

run()
