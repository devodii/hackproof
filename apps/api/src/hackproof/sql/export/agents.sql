SELECT
    full_name,
    agent,
    method,
    evidence,
    path
FROM repo_agents
WHERE full_name = ANY($1)
ORDER BY agent, method, evidence
