SELECT
    c.login,
    c.url,
    c.avatar_url,
    c.contributions,
    u.country
FROM repo_contributors AS c
LEFT JOIN github_users AS u ON c.login = u.login
WHERE c.full_name = $1
ORDER BY c.contributions DESC, c.login ASC
