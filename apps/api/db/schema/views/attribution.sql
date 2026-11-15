CREATE OR REPLACE VIEW attribution AS
SELECT DISTINCT ON (l.subject_kind, l.subject)
    l.subject_kind,
    l.subject,
    l.full_name,
    l.method
FROM links AS l
INNER JOIN repos AS r ON l.full_name = r.full_name
ORDER BY l.subject_kind, l.subject, method_rank(l.method), r.created_at, l.full_name;
