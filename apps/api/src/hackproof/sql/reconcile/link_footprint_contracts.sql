INSERT INTO links (full_name, subject_kind, subject, method)
SELECT
    l.full_name,
    'contract' AS subject_kind,
    c.contract_id AS subject,
    $1::text AS method
FROM links AS l
INNER JOIN contracts AS c ON l.subject_kind = 'account' AND l.subject = c.deployer
ON CONFLICT DO NOTHING
