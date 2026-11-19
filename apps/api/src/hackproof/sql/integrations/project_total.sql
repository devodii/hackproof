SELECT count(*) AS total FROM projects
WHERE tier IN ('verified', 'likely')
