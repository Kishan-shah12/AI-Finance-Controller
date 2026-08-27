from app.schemas.financial import Order, Payment, Settlement, BankTransaction
from .models import NormalizedRecord

def normalize_order(o: Order) -> NormalizedRecord:
    return NormalizedRecord(
        type='order',
        id=o.order_id.strip(),
        merchant_id=o.merchant_id.strip(),
        amount=o.gross_amount,
        date=o.order_date.timestamp(),
        original=o
    )

def normalize_payment(p: Payment) -> NormalizedRecord:
    return NormalizedRecord(
        type='payment',
        id=p.payment_id.strip(),
        merchant_id=p.merchant_id.strip(),
        amount=p.amount,
        date=p.payment_date.timestamp(),
        original=p
    )

def normalize_settlement(s: Settlement) -> NormalizedRecord:
    return NormalizedRecord(
        type='settlement',
        id=s.settlement_id.strip(),
        merchant_id=s.merchant_id.strip(),
        amount=s.gross_amount,
        date=s.settlement_date.timestamp(),
        utr=s.utr.strip() if s.utr else None,
        original=s
    )

def normalize_bank(b: BankTransaction) -> NormalizedRecord:
    return NormalizedRecord(
        type='bank',
        id=b.bank_txn_id.strip(),
        merchant_id=b.merchant_id.strip(),
        amount=b.credit_amount, # bank amount to match settlement net
        date=b.transaction_date.timestamp(),
        utr=b.utr.strip() if b.utr else None,
        original=b
    )
