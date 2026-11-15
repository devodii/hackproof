SELECT
    i.partner AS slug,
    count(DISTINCT i.full_name) AS projects
FROM repo_integrations AS i
INNER JOIN projects AS p ON i.full_name = p.full_name AND p.tier IN ('verified', 'likely')
GROUP BY i.partner
