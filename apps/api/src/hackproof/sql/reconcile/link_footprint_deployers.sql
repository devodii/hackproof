INSERT INTO links (full_name, subject_kind, subject, method)
SELECT
    l.full_name,
    'account' AS subject_kind,
    c.deployer AS subject,
    $1::text AS method
FROM links AS l
INNER JOIN contracts AS c ON l.subject_kind = 'contract' AND l.subject = c.contract_id
ON CONFLICT DO NOTHING
