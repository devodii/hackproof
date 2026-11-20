INSERT INTO links (full_name, subject_kind, subject, method)
SELECT
    r.full_name,
    'asset' AS subject_kind,
    r.value AS subject,
    $1::text AS method
FROM repo_refs AS r
WHERE
    r.full_name IN (
        SELECT o.full_name FROM repos AS o
        WHERE o.hackathon = $5
    )
    AND r.kind = 'asset'
    AND split_part(r.value, ':', 2) IN (SELECT hackers($2, $3, $4) AS account)
    AND r.value IN (
        SELECT o.asset FROM classic_ops AS o
        WHERE o.asset IS NOT NULL AND o.occurred_at BETWEEN $2 AND $3
    )
ON CONFLICT DO NOTHING
