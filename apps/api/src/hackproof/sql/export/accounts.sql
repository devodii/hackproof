SELECT
    full_name,
    subject
FROM links
WHERE subject_kind = 'account' AND full_name = ANY($1)
ORDER BY subject
