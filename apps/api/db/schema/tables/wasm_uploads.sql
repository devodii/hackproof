CREATE TABLE wasm_uploads (
    tx_hash text,
    wasm_hash text NOT NULL,
    uploader text NOT NULL,
    size bigint NOT NULL,
    source_repo text,
    meta jsonb NOT NULL,
    ledger bigint NOT NULL,
    uploaded_at timestamptz NOT NULL,
    CONSTRAINT wasm_uploads_pkey PRIMARY KEY (tx_hash)
);
