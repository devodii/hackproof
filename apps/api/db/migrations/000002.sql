CREATE OR REPLACE FUNCTION hackers(
    window_start timestamptz,
    window_end timestamptz,
    friendbot text
)
RETURNS SETOF text
LANGUAGE sql
STABLE
AS $$
    SELECT account FROM accounts
    WHERE funder = friendbot AND funded_at BETWEEN window_start AND window_end
    UNION SELECT deployer FROM contracts
    UNION SELECT uploader FROM wasm_uploads
$$;
