SELECT
    g.hour,
    count(c.contract_id) AS contracts
FROM
    generate_series($1::timestamptz, $2::timestamptz - interval '1 hour', interval '1 hour')
        AS g (hour)
LEFT JOIN contracts AS c ON g.hour <= c.deployed_at AND c.deployed_at < g.hour + interval '1 hour'
GROUP BY g.hour
ORDER BY g.hour
