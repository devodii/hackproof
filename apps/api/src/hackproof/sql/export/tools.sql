SELECT
    full_name,
    tool,
    method,
    evidence,
    path
FROM repo_tools
WHERE full_name = ANY($1)
ORDER BY tool, method, evidence
