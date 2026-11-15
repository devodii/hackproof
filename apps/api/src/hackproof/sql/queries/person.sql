SELECT
    c.login,
    c.url,
    c.avatar_url,
    c.contributions,
    c.full_name,
    u.country
FROM repo_contributors AS c
LEFT JOIN github_users AS u ON c.login = u.login
WHERE lower(c.login) = lower($1)
ORDER BY c.contributions DESC, c.full_name ASC
