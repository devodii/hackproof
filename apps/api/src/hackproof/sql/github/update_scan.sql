UPDATE repos SET
    dependencies = $2,
    stellar_added_in_window = $3,
    declared_track = $4,
    scanned_at = now()
WHERE full_name = $1
