INSERT INTO accounts (account, funder, tx_hash, ledger, funded_at)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT DO NOTHING
