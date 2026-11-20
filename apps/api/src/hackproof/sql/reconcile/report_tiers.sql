SELECT
    tier,
    count(*) AS n
FROM projects
WHERE hackathon = $1
GROUP BY tier
