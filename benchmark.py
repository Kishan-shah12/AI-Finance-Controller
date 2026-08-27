import os
import sys
import time
import warnings
warnings.filterwarnings("ignore")

import requests
from pathlib import Path

backend_dir = str(Path(__file__).parent.resolve() / "backend")
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from app.services.reconciliation.engine import reconcile
from app.services.reconciliation.thresholds import ReconciliationThresholds
from app.services.synthetic.generator import DataGenerator


def benchmark_core_engine():
    print("--- CORE ENGINE THROUGHPUT BENCHMARK ---")
    
    # 1. Generate 1000 records
    start_gen = time.time()
    provider = DataGenerator(seed=42)
    scenarios = provider.generate(size=1000)
    
    o_list, p_list, s_list, b_list = [], [], [], []
    for o, p, s, b, gt in scenarios:
        o_list.extend(o)
        p_list.extend(p)
        s_list.extend(s)
        b_list.extend(b)
        
    gen_time = time.time() - start_gen
    print(f"Generation time: {gen_time:.3f}s")
    
    # 2. Setup Thresholds
    thresholds = ReconciliationThresholds()
    
    # 3. Run Reconcile
    start_recon = time.time()
    result = reconcile(o_list, p_list, s_list, b_list, thresholds=thresholds)
    recon_time = time.time() - start_recon
    
    metrics = result['metrics']
    print(f"Reconciliation Engine Time: {recon_time:.3f}s")
    print(f"Records processed: {metrics['records_processed']}")
    print(f"Core Engine Throughput: {metrics['records_per_second']:.2f} records/second")

def benchmark_e2e():
    print("\n--- END-TO-END DEMO LATENCY BENCHMARK ---")
    print("Ensure the backend is running at http://localhost:8000")
    try:
        start = time.time()
        resp = requests.post("http://localhost:8000/api/v1/reconciliation/run", json={
            "mode": "demo",
            "provider": "SYNTHETIC",
            "size": 1000,
            "seed": 42
        })
        end = time.time()
        
        if resp.status_code == 200:
            print(f"API Request Latency: {end - start:.3f}s")
        else:
            print(f"API Failed: {resp.status_code}")
    except requests.exceptions.ConnectionError:
        print("Backend not running. Skipping E2E test.")

if __name__ == "__main__":
    benchmark_core_engine()
    benchmark_e2e()
