SELECT
    c.login,
    max(c.avatar_url) AS avatar_url,
    count(DISTINCT c.full_name) AS projects,
    sum(c.contributions)::int AS contributions,
    array_agg(DISTINCT c.full_name ORDER BY c.full_name) AS project_names
FROM repo_contributors AS c INNER JOIN projects AS p ON c.full_name = p.full_name
WHERE p.tier IN ('verified', 'likely') AND lower(c.login) <> all($1::text[]) AND c.login NOT LIKE '%[bot]'
GROUP BY c.login
HAVING count(DISTINCT c.full_name) >= $2
ORDER BY projects DESC, contributions DESC, c.login ASC
LIMIT $3
