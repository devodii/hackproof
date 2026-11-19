INSERT INTO sync_state (key, value) VALUES ('event', $1) ON CONFLICT DO NOTHING
