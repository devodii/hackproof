WITH found AS (
    SELECT
        i.full_name,
        i.method,
        i.evidence,
        i.path
    FROM repo_integrations AS i
    WHERE i.partner = $1
    UNION ALL
    SELECT
        t.full_name,
        t.method,
        t.evidence,
        t.path
    FROM repo_tools AS t
    WHERE t.tool = $1
)

SELECT
    p.project_id,
    p.full_name,
    p.tier,
    r.url,
    r.owner,
    r.owner_avatar,
    r.language,
    f.method,
    f.evidence,
    f.path
FROM found AS f
INNER JOIN projects AS p ON f.full_name = p.full_name AND p.hackathon = $2 AND p.tier IN ('verified', 'likely')
INNER JOIN repos AS r ON p.full_name = r.full_name
ORDER BY p.project_id, f.method, f.evidence
