CREATE TABLE failed_txs (
    tx_hash text,
    source_account text NOT NULL,
    kind text NOT NULL,
    result_code text NOT NULL,
    ledger bigint NOT NULL,
    created_at timestamptz NOT NULL,
    CONSTRAINT failed_txs_pkey PRIMARY KEY (tx_hash)
);
