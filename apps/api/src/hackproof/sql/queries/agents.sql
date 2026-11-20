SELECT
    a.agent AS slug,
    count(DISTINCT a.full_name) AS projects
FROM repo_agents AS a
INNER JOIN projects AS p ON a.full_name = p.full_name AND p.hackathon = $1 AND p.tier IN ('verified', 'likely')
GROUP BY a.agent
