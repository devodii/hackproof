SELECT
    team_size AS label,
    count(*) AS value
FROM (
    SELECT
        c.full_name,
        least(count(*), 5)::text AS team_size
    FROM repo_contributors AS c INNER JOIN projects AS p ON c.full_name = p.full_name
    WHERE p.tier IN ('verified', 'likely') AND lower(c.login) <> all($1::text[]) AND c.login NOT LIKE '%[bot]'
    GROUP BY c.full_name
) AS teams
GROUP BY team_size
ORDER BY team_size
