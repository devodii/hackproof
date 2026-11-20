SELECT
    r.full_name,
    r.url,
    r.owner,
    r.default_branch,
    r.homepage,
    r.base_sha
FROM repos AS r
WHERE
    r.hackathon = $3
    AND ($1 OR r.scanned_at IS NULL)
    AND ($2 IS FALSE OR r.full_name IN (
        SELECT p.full_name FROM projects AS p
        WHERE p.full_name IS NOT NULL
    ))
    AND (COALESCE(r.window_commits, 0) > 0 OR 'wasm_meta' = ANY(r.discovered_via))
ORDER BY r.pushed_at DESC NULLS LAST
