INSERT INTO github_users (login, location, country) VALUES ($1, $2, $3)
ON CONFLICT (login) DO NOTHING
