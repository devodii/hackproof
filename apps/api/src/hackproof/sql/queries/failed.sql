SELECT
    f.tx_hash,
    f.source_account,
    f.kind,
    f.result_code,
    f.ledger,
    f.created_at,
    count(*) OVER () AS total
FROM failed_txs AS f
LEFT JOIN account_projects AS ap ON f.source_account = ap.account
WHERE
    f.created_at BETWEEN $1 AND $2
    AND (
        $3::text IS NULL
        OR f.tx_hash ILIKE '%' || $3 || '%'
        OR f.source_account ILIKE '%' || $3 || '%'
        OR f.result_code ILIKE '%' || $3 || '%'
    )
    AND ($4::text IS NULL OR f.source_account = $4)
    AND ($5::text IS NULL OR coalesce(ap.project_id, 'acct:' || f.source_account) = $5)
ORDER BY f.created_at DESC
LIMIT $6 OFFSET $7
