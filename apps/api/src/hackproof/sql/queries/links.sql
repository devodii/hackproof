SELECT
    l.subject_kind,
    l.subject,
    l.method,
    r.path
FROM links AS l
LEFT JOIN repo_refs AS r
    ON l.full_name = r.full_name AND l.subject_kind = r.kind AND l.subject = r.value
WHERE l.full_name = $1
ORDER BY method_rank(l.method), l.subject_kind, l.subject
