WITH assets AS (
    SELECT DISTINCT
        a.asset,
        a.contract_id
    FROM links AS l
    INNER JOIN projects AS p ON l.full_name = p.full_name AND p.hackathon = $2 AND p.tier IN ('verified', 'likely')
    INNER JOIN asset_contracts AS a ON l.subject = a.asset
    WHERE l.subject_kind = 'asset'
)

SELECT
    c.contract_id,
    count(DISTINCT a.asset) AS matched,
    (SELECT count(*) FROM assets) AS total
FROM integration_contracts AS c
LEFT JOIN assets AS a
    ON
        a.contract_id IN (
            SELECT jsonb_array_elements_text(c.snapshot -> 'items')
        )
WHERE c.partner = $1
GROUP BY c.contract_id
