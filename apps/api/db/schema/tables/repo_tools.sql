CREATE TABLE repo_tools (
    full_name text,
    tool text,
    method text,
    evidence text,
    path text NOT NULL,
    CONSTRAINT repo_tools_pkey PRIMARY KEY (full_name, tool, method, evidence)
);
