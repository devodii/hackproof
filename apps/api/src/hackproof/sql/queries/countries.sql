SELECT
    u.country,
    count(DISTINCT c.login) AS contributors
FROM repo_contributors AS c
INNER JOIN projects AS p ON c.full_name = p.full_name AND p.tier IN ('verified', 'likely')
INNER JOIN github_users AS u ON c.login = u.login
WHERE u.country IS NOT NULL
GROUP BY u.country
ORDER BY contributors DESC, u.country ASC
LIMIT $1
