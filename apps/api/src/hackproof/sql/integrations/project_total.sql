SELECT count(*) AS total FROM projects
WHERE hackathon = $1 AND tier IN ('verified', 'likely')
