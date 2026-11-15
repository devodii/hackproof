CREATE OR REPLACE FUNCTION method_rank(method text)
RETURNS integer
LANGUAGE sql
IMMUTABLE
AS $$
    SELECT array_position(ARRAY[
        'contract_in_repo',
        'wasm_hash_match',
        'wasm_meta',
        'asset_in_repo',
        'deployer_in_repo',
        'footprint'
    ], method)
$$;
