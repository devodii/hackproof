CREATE OR REPLACE FUNCTION method_rank(
    method text
)
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

CREATE OR REPLACE VIEW attribution AS
 SELECT DISTINCT ON (l.subject_kind, l.subject) l.subject_kind,
    l.subject,
    l.full_name,
    l.method
   FROM links l
     JOIN repos r ON l.full_name = r.full_name
  ORDER BY l.subject_kind, l.subject, (method_rank(l.method)), r.created_at, l.full_name;
