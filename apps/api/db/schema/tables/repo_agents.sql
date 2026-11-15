CREATE TABLE repo_agents (
    full_name text,
    agent text,
    method text,
    evidence text,
    path text NOT NULL,
    CONSTRAINT repo_agents_pkey PRIMARY KEY (full_name, agent, method, evidence)
);
