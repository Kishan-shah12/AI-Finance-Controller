import pytest
from app.services.synthetic.generator import DataGenerator
from app.schemas.ground_truth import RecordStatus, ExpectedDecision, ExceptionType

def test_deterministic_output():
    gen1 = DataGenerator(seed=42)
    s1 = gen1.generate(100)
    
    gen2 = DataGenerator(seed=42)
    s2 = gen2.generate(100)
    
    gen3 = DataGenerator(seed=43)
    s3 = gen3.generate(100)
    
    # Check 42 == 42
    assert s1[0][0][0].order_id == s2[0][0][0].order_id
    # Check 42 != 43
    assert s1[0][0][0].order_id != s3[0][0][0].order_id

def test_missing_settlement():
    gen = DataGenerator(seed=1)
    o, p, s, b, gt = gen.gen_missing_settlement("SCN-1")
    assert len(s) == 0
    assert len(b) == 0
    assert gt.record_status == RecordStatus.NON_MATCHABLE
    assert gt.expected_decision == ExpectedDecision.UNRESOLVED
    assert gt.exception_type == ExceptionType.MISSING_SETTLEMENT

def test_missing_bank_entry():
    gen = DataGenerator(seed=1)
    o, p, s, b, gt = gen.gen_missing_bank_entry("SCN-1")
    assert len(s) == 1
    assert len(b) == 0
    assert gt.record_status == RecordStatus.NON_MATCHABLE
    assert gt.expected_decision == ExpectedDecision.UNRESOLVED
    assert gt.exception_type == ExceptionType.MISSING_BANK_ENTRY

def test_duplicate_generation():
    gen = DataGenerator(seed=1)
    o, p, s, b, gt = gen.gen_duplicate("SCN-1")
    assert len(p) == 2
    assert p[0].payment_id != p[1].payment_id
    assert p[0].amount == p[1].amount
    assert gt.expected_decision == ExpectedDecision.DUPLICATE_CONFLICT

def test_utr_mismatch():
    gen = DataGenerator(seed=1)
    o, p, s, b, gt = gen.gen_utr_mismatch("SCN-1")
    assert s[0].utr != b[0].utr
    assert gt.exception_type == ExceptionType.UTR_MISMATCH

def test_partial_settlement():
    gen = DataGenerator(seed=1)
    o, p, s, b, gt = gen.gen_partial_settlement("SCN-1")
    assert s[0].gross_amount < p[0].amount
    assert s[0].net_amount == b[0].credit_amount
    assert gt.exception_type == ExceptionType.PARTIAL_SETTLEMENT

def test_ambiguous_candidates():
    gen = DataGenerator(seed=1)
    o, p, s, b, gt = gen.gen_ambiguous("SCN-1")
    assert len(o) == 2
    assert len(p) == 2
    assert len(s) == 1
    assert gt.expected_decision == ExpectedDecision.REVIEW

def test_settlement_arithmetic():
    gen = DataGenerator(seed=1)
    o, p, s, b, gt = gen.gen_exact_match("SCN-1")
    settlement = s[0]
    expected_net = settlement.gross_amount - settlement.fee - settlement.tax
    assert settlement.net_amount == expected_net
    assert b[0].credit_amount == settlement.net_amount

def test_date_ordering():
    gen = DataGenerator(seed=1)
    o, p, s, b, gt = gen.gen_exact_match("SCN-1")
    assert o[0].order_date <= p[0].payment_date
    assert p[0].payment_date <= s[0].settlement_date
    assert s[0].settlement_date <= b[0].transaction_date
