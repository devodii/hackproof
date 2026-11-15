INSERT INTO repos (
    full_name, url, description, stars, owner, owner_avatar,
    default_branch, homepage, language, license, forks, created_at,
    pushed_at, topics, window_commits, total_commits, base_sha,
    owner_location, country, discovered_via
)
VALUES (
    $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16,
    $17, $18, $19, $20
)
ON CONFLICT (full_name) DO UPDATE SET
    description = excluded.description, stars = excluded.stars,
    default_branch = excluded.default_branch, homepage = excluded.homepage,
    language = excluded.language, license = excluded.license, forks = excluded.forks,
    pushed_at = excluded.pushed_at, topics = excluded.topics,
    window_commits = excluded.window_commits, total_commits = excluded.total_commits,
    base_sha = excluded.base_sha, owner_location = excluded.owner_location,
    country = excluded.country,
    discovered_via = ARRAY(
        SELECT DISTINCT via FROM UNNEST(repos.discovered_via || excluded.discovered_via) AS via -- noqa: RF01
    )
