SELECT
    p.project_id,
    p.full_name,
    p.tier,
    r.url,
    r.owner,
    r.owner_avatar,
    r.language,
    i.method,
    i.evidence,
    i.path
FROM repo_integrations AS i
INNER JOIN projects AS p ON i.full_name = p.full_name AND p.tier IN ('verified', 'likely')
INNER JOIN repos AS r ON p.full_name = r.full_name
WHERE i.partner = $1
ORDER BY p.project_id, i.method, i.evidence
