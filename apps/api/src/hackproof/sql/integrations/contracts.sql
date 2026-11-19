SELECT
    contract_id,
    snapshot,
    observed_at
FROM integration_contracts
WHERE partner = $1
