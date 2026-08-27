import argparse
import random
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
import json
import csv
import os
from pathlib import Path
from typing import Tuple, List, Any

from app.schemas.financial import (
    Order, OrderStatus, Payment, PaymentStatus, PaymentMethod,
    Settlement, SettlementStatus, BankTransaction
)
from app.schemas.ground_truth import (
    GroundTruthItem, RecordStatus, ExpectedDecision, ExceptionType
)

MERCHANTS = ["M_RETAIL_1", "M_FOOD_1", "M_TECH_1", "M_CLOTHING_1"]
PAYMENT_METHODS = [PaymentMethod.UPI, PaymentMethod.CARD, PaymentMethod.NETBANKING, PaymentMethod.WALLET]

SCENARIO_DISTRIBUTION = [
    ("EXACT_MATCH", 0.55),
    ("FEE_VARIANCE", 0.08),
    ("TAX_VARIANCE", 0.05),
    ("MISSING_SETTLEMENT", 0.06),
    ("MISSING_BANK_ENTRY", 0.05),
    ("DUPLICATE", 0.05),
    ("UTR_MISMATCH", 0.05),
    ("PARTIAL_SETTLEMENT", 0.05),
    ("AMBIGUOUS", 0.06)
]

def generate_amount(random_instance) -> Decimal:
    base = random_instance.randint(100, 15000)
    if random_instance.random() < 0.3:
        base += 99
    elif random_instance.random() < 0.2:
        base += 50
    return Decimal(str(base))

def generate_utr(random_instance) -> str:
    return f"UTR{random_instance.randint(1000000000, 9999999999)}"

def generate_dates(random_instance, start_dt: datetime) -> Tuple[datetime, datetime, datetime, datetime]:
    order_dt = start_dt + timedelta(minutes=random_instance.randint(1, 1000))
    payment_dt = order_dt + timedelta(minutes=random_instance.randint(1, 30))
    settlement_dt = payment_dt + timedelta(hours=random_instance.randint(12, 48))
    bank_dt = settlement_dt + timedelta(hours=random_instance.randint(1, 24))
    return order_dt, payment_dt, settlement_dt, bank_dt

