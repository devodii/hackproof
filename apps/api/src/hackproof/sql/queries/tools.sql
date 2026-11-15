SELECT
    t.tool AS slug,
    count(DISTINCT t.full_name) AS projects
FROM repo_tools AS t
INNER JOIN projects AS p ON t.full_name = p.full_name AND p.tier IN ('verified', 'likely')
GROUP BY t.tool
