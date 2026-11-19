SELECT
    contract_id,
    network,
    snapshot,
    observed_at
FROM integration_contracts
WHERE partner = $1
