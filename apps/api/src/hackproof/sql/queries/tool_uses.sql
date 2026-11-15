SELECT
    tool AS slug,
    method,
    evidence,
    path
FROM repo_tools
WHERE full_name = $1
ORDER BY tool, method, evidence
