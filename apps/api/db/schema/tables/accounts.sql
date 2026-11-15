CREATE TABLE accounts (
    account text,
    funder text NOT NULL,
    tx_hash text NOT NULL,
    ledger bigint NOT NULL,
    funded_at timestamptz NOT NULL,
    CONSTRAINT accounts_pkey PRIMARY KEY (account)
);
