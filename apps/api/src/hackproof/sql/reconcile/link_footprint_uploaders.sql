INSERT INTO links (full_name, subject_kind, subject, method)
SELECT
    l.full_name,
    'account' AS subject_kind,
    w.uploader AS subject,
    $1::text AS method
FROM links AS l
INNER JOIN wasm_uploads AS w ON l.subject_kind = 'wasm' AND l.subject = w.wasm_hash
WHERE
    l.subject IN (
        SELECT s.wasm_hash FROM wasm_uploads AS s
        GROUP BY s.wasm_hash
        HAVING count(DISTINCT s.uploader) = 1
    )
ON CONFLICT DO NOTHING
