INSERT INTO contracts (contract_id, deployer, wasm_hash, tx_hash, ledger, deployed_at)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT DO NOTHING
