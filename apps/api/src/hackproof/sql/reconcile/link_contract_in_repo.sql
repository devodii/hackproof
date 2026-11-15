INSERT INTO links (full_name, subject_kind, subject, method)
SELECT
    r.full_name,
    'contract' AS subject_kind,
    r.value AS subject,
    $1::text AS method
FROM repo_refs AS r
WHERE
    r.kind = 'contract'
    AND r.value IN (SELECT c.contract_id FROM contracts AS c)
ON CONFLICT DO NOTHING
