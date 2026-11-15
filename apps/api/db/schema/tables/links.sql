CREATE TABLE links (
    full_name text,
    subject_kind text,
    subject text,
    method text NOT NULL,
    CONSTRAINT links_pkey PRIMARY KEY (subject_kind, subject, full_name)
);
