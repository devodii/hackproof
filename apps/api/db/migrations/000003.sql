CREATE TABLE IF NOT EXISTS asset_contracts (
    asset text,
    contract_id text NOT NULL,
    CONSTRAINT asset_contracts_pkey PRIMARY KEY (asset)
);

CREATE INDEX IF NOT EXISTS asset_contracts_contract ON asset_contracts (contract_id);

CREATE TABLE IF NOT EXISTS integration_contracts (
    partner text,
    contract_id text,
    network text NOT NULL,
    snapshot jsonb NOT NULL,
    observed_at timestamptz NOT NULL,
    CONSTRAINT integration_contracts_pkey PRIMARY KEY (partner, contract_id)
);
