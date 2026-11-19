SELECT DISTINCT o.asset
FROM classic_ops AS o
WHERE
    o.asset IS NOT NULL
    AND o.asset NOT IN (SELECT a.asset FROM asset_contracts AS a)
