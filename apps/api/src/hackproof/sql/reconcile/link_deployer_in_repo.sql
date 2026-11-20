INSERT INTO links (full_name, subject_kind, subject, method)
SELECT
    r.full_name,
    'account' AS subject_kind,
    r.value AS subject,
    $1::text AS method
FROM repo_refs AS r
WHERE
    r.full_name IN (
        SELECT o.full_name FROM repos AS o
        WHERE o.hackathon = $7
    )
    AND r.kind = 'account'
    AND r.value IN (SELECT hackers($2, $3, $4) AS account)
    AND r.value <> all($5::text[])
    AND r.value NOT IN (
        SELECT x.value FROM repo_refs AS x
        WHERE x.kind = 'account'
        GROUP BY x.value
        HAVING count(*) > $6
    )
ON CONFLICT DO NOTHING
