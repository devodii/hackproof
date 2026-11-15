SELECT
    method,
    count(*) AS n
FROM links
GROUP BY method
