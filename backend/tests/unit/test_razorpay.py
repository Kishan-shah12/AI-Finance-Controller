import json
import pytest
import os
from decimal import Decimal
from app.providers.razorpay_provider import RazorpayProvider

@pytest.fixture
def provider():
    # Will not use real keys during unit tests
    return RazorpayProvider()

@pytest.fixture
def settlement_fixture():
    with open(os.path.join(os.path.dirname(__file__), "../fixtures/razorpay/settlement.json"), "r") as f:
        return json.load(f)

@pytest.fixture
def recon_fixture():
    with open(os.path.join(os.path.dirname(__file__), "../fixtures/razorpay/settlement_recon.json"), "r") as f:
        return json.load(f)

@pytest.fixture
def payment_fixture():
    with open(os.path.join(os.path.dirname(__file__), "../fixtures/razorpay/payment.json"), "r") as f:
        return json.load(f)

@pytest.fixture
def order_fixture():
    with open(os.path.join(os.path.dirname(__file__), "../fixtures/razorpay/order.json"), "r") as f:
        return json.load(f)

def test_settlement_normalization(provider, settlement_fixture):
    item = settlement_fixture["items"][0]
    s = provider.normalize_settlement(item)
    
    assert s.settlement_id == "setl_1234567890"
    assert s.gross_amount == Decimal("4850.00")
    assert s.fee == Decimal("12.71")
    assert s.tax == Decimal("2.29")
    assert s.net_amount == Decimal("4835.00") # 4850 - 12.71 - 2.29
    assert s.utr == "UTR987654321"

def test_recon_normalization(provider, recon_fixture):
    item = recon_fixture["items"][0]
    s = provider.normalize_recon(item)
    
    assert s.settlement_id == "setl_1234567890"
    assert s.payment_id == "pay_1234567890"
    assert s.gross_amount == Decimal("5000.00")
    assert s.fee == Decimal("12.71")
    assert s.tax == Decimal("2.29")
    assert s.net_amount == Decimal("4850.00")

def test_payment_normalization(provider, payment_fixture):
    p = provider.normalize_payment(payment_fixture)
    
    assert p.payment_id == "pay_1234567890"
    assert p.order_id == "order_1234567890"
    assert p.amount == Decimal("5000.00")
    assert p.payment_method.value == "UPI"
    assert p.payment_status.value == "SUCCESS"

def test_order_normalization(provider, order_fixture):
    o = provider.normalize_order(order_fixture)
    
    assert o.order_id == "order_1234567890"
    assert o.gross_amount == Decimal("5000.00")
    assert o.status.value == "COMPLETED"

def test_provider_status_no_credentials(provider):
    # Should report NOT_CONFIGURED when missing credentials
    status = provider.get_status()
    assert status["configured"] is False
    assert status["reachable"] is False
    assert "Server credentials not configured" in status["message"]
