SELECT r.full_name FROM repos AS r
WHERE
    r.hackathon = $3
    AND ($1 OR r.scanned_at IS NULL)
    AND ($2 IS FALSE OR r.full_name IN (
        SELECT p.full_name FROM projects AS p
        WHERE p.full_name IS NOT NULL
    ))
