ALTER TABLE projects ADD COLUMN hackathon text DEFAULT 'hackmeridian-2026' NOT NULL;

ALTER TABLE projects DROP CONSTRAINT projects_pkey;

ALTER TABLE projects
ADD CONSTRAINT projects_pkey PRIMARY KEY (hackathon, project_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS projects_hackathon ON projects (hackathon);

-- pgschema:wait
SELECT 
    COALESCE(i.indisvalid, false) as done,
    CASE 
        WHEN p.blocks_total > 0 THEN p.blocks_done * 100 / p.blocks_total
        ELSE 0
    END as progress
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
LEFT JOIN pg_index i ON c.oid = i.indexrelid
LEFT JOIN pg_stat_progress_create_index p ON c.oid = p.index_relid
WHERE c.relname = 'projects_hackathon'
  AND n.nspname = 'public';

ALTER TABLE repos ADD COLUMN hackathon text DEFAULT 'hackmeridian-2026' NOT NULL;

CREATE INDEX CONCURRENTLY IF NOT EXISTS repos_hackathon ON repos (hackathon);

-- pgschema:wait
SELECT 
    COALESCE(i.indisvalid, false) as done,
    CASE 
        WHEN p.blocks_total > 0 THEN p.blocks_done * 100 / p.blocks_total
        ELSE 0
    END as progress
FROM pg_class c
JOIN pg_namespace n ON c.relnamespace = n.oid
LEFT JOIN pg_index i ON c.oid = i.indexrelid
LEFT JOIN pg_stat_progress_create_index p ON c.oid = p.index_relid
WHERE c.relname = 'repos_hackathon'
  AND n.nspname = 'public';
