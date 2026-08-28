import requests

r = requests.get("https://reconai-backend-0aot.onrender.com/api/v1/exceptions")
if r.status_code == 200:
    data = r.json()
    if len(data) > 0:
        print("Keys of first exception:", list(data[0].keys()))
        print("First exception:", data[0])
    else:
        print("No exceptions found in DB.")
else:
    print("Error:", r.status_code, r.text)

r2 = requests.get("https://reconai-backend-0aot.onrender.com/api/v1/reconciliation/demo/latest")
print("\nDemo latest:")
if r2.status_code == 200:
    run_id = r2.json()["run_id"]
    r3 = requests.get(f"https://reconai-backend-0aot.onrender.com/api/v1/exceptions/run/{run_id}/highest-priority")
    print("Highest priority:", r3.text)
else:
    print("Error:", r2.status_code)

