INSERT INTO repo_contributors (full_name, login, url, avatar_url, contributions)
VALUES ($1, $2, $3, $4, $5)
ON CONFLICT (full_name, login) DO UPDATE SET
    contributions = excluded.contributions,
    avatar_url = excluded.avatar_url