class DataGenerator:
    def __init__(self, seed: int):
        self.seed = seed
        self.random = random.Random(seed)
        self.start_date = datetime(2025, 1, 1)
        self.counter = 0

    def get_id(self, prefix: str) -> str:
        self.counter += 1
        return f"{prefix}-{self.counter}-{uuid.UUID(int=self.random.getrandbits(128))}"

    def get_merchant(self) -> str:
        return self.random.choice(MERCHANTS)

    def get_customer(self) -> str:
        return f"CUST_{self.random.randint(1000, 9999)}"

    def _create_base_chain(self) -> Tuple[Order, Payment, Settlement, BankTransaction]:
        merchant_id = self.get_merchant()
        customer_id = self.get_customer()
        order_dt, payment_dt, settlement_dt, bank_dt = generate_dates(self.random, self.start_date)
        amount = generate_amount(self.random)
        
        fee_pct = Decimal(str(round(self.random.uniform(0.01, 0.02), 4)))
        fee = round(amount * fee_pct, 2)
        tax = round(fee * Decimal('0.18'), 2)
        net = amount - fee - tax
        utr = generate_utr(self.random)

        order = Order(order_id=self.get_id("ORD"), merchant_id=merchant_id, customer_id=customer_id, order_date=order_dt, gross_amount=amount, status=OrderStatus.COMPLETED)
        payment = Payment(payment_id=self.get_id("PAY"), merchant_id=merchant_id, order_id=order.order_id, payment_date=payment_dt, amount=amount, payment_method=self.random.choice(PAYMENT_METHODS), payment_status=PaymentStatus.SUCCESS)
        settlement = Settlement(settlement_id=self.get_id("SET"), merchant_id=merchant_id, payment_id=payment.payment_id, settlement_date=settlement_dt, gross_amount=amount, fee=fee, tax=tax, net_amount=net, utr=utr, settlement_status=SettlementStatus.PROCESSED)
        bank = BankTransaction(bank_txn_id=self.get_id("BNK"), merchant_id=merchant_id, transaction_date=bank_dt, credit_amount=net, debit_amount=Decimal('0'), utr=utr, description=f"Settlement for {merchant_id} UTR: {utr}")
        return order, payment, settlement, bank

    def gen_exact_match(self, s_id: str):
        o, p, s, b = self._create_base_chain()
        gt = GroundTruthItem(scenario_id=s_id, scenario_type="EXACT_MATCH", record_status=RecordStatus.MATCHABLE, order_id=o.order_id, payment_id=p.payment_id, settlement_id=s.settlement_id, bank_transaction_id=b.bank_txn_id, ground_truth_match=True, expected_decision=ExpectedDecision.VERIFIED_MATCH)
        return [o], [p], [s], [b], gt

    def gen_fee_variance(self, s_id: str):
        o, p, s, b = self._create_base_chain()
        variance = Decimal('2.00')
        s.fee += variance
        s.net_amount -= variance
        b.credit_amount = s.net_amount
        gt = GroundTruthItem(scenario_id=s_id, scenario_type="FEE_VARIANCE", record_status=RecordStatus.MATCHABLE, order_id=o.order_id, payment_id=p.payment_id, settlement_id=s.settlement_id, bank_transaction_id=b.bank_txn_id, ground_truth_match=True, expected_decision=ExpectedDecision.MATCH_WITH_EXPLAINABLE_VARIANCE, exception_type=ExceptionType.FEE_VARIANCE)
        return [o], [p], [s], [b], gt

    def gen_tax_variance(self, s_id: str):
        o, p, s, b = self._create_base_chain()
        variance = Decimal('1.50')
        s.tax += variance
        s.net_amount -= variance
        b.credit_amount = s.net_amount
        gt = GroundTruthItem(scenario_id=s_id, scenario_type="TAX_VARIANCE", record_status=RecordStatus.MATCHABLE, order_id=o.order_id, payment_id=p.payment_id, settlement_id=s.settlement_id, bank_transaction_id=b.bank_txn_id, ground_truth_match=True, expected_decision=ExpectedDecision.MATCH_WITH_EXPLAINABLE_VARIANCE, exception_type=ExceptionType.TAX_VARIANCE)
        return [o], [p], [s], [b], gt

    def gen_missing_settlement(self, s_id: str):
        o, p, _, _ = self._create_base_chain()
        gt = GroundTruthItem(scenario_id=s_id, scenario_type="MISSING_SETTLEMENT", record_status=RecordStatus.NON_MATCHABLE, order_id=o.order_id, payment_id=p.payment_id, ground_truth_match=False, expected_decision=ExpectedDecision.UNRESOLVED, exception_type=ExceptionType.MISSING_SETTLEMENT)
        return [o], [p], [], [], gt

    def gen_missing_bank_entry(self, s_id: str):
        o, p, s, _ = self._create_base_chain()
        gt = GroundTruthItem(scenario_id=s_id, scenario_type="MISSING_BANK_ENTRY", record_status=RecordStatus.NON_MATCHABLE, order_id=o.order_id, payment_id=p.payment_id, settlement_id=s.settlement_id, ground_truth_match=False, expected_decision=ExpectedDecision.UNRESOLVED, exception_type=ExceptionType.MISSING_BANK_ENTRY)
        return [o], [p], [s], [], gt

    def gen_duplicate(self, s_id: str):
        o, p, s, b = self._create_base_chain()
        p2 = p.model_copy(update={'payment_id': self.get_id("PAY")})
        gt = GroundTruthItem(scenario_id=s_id, scenario_type="DUPLICATE", record_status=RecordStatus.MATCHABLE, order_id=o.order_id, payment_id=p.payment_id, settlement_id=s.settlement_id, bank_transaction_id=b.bank_txn_id, ground_truth_match=True, expected_decision=ExpectedDecision.DUPLICATE_CONFLICT, exception_type=ExceptionType.DUPLICATE)
        return [o], [p, p2], [s], [b], gt

    def gen_utr_mismatch(self, s_id: str):
        o, p, s, b = self._create_base_chain()
        s.utr = generate_utr(self.random)
        gt = GroundTruthItem(scenario_id=s_id, scenario_type="UTR_MISMATCH", record_status=RecordStatus.MATCHABLE, order_id=o.order_id, payment_id=p.payment_id, settlement_id=s.settlement_id, bank_transaction_id=b.bank_txn_id, ground_truth_match=True, expected_decision=ExpectedDecision.REVIEW, exception_type=ExceptionType.UTR_MISMATCH)
        return [o], [p], [s], [b], gt

    def gen_partial_settlement(self, s_id: str):
        o, p, s, b = self._create_base_chain()
        s.gross_amount = round(s.gross_amount / 2, 2)
        s.fee = round(s.fee / 2, 2)
        s.tax = round(s.tax / 2, 2)
        s.net_amount = s.gross_amount - s.fee - s.tax
        b.credit_amount = s.net_amount
        gt = GroundTruthItem(scenario_id=s_id, scenario_type="PARTIAL_SETTLEMENT", record_status=RecordStatus.MATCHABLE, order_id=o.order_id, payment_id=p.payment_id, settlement_id=s.settlement_id, bank_transaction_id=b.bank_txn_id, ground_truth_match=True, expected_decision=ExpectedDecision.REVIEW, exception_type=ExceptionType.PARTIAL_SETTLEMENT)
        return [o], [p], [s], [b], gt

    def gen_ambiguous(self, s_id: str):
        o1, p1, s1, b1 = self._create_base_chain()
        
        # Create a second candidate that is distinct but very similar (e.g., same amount, same date, different order/payment ID)
        o2 = o1.model_copy(update={
            'order_id': self.get_id("ORD"),
            'customer_id': self.get_customer(), # different customer
            'order_date': o1.order_date + timedelta(minutes=2) # close time
        })
        p2 = p1.model_copy(update={
            'payment_id': self.get_id("PAY"),
            'order_id': o2.order_id,
            'payment_date': p1.payment_date + timedelta(minutes=2)
        })
        
        # Instead of two settlements, let's say only ONE settlement exists that looks like it could belong to either payment.
        # This forces the engine to choose or flag as ambiguous.
        s1.utr = "UTR" # Strip UTR or make it generic so it doesn't perfectly match either payment uniquely if we had unique identifiers
        s1.payment_id = "UNKNOWN" # Strip payment_id to prevent exact match
        b1.utr = "UTR" # Ensure bank exact matches the settlement
        
        gt = GroundTruthItem(
            scenario_id=s_id, scenario_type="AMBIGUOUS", record_status=RecordStatus.MATCHABLE,
            order_id=o1.order_id, payment_id=p1.payment_id, settlement_id=s1.settlement_id, bank_transaction_id=b1.bank_txn_id,
            ground_truth_match=True, expected_decision=ExpectedDecision.REVIEW, exception_type=ExceptionType.AMBIGUOUS
        )
        return [o1, o2], [p1, p2], [s1], [b1], gt

    def generate(self, size: int):
        scenarios = []
        scenario_types = [s[0] for s in SCENARIO_DISTRIBUTION]
        scenario_weights = [s[1] for s in SCENARIO_DISTRIBUTION]

        for i in range(size):
            s_type = self.random.choices(scenario_types, weights=scenario_weights, k=1)[0]
            s_id = f"SCN-{i:05d}"
            
            generators = {
                "EXACT_MATCH": self.gen_exact_match,
                "FEE_VARIANCE": self.gen_fee_variance,
                "TAX_VARIANCE": self.gen_tax_variance,
                "MISSING_SETTLEMENT": self.gen_missing_settlement,
                "MISSING_BANK_ENTRY": self.gen_missing_bank_entry,
                "DUPLICATE": self.gen_duplicate,
                "UTR_MISMATCH": self.gen_utr_mismatch,
                "PARTIAL_SETTLEMENT": self.gen_partial_settlement,
                "AMBIGUOUS": self.gen_ambiguous
            }
            scenarios.append(generators[s_type](s_id))
            
        return scenarios

