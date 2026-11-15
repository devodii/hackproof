SELECT
    footprint,
    count(*) AS n
FROM projects
GROUP BY footprint
