CREATE TABLE classic_ops (
    tx_hash text,
    op_index integer,
    source_account text NOT NULL,
    op_type text NOT NULL,
    asset text,
    counterparty text,
    ledger bigint NOT NULL,
    occurred_at timestamptz NOT NULL,
    CONSTRAINT classic_ops_pkey PRIMARY KEY (tx_hash, op_index)
);
