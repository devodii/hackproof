CREATE TABLE projects (
    project_id text,
    hackathon text DEFAULT 'hackmeridian-2026' NOT NULL,
    full_name text,
    footprint text NOT NULL,
    tier text NOT NULL,
    contracts integer NOT NULL,
    classic_ops integer NOT NULL,
    assets integer NOT NULL,
    wasm_uploads integer NOT NULL,
    failed_txs integer NOT NULL,
    builders integer NOT NULL,
    first_activity timestamptz,
    last_activity timestamptz,
    CONSTRAINT projects_pkey PRIMARY KEY (project_id)
);
