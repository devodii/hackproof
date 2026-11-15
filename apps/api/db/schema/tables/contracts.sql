CREATE TABLE contracts (
    contract_id text,
    deployer text NOT NULL,
    wasm_hash text NOT NULL,
    tx_hash text NOT NULL,
    ledger bigint NOT NULL,
    deployed_at timestamptz NOT NULL,
    CONSTRAINT contracts_pkey PRIMARY KEY (contract_id)
);
