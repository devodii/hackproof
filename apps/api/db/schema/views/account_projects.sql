CREATE OR REPLACE VIEW account_projects AS
SELECT
    subject AS account,
    'repo:'::text || full_name AS project_id
FROM attribution
WHERE subject_kind = 'account'::text;
