SELECT
    p.full_name,
    p.tier,
    p.contracts,
    p.classic_ops,
    p.assets,
    p.wasm_uploads,
    p.failed_txs,
    r.url,
    r.description,
    r.homepage,
    r.language,
    r.license,
    r.stars,
    r.forks,
    r.topics,
    r.dependencies,
    r.created_at,
    r.pushed_at,
    r.window_commits,
    r.total_commits,
    r.owner,
    r.owner_avatar,
    r.country,
    r.declared_track
FROM projects AS p
INNER JOIN repos AS r ON p.full_name = r.full_name
WHERE p.tier = ANY($1) AND p.hackathon = $3
ORDER BY ARRAY_POSITION($2::text[], p.tier), p.contracts DESC, r.stars DESC, p.full_name ASC
