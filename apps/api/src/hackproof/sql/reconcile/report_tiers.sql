SELECT
    tier,
    count(*) AS n
FROM projects
GROUP BY tier
