INSERT INTO links (full_name, subject_kind, subject, method)
WITH a AS (
    SELECT DISTINCT o.asset FROM classic_ops AS o
    WHERE o.asset IS NOT NULL
)

SELECT
    l.full_name,
    'asset' AS subject_kind,
    a.asset AS subject,
    $1::text AS method
FROM links AS l
INNER JOIN a ON l.subject_kind = 'account' AND split_part(a.asset, ':', 2) = l.subject
ON CONFLICT DO NOTHING
