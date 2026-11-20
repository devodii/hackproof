SELECT
    footprint,
    count(*) AS n
FROM projects
WHERE hackathon = $1
GROUP BY footprint
