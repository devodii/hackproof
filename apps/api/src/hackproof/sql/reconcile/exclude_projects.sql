DELETE FROM projects
WHERE lower(project_id) = any($1)