def write_csv(data: List[Any], filepath: Path):
    if not data:
        with open(filepath, 'w') as f:
            f.write("")
        return
    with open(filepath, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=data[0].model_dump().keys())
        writer.writeheader()
        for item in data:
            writer.writerow(item.model_dump())

def write_json(data: List[Any], filepath: Path):
    with open(filepath, 'w') as f:
        json.dump([item.model_dump(mode='json') for item in data], f, indent=2)

def validate_data(orders, payments, settlements, banks):
    # 1. Every payment references a real order unless intentionally missing (none are intentionally missing orders in our scenarios)
    order_ids = {o.order_id for o in orders}
    for p in payments:
        if p.order_id not in order_ids:
            raise ValueError(f"Payment {p.payment_id} references missing order {p.order_id}")
            
    # 2. Every settlement references a real payment
    payment_ids = {p.payment_id for p in payments}
    for s in settlements:
        if s.payment_id and s.payment_id != "UNKNOWN" and s.payment_id not in payment_ids:
            raise ValueError(f"Settlement {s.settlement_id} references missing payment {s.payment_id}")

    # 4. Settlement net amount equals gross - fee - tax where applicable (except some scenarios, but let's check general logic)
    # Our logic guarantees this in _create_base_chain, except we alter it for fee_variance. Actually wait, for fee variance:
    # s.fee += variance, s.net_amount -= variance. So gross - (fee+var) - (tax) == net - var. It holds!
    for s in settlements:
        expected_net = s.gross_amount - s.fee - s.tax
        if s.net_amount != expected_net:
            raise ValueError(f"Settlement {s.settlement_id} arithmetic failed: {s.gross_amount} - {s.fee} - {s.tax} != {s.net_amount}")

