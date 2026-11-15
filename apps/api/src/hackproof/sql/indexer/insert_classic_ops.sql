INSERT INTO classic_ops (tx_hash, op_index, source_account, op_type, asset, counterparty, ledger, occurred_at)
VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
ON CONFLICT DO NOTHING
