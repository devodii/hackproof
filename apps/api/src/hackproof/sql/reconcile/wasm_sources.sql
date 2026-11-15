SELECT DISTINCT
    wasm_hash,
    source_repo
FROM wasm_uploads
WHERE source_repo IS NOT NULL
