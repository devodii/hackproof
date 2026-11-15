SELECT
    c.contract_id,
    c.deployer,
    c.wasm_hash,
    c.tx_hash,
    c.ledger,
    c.deployed_at,
    COALESCE('repo:' || a.full_name, 'acct:' || c.deployer) AS project_id,
    COUNT(*) OVER () AS total
FROM contracts AS c
LEFT JOIN attribution AS a ON a.subject_kind = 'contract' AND c.contract_id = a.subject
WHERE
    c.deployed_at BETWEEN $1 AND $2
    AND (
        $3::text IS NULL
        OR c.contract_id ILIKE '%' || $3 || '%'
        OR c.deployer ILIKE '%' || $3 || '%'
        OR c.wasm_hash ILIKE '%' || $3 || '%'
    )
    AND ($4::text IS NULL OR c.deployer = $4)
    AND ($5::text IS NULL OR COALESCE('repo:' || a.full_name, 'acct:' || c.deployer) = $5)
ORDER BY c.deployed_at DESC
LIMIT $6 OFFSET $7
