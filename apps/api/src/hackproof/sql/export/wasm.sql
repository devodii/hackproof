SELECT DISTINCT ON (a.full_name, w.wasm_hash)
    a.full_name,
    w.wasm_hash,
    w.tx_hash
FROM wasm_uploads AS w
INNER JOIN attribution AS a ON a.subject_kind = 'account' AND w.uploader = a.subject
WHERE a.full_name = ANY($1) AND w.uploaded_at BETWEEN $2 AND $3
ORDER BY a.full_name, w.wasm_hash, w.uploaded_at
