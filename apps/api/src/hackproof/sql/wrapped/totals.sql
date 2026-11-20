SELECT
    (
        SELECT count(DISTINCT c.login) FROM repo_contributors AS c
        INNER JOIN projects AS p ON c.full_name = p.full_name
        WHERE p.hackathon = $4 AND p.tier IN ('verified', 'likely') AND lower(c.login) <> all($1::text[]) AND c.login NOT LIKE '%[bot]'
    ) AS builders,
    (
        SELECT count(*) FROM accounts
        WHERE funded_at BETWEEN $2 AND $3
    ) AS accounts_funded,
    (
        SELECT count(DISTINCT deployer) FROM contracts
        WHERE deployed_at BETWEEN $2 AND $3
    ) AS deployers,
    (
        SELECT count(*) FROM classic_ops
        WHERE occurred_at BETWEEN $2 AND $3
    ) AS operations,
    (SELECT coalesce(max(n), 0) FROM (
        SELECT count(*) AS n FROM contracts
        WHERE deployed_at BETWEEN $2 AND $3
        GROUP BY wasm_hash
    ) AS shared) AS largest_wasm_contracts
