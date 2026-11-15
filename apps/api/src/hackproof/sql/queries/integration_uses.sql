SELECT
    partner AS slug,
    method,
    evidence,
    path
FROM repo_integrations
WHERE full_name = $1
ORDER BY partner, method, evidence
