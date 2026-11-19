CREATE TABLE integration_contracts (
    partner text,
    contract_id text,
    network text NOT NULL,
    snapshot jsonb NOT NULL,
    observed_at timestamptz NOT NULL,
    CONSTRAINT integration_contracts_pkey PRIMARY KEY (partner, contract_id)
);
