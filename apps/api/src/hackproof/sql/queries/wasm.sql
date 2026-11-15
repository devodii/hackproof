SELECT
    w.wasm_hash,
    w.uploader,
    w.tx_hash,
    w.size,
    w.source_repo,
    w.uploaded_at,
    COALESCE(aa.full_name, aw.full_name) AS full_name,
    (
        SELECT COUNT(*) FROM contracts AS c
        WHERE c.wasm_hash = w.wasm_hash
    ) AS contracts,
    COUNT(*) OVER () AS total
FROM wasm_uploads AS w
LEFT JOIN attribution AS aa ON aa.subject_kind = 'account' AND w.uploader = aa.subject
LEFT JOIN attribution AS aw ON aw.subject_kind = 'wasm' AND w.wasm_hash = aw.subject
WHERE
    w.uploaded_at BETWEEN $1 AND $2
    AND (
        $3::text IS NULL
        OR w.wasm_hash ILIKE '%' || $3 || '%'
        OR w.uploader ILIKE '%' || $3 || '%'
        OR w.source_repo ILIKE '%' || $3 || '%'
    )
    AND ($4::text IS NULL OR w.uploader = $4)
    AND (
        $5::text IS NULL
        OR COALESCE('repo:' || COALESCE(aa.full_name, aw.full_name), 'acct:' || w.uploader) = $5
    )
ORDER BY w.uploaded_at DESC
LIMIT $6 OFFSET $7
