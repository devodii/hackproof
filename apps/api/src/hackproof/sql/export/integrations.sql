SELECT
    full_name,
    partner,
    method,
    evidence,
    path
FROM repo_integrations
WHERE full_name = ANY($1)
ORDER BY partner, method, evidence
