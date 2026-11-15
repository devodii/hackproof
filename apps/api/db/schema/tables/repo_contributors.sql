CREATE TABLE repo_contributors (
    full_name text,
    login text,
    url text NOT NULL,
    avatar_url text,
    contributions integer NOT NULL,
    CONSTRAINT repo_contributors_pkey PRIMARY KEY (full_name, login)
);
