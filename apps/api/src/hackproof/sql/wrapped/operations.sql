SELECT
    op_type AS label,
    count(*) AS value
FROM classic_ops
WHERE occurred_at BETWEEN $1 AND $2
GROUP BY op_type
ORDER BY value DESC, op_type ASC
LIMIT 5
