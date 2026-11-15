SELECT
    a.full_name,
    c.contract_id,
    c.deployer,
    c.wasm_hash,
    c.deployed_at,
    c.ledger,
    c.tx_hash
FROM contracts AS c
INNER JOIN attribution AS a ON a.subject_kind = 'contract' AND c.contract_id = a.subject
WHERE a.full_name = ANY($1) AND c.deployed_at BETWEEN $2 AND $3
ORDER BY c.deployed_at
