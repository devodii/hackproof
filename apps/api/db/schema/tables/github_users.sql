CREATE TABLE github_users (
    login text,
    location text,
    country text,
    fetched_at timestamptz DEFAULT now() NOT NULL,
    CONSTRAINT github_users_pkey PRIMARY KEY (login)
);
