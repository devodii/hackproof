DELETE FROM links
WHERE full_name IN (SELECT r.full_name FROM repos AS r WHERE r.hackathon = $1)
