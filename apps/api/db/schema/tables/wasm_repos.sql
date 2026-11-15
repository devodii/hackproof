CREATE TABLE wasm_repos (
    wasm_hash text,
    full_name text NOT NULL,
    source text NOT NULL,
    CONSTRAINT wasm_repos_pkey PRIMARY KEY (wasm_hash)
);
