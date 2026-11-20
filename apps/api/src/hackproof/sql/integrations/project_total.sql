SELECT count(*) AS total FROM projects
WHERE ($1::text IS NULL OR hackathon = $1) AND tier IN ('verified', 'likely')