def process_split(split_name: str, split_data: List, base_path: Path):
    o_list, p_list, s_list, b_list, gt_list = [], [], [], [], []
    for o, p, s, b, gt in split_data:
        o_list.extend(o)
        p_list.extend(p)
        s_list.extend(s)
        b_list.extend(b)
        gt_list.append(gt)

    validate_data(o_list, p_list, s_list, b_list)

    sync_dir = base_path / "synthetic" / split_name
    sync_dir.mkdir(parents=True, exist_ok=True)
    write_csv(o_list, sync_dir / "orders.csv")
    write_csv(p_list, sync_dir / "payments.csv")
    write_csv(s_list, sync_dir / "settlements.csv")
    write_csv(b_list, sync_dir / "bank_transactions.csv")

    gt_dir = base_path / "ground_truth"
    gt_dir.mkdir(parents=True, exist_ok=True)
    write_json(gt_list, gt_dir / f"{split_name}_set.json")
    
    return len(gt_list)

def main():
    parser = argparse.ArgumentParser(description="Generate synthetic financial data")
    parser.add_argument("--size", type=int, default=1000, help="Number of scenarios to generate")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for determinism")
    args = parser.parse_args()

    import math
    assert math.isclose(sum(w for _, w in SCENARIO_DISTRIBUTION), 1.0), "Distribution weights must sum to 1.0"

    print(f"Generating {args.size} scenarios with seed {args.seed}...")
    generator = DataGenerator(seed=args.seed)
    scenarios = generator.generate(args.size)
    
    split_random = random.Random(args.seed + 1)
    split_random.shuffle(scenarios)
    
    dev_end = int(args.size * 0.7)
    val_end = dev_end + int(args.size * 0.15)
    
    dev_scenarios = scenarios[:dev_end]
    val_scenarios = scenarios[dev_end:val_end]
    test_scenarios = scenarios[val_end:]

    base_path = Path(__file__).parent.parent.parent.parent.parent / "data"
    
    dev_count = process_split("dev", dev_scenarios, base_path)
    val_count = process_split("val", val_scenarios, base_path)
    test_count = process_split("test", test_scenarios, base_path)

    print(f"Data generation complete. Dev: {dev_count}, Val: {val_count}, Test: {test_count}")

if __name__ == "__main__":
    main()
