INSERT INTO wasm_uploads (tx_hash, wasm_hash, uploader, size, source_repo, meta, ledger, uploaded_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
ON CONFLICT DO NOTHING
