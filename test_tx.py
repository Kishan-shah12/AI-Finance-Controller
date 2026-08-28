import requests

print("--- FETCHING EXCEPTIONS ---")
r = requests.get("https://reconai-backend-0aot.onrender.com/api/v1/exceptions")
if r.status_code == 200:
    data = r.json()
    if len(data) > 0:
        print(f"Total exceptions: {len(data)}")
        print("First exception keys:", list(data[0].keys()))
        for i in range(min(3, len(data))):
            ex = data[i]
            print(f"\nException {i}:")
            print(f"id: {ex.get('id')}")
            print(f"exception_type: {ex.get('exception_type')}")
            print(f"decision: {ex.get('decision')}")
            
        first_id = data[0]['id']
        print(f"\n--- FETCHING REAL EXCEPTION ({first_id}) ---")
        r2 = requests.get(f"https://reconai-backend-0aot.onrender.com/api/v1/exceptions/{first_id}")
        print(f"Status: {r2.status_code}")
        
    else:
        print("No exceptions found in DB.")
else:
    print("Error:", r.status_code, r.text)

print("\n--- FETCHING INVALID EXCEPTION (TX-9025) ---")
r3 = requests.get("https://reconai-backend-0aot.onrender.com/api/v1/exceptions/TX-9025")
print(f"Status: {r3.status_code}")
print(f"Response: {r3.text}")
