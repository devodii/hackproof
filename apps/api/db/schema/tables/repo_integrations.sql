CREATE TABLE repo_integrations (
    full_name text,
    partner text,
    method text,
    evidence text,
    path text NOT NULL,
    CONSTRAINT repo_integrations_pkey PRIMARY KEY (full_name, partner, method, evidence)
);
