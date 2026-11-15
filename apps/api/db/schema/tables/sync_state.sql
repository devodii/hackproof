CREATE TABLE sync_state (
    key text,
    value text NOT NULL,
    CONSTRAINT sync_state_pkey PRIMARY KEY (key)
);
