CREATE TABLE repo_refs (
    full_name text,
    kind text,
    value text,
    path text NOT NULL,
    CONSTRAINT repo_refs_pkey PRIMARY KEY (full_name, kind, value)
);
