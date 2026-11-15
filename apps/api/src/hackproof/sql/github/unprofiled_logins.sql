SELECT DISTINCT c.login FROM repo_contributors AS c
WHERE c.login NOT IN (SELECT u.login FROM github_users AS u)
