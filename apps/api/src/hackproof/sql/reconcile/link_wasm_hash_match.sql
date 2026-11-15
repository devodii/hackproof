INSERT INTO links (full_name, subject_kind, subject, method)
SELECT
    r.full_name,
    'wasm' AS subject_kind,
    r.value AS subject,
    $1::text AS method
FROM repo_refs AS r
WHERE
    r.kind = 'wasm'
    AND (
        r.value IN (SELECT w.wasm_hash FROM wasm_uploads AS w)
        OR r.value IN (SELECT c.wasm_hash FROM contracts AS c)
    )
ON CONFLICT DO NOTHING
