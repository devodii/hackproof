INSERT INTO integration_contracts (partner, contract_id, network, snapshot, observed_at)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (partner, network, contract_id) DO UPDATE SET
    snapshot = excluded.snapshot,
    observed_at = excluded.observed_at
