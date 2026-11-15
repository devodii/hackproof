INSERT INTO projects (
    project_id, full_name, footprint, tier, contracts, classic_ops, assets,
    wasm_uploads, failed_txs, builders, first_activity, last_activity
)
WITH builders AS (
    SELECT c.deployer AS account FROM contracts AS c
    WHERE c.deployed_at BETWEEN $1 AND $2
    UNION
    SELECT w.uploader FROM wasm_uploads AS w
    WHERE w.uploaded_at BETWEEN $1 AND $2
    UNION
    SELECT split_part(x.asset, ':', 2) FROM classic_ops AS x
    WHERE
        x.asset IS NOT NULL AND x.occurred_at BETWEEN $1 AND $2
        AND split_part(x.asset, ':', 2) IN (SELECT hackers($1, $2, $3) AS account)
),

orphans AS (
    SELECT b.account FROM builders AS b
    WHERE b.account NOT IN (
        SELECT l.subject FROM links AS l
        WHERE l.subject_kind = 'account'
    )
)

SELECT
    'acct:' || o.account AS project_id,
    NULL AS full_name,
    CASE WHEN EXISTS (
        SELECT 1 FROM contracts AS c
        WHERE c.deployer = o.account AND c.deployed_at BETWEEN $1 AND $2
    ) THEN 'contracts' ELSE 'classic' END AS footprint,
    'unattributed' AS tier,
    (
        SELECT count(*) FROM contracts AS c
        WHERE c.deployer = o.account AND c.deployed_at BETWEEN $1 AND $2
    ) AS contracts,
    (
        SELECT count(*) FROM classic_ops AS x
        WHERE x.source_account = o.account AND x.occurred_at BETWEEN $1 AND $2
    ) AS classic_ops,
    (
        SELECT count(DISTINCT x.asset) FROM classic_ops AS x
        WHERE split_part(x.asset, ':', 2) = o.account AND x.occurred_at BETWEEN $1 AND $2
    ) AS assets,
    (
        SELECT count(DISTINCT w.wasm_hash) FROM wasm_uploads AS w
        WHERE w.uploader = o.account AND w.uploaded_at BETWEEN $1 AND $2
    ) AS wasm_uploads,
    (
        SELECT count(*) FROM failed_txs AS f
        WHERE f.source_account = o.account AND f.created_at BETWEEN $1 AND $2
    ) AS failed_txs,
    1 AS builders,
    (
        SELECT min(t.at) FROM (
            SELECT c.deployed_at AS at FROM contracts AS c
            WHERE c.deployer = o.account
            UNION ALL
            SELECT w.uploaded_at AS at FROM wasm_uploads AS w
            WHERE w.uploader = o.account
            UNION ALL
            SELECT x.occurred_at AS at FROM classic_ops AS x
            WHERE x.source_account = o.account
        ) AS t
    ) AS first_activity,
    (
        SELECT max(t.at) FROM (
            SELECT c.deployed_at AS at FROM contracts AS c
            WHERE c.deployer = o.account
            UNION ALL
            SELECT w.uploaded_at AS at FROM wasm_uploads AS w
            WHERE w.uploader = o.account
            UNION ALL
            SELECT x.occurred_at AS at FROM classic_ops AS x
            WHERE x.source_account = o.account
        ) AS t
    ) AS last_activity
FROM orphans AS o
