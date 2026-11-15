INSERT INTO projects (
    project_id, full_name, footprint, tier, contracts, classic_ops, assets,
    wasm_uploads, failed_txs, builders, first_activity, last_activity
)
WITH contract_stats AS (
    SELECT
        a.full_name,
        count(*) AS contracts,
        count(DISTINCT c.deployer) AS builders,
        min(c.deployed_at) AS first_at,
        max(c.deployed_at) AS last_at
    FROM contracts AS c
    INNER JOIN attribution AS a ON a.subject_kind = 'contract' AND c.contract_id = a.subject
    WHERE c.deployed_at BETWEEN $1 AND $2
    GROUP BY a.full_name
),

op_stats AS (
    SELECT
        a.full_name,
        count(*) AS classic_ops
    FROM classic_ops AS o
    INNER JOIN attribution AS a ON a.subject_kind = 'account' AND o.source_account = a.subject
    WHERE o.occurred_at BETWEEN $1 AND $2
    GROUP BY a.full_name
),

asset_stats AS (
    SELECT
        t.full_name,
        count(*) AS assets
    FROM attribution AS t
    WHERE t.subject_kind = 'asset'
    GROUP BY t.full_name
),

wasm_stats AS (
    SELECT
        coalesce(aa.full_name, aw.full_name) AS full_name,
        count(DISTINCT w.wasm_hash) AS wasm
    FROM wasm_uploads AS w
    LEFT JOIN attribution AS aa ON aa.subject_kind = 'account' AND w.uploader = aa.subject
    LEFT JOIN attribution AS aw ON aw.subject_kind = 'wasm' AND w.wasm_hash = aw.subject
    WHERE w.uploaded_at BETWEEN $1 AND $2
    GROUP BY coalesce(aa.full_name, aw.full_name)
),

failed_stats AS (
    SELECT
        a.full_name,
        count(*) AS failed
    FROM failed_txs AS f
    INNER JOIN attribution AS a ON a.subject_kind = 'account' AND f.source_account = a.subject
    WHERE f.created_at BETWEEN $1 AND $2
    GROUP BY a.full_name
)

SELECT
    'repo:' || r.full_name AS project_id,
    r.full_name,
    CASE
        WHEN coalesce(cs.contracts, 0) > 0 THEN 'contracts'
        WHEN coalesce(os.classic_ops, 0) + coalesce(ast.assets, 0) > 0 THEN 'classic'
        ELSE 'github'
    END AS footprint,
    CASE
        WHEN
            EXISTS (
                SELECT 1 FROM links AS l
                WHERE l.full_name = r.full_name
            )
            AND coalesce(cs.contracts, 0) + coalesce(os.classic_ops, 0)
            + coalesce(ast.assets, 0) + coalesce(ws.wasm, 0) + coalesce(fs.failed, 0) > 0
            THEN 'verified'
        WHEN
            jsonb_array_length(r.dependencies -> 'ecosystems') > 0
            AND coalesce(r.window_commits, 0) >= $4
            AND (
                r.created_at BETWEEN $1 AND $2
                OR coalesce(r.stellar_added_in_window, FALSE)
            ) THEN 'likely'
        ELSE 'possible'
    END AS tier,
    coalesce(cs.contracts, 0) AS contracts,
    coalesce(os.classic_ops, 0) AS classic_ops,
    coalesce(ast.assets, 0) AS assets,
    coalesce(ws.wasm, 0) AS wasm_uploads,
    coalesce(fs.failed, 0) AS failed_txs,
    coalesce(cs.builders, 0) AS builders,
    coalesce(cs.first_at, r.pushed_at) AS first_activity,
    coalesce(cs.last_at, r.pushed_at) AS last_activity
FROM repos AS r
LEFT JOIN contract_stats AS cs ON r.full_name = cs.full_name
LEFT JOIN op_stats AS os ON r.full_name = os.full_name
LEFT JOIN asset_stats AS ast ON r.full_name = ast.full_name
LEFT JOIN wasm_stats AS ws ON r.full_name = ws.full_name
LEFT JOIN failed_stats AS fs ON r.full_name = fs.full_name
WHERE
    r.full_name IN (SELECT l.full_name FROM links AS l)
    OR 'wasm_meta' = any(r.discovered_via)
    OR (
        jsonb_array_length(r.dependencies -> 'ecosystems') > 0
        AND (
            coalesce(r.window_commits, 0) >= $3
            OR coalesce(r.stellar_added_in_window, FALSE)
            OR r.created_at BETWEEN $1 AND $2
        )
    )
