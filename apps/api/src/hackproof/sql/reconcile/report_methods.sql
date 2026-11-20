SELECT
    l.method,
    count(*) AS n
FROM links AS l
INNER JOIN repos AS r ON l.full_name = r.full_name
WHERE r.hackathon = $1
GROUP BY l.method
