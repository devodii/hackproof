INSERT INTO failed_txs (tx_hash, source_account, kind, result_code, ledger, created_at)
VALUES ($1, $2, $3, $4, $5, $6)
ON CONFLICT DO NOTHING
