CREATE TABLE IF NOT EXISTS reconciliation_runs (
    id VARCHAR PRIMARY KEY,
    mode VARCHAR NOT NULL,
    provider VARCHAR NOT NULL,
    status VARCHAR NOT NULL,
    size INTEGER,
    seed INTEGER,
    records_processed INTEGER,
    scenario_count INTEGER,
    verified_match INTEGER,
    explainable_variance INTEGER,
    review INTEGER,
    unresolved INTEGER,
    duplicate_conflict INTEGER,
    elapsed_seconds FLOAT,
    throughput FLOAT,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS reconciliation_matches (
    id VARCHAR PRIMARY KEY,
    run_id VARCHAR NOT NULL REFERENCES reconciliation_runs(id) ON DELETE CASCADE,
    scenario_id VARCHAR,
    decision VARCHAR NOT NULL,
    confidence FLOAT NOT NULL,
    order_id VARCHAR,
    payment_id VARCHAR,
    settlement_id VARCHAR,
    bank_transaction_id VARCHAR,
    variance_details JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS exceptions (
    id VARCHAR PRIMARY KEY,
    run_id VARCHAR NOT NULL REFERENCES reconciliation_runs(id) ON DELETE CASCADE,
    scenario_id VARCHAR,
    exception_type VARCHAR NOT NULL,
    decision VARCHAR NOT NULL,
    confidence FLOAT NOT NULL,
    order_id VARCHAR,
    payment_id VARCHAR,
    settlement_id VARCHAR,
    bank_transaction_id VARCHAR,
    variance_details JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE,
    updated_at TIMESTAMP WITHOUT TIME ZONE
);

CREATE TABLE IF NOT EXISTS exception_evidence (
    id VARCHAR PRIMARY KEY,
    exception_id VARCHAR NOT NULL REFERENCES exceptions(id) ON DELETE CASCADE,
    feature_name VARCHAR NOT NULL,
    value FLOAT,
    threshold FLOAT,
    passed INTEGER,
    explanation VARCHAR
);

CREATE TABLE IF NOT EXISTS audit_events (
    id VARCHAR PRIMARY KEY,
    run_id VARCHAR REFERENCES reconciliation_runs(id) ON DELETE CASCADE,
    action VARCHAR NOT NULL,
    entity_type VARCHAR NOT NULL,
    entity_id VARCHAR NOT NULL,
    actor VARCHAR NOT NULL,
    metadata_json JSON,
    created_at TIMESTAMP WITHOUT TIME ZONE
);
