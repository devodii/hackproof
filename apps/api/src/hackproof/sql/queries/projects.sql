SELECT
    p.project_id,
    p.hackathon,
    p.full_name,
    r.url,
    p.footprint,
    p.tier,
    p.contracts,
    p.classic_ops,
    p.assets,
    p.builders,
    p.wasm_uploads,
    p.failed_txs,
    p.first_activity,
    p.last_activity,
    r.description,
    r.homepage,
    r.stars,
    r.forks,
    r.language,
    r.license,
    r.owner,
    r.owner_avatar,
    r.country,
    r.dependencies,
    r.window_commits,
    r.total_commits,
    r.stellar_added_in_window,
    r.created_at,
    r.topics,
    COALESCE(r.declared_track, 'genesis') AS track,
    ARRAY(
        SELECT i.partner FROM repo_integrations AS i
        WHERE i.full_name = p.full_name
        GROUP BY i.partner
        ORDER BY i.partner
    ) AS integrations,
    ARRAY(
        SELECT t.tool FROM repo_tools AS t
        WHERE t.full_name = p.full_name
        GROUP BY t.tool
        ORDER BY t.tool
    ) AS tools,
    ARRAY(
        SELECT a.agent FROM repo_agents AS a
        WHERE a.full_name = p.full_name
        GROUP BY a.agent
        ORDER BY a.agent
    ) AS agents,
    COUNT(*) OVER () AS total
FROM projects AS p
LEFT JOIN repos AS r ON p.full_name = r.full_name
WHERE
    ($15::text IS NULL OR p.hackathon = $15)
    AND (
        $1::text IS NULL
        OR p.project_id ILIKE '%' || $1 || '%'
        OR r.description ILIKE '%' || $1 || '%'
    )
    AND (
        $2::text IS NULL
        OR p.project_id = 'acct:' || $2
        OR p.project_id IN (
            SELECT ap.project_id FROM account_projects AS ap
            WHERE ap.account = $2
        )
    )
    AND ($3::text IS NULL OR p.project_id = $3)
    AND ($4::text[] IS NULL OR p.tier = ANY($4))
    AND ($7::text IS NULL OR COALESCE(r.declared_track, 'genesis') = $7)
    AND ($8::text[] IS NULL OR EXISTS (
        SELECT 1 FROM repo_integrations AS i
        WHERE i.full_name = p.full_name AND i.partner = ANY($8)
    ))
    AND ($9::text[] IS NULL OR p.project_id = ANY($9))
    AND ($10::text[] IS NULL OR EXISTS (
        SELECT 1 FROM repo_tools AS t
        WHERE t.full_name = p.full_name AND t.tool = ANY($10)
    ))
    AND ($11::text[] IS NULL OR EXISTS (
        SELECT 1 FROM repo_agents AS a
        WHERE a.full_name = p.full_name AND a.agent = ANY($11)
    ))
    AND ($12::text[] IS NULL OR r.language = ANY($12))
    AND ($13::text[] IS NULL OR r.country = ANY($13))
    AND (
        $14::text[] IS NULL
        OR ('contracts' = ANY($14) AND p.contracts > 0)
        OR ('failed' = ANY($14) AND p.failed_txs > 0)
    )
ORDER BY
    ARRAY_POSITION(
        ARRAY['verified', 'likely', 'possible', 'unattributed'], p.tier
    ),
    p.contracts DESC, p.classic_ops DESC, r.stars DESC NULLS LAST, p.last_activity DESC
LIMIT $5 OFFSET $6
