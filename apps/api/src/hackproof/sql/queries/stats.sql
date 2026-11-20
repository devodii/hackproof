SELECT
    (
        SELECT count(*) FROM projects
        WHERE hackathon = $3 AND tier IN ('verified', 'likely')
    ) AS projects,
    (
        SELECT count(*) FROM projects
        WHERE hackathon = $3 AND tier = 'verified'
    ) AS verified_projects,
    (
        SELECT count(*) FROM projects
        WHERE hackathon = $3 AND tier = 'likely'
    ) AS likely_projects,
    (
        SELECT count(*) FROM projects
        WHERE hackathon = $3 AND tier = 'possible'
    ) AS possible_projects,
    (
        SELECT count(*) FROM projects
        WHERE hackathon = $3 AND tier = 'unattributed'
    ) AS unattributed_accounts,
    (
        SELECT count(*) FROM contracts
        WHERE deployed_at BETWEEN $1 AND $2
    ) AS contracts,
    (SELECT count(*) FROM (
        SELECT deployer FROM contracts
        WHERE deployed_at BETWEEN $1 AND $2
        UNION
        SELECT uploader FROM wasm_uploads
        WHERE uploaded_at BETWEEN $1 AND $2
    ) AS builders)
        AS builders,
    (
        SELECT count(DISTINCT c.login) FROM repo_contributors AS c
        INNER JOIN projects AS p ON c.full_name = p.full_name
        WHERE p.hackathon = $3 AND p.tier IN ('verified', 'likely')
    ) AS contributors,
    (SELECT count(DISTINCT country) FROM (
        SELECT r.country FROM projects AS p INNER JOIN repos AS r ON p.full_name = r.full_name
        WHERE p.hackathon = $3 AND p.tier IN ('verified', 'likely')
        UNION
        SELECT u.country FROM projects AS p
        INNER JOIN repo_contributors AS c ON p.full_name = c.full_name
        INNER JOIN github_users AS u ON c.login = u.login
        WHERE p.hackathon = $3 AND p.tier IN ('verified', 'likely')
    ) AS found
    WHERE country IS NOT NULL) AS countries,
    (
        SELECT count(*) FROM wasm_uploads
        WHERE uploaded_at BETWEEN $1 AND $2
    ) AS wasm_uploads,
    (
        SELECT count(*) FROM failed_txs
        WHERE created_at BETWEEN $1 AND $2
    ) AS failed_txs
