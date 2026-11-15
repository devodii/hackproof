INSERT INTO repo_refs (full_name, kind, value, path) VALUES ($1, $2, $3, $4)
ON CONFLICT DO NOTHING
