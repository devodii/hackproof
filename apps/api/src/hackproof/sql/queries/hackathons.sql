SELECT
    hackathon,
    count(*) FILTER (WHERE tier IN ('verified', 'likely')) AS projects,
    count(*) FILTER (WHERE tier = 'verified') AS verified_projects,
    coalesce(sum(contracts) FILTER (WHERE tier IN ('verified', 'likely')), 0)::int AS contracts
FROM projects
GROUP BY hackathon
