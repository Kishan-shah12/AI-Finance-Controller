from enum import Enum
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"

class Order(BaseModel):
    order_id: str
    merchant_id: str
    customer_id: str
    order_date: datetime
    gross_amount: Decimal
    currency: str = "INR"
    status: OrderStatus

class PaymentStatus(str, Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"

class PaymentMethod(str, Enum):
    UPI = "UPI"
    CARD = "CARD"
    NETBANKING = "NETBANKING"
    WALLET = "WALLET"

class Payment(BaseModel):
    payment_id: str
    merchant_id: str
    order_id: str
    payment_date: datetime
    amount: Decimal
    currency: str = "INR"
    payment_method: PaymentMethod
    payment_status: PaymentStatus

class SettlementStatus(str, Enum):
    PROCESSED = "PROCESSED"
    FAILED = "FAILED"

class Settlement(BaseModel):
    settlement_id: str
    merchant_id: str
    payment_id: str
    settlement_date: datetime
    gross_amount: Decimal
    fee: Decimal
    tax: Decimal
    net_amount: Decimal
    utr: str
    settlement_status: SettlementStatus

class BankTransaction(BaseModel):
    bank_txn_id: str
    merchant_id: str
    transaction_date: datetime
    credit_amount: Decimal
    debit_amount: Decimal
    utr: str
    description: str
