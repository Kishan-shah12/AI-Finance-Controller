import json
import csv
from typing import Tuple, List, Dict
from pathlib import Path
from decimal import Decimal
from app.schemas.financial import Order, Payment, Settlement, BankTransaction
from app.schemas.ground_truth import GroundTruthItem

def load_split(split_name: str, base_path: Path) -> Tuple[List[Order], List[Payment], List[Settlement], List[BankTransaction], List[GroundTruthItem]]:
    synth_path = base_path / 'synthetic'
    gt_path = base_path / 'ground_truth'
    
    orders = []
    with open(synth_path / split_name / 'orders.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            orders.append(Order(**row))
            
    payments = []
    with open(synth_path / split_name / 'payments.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            payments.append(Payment(**row))
            
    settlements = []
    with open(synth_path / split_name / 'settlements.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            settlements.append(Settlement(**row))
            
    banks = []
    with open(synth_path / split_name / 'bank_transactions.csv', 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            banks.append(BankTransaction(**row))
            
    ground_truth = []
    with open(gt_path / f'{split_name}_set.json', 'r') as f:
        data = json.load(f)
        for item in data:
            ground_truth.append(GroundTruthItem(**item))
            
    return orders, payments, settlements, banks, ground_truth
