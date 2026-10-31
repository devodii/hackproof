"""Project claim & edit overrides.

Overrides are stored in `project_edits` and applied at read time (see queries.py)
and in the export. They never mutate derived tables, so they survive reconcile.
"""

import os
import sqlite3
from datetime import datetime, timezone

EDITABLE = {"display_name", "tagline", "demo_url", "video_url", "track"}


def _now():
    return datetime.now(timezone.utc).isoformat()


def create_table(conn):
    conn.execute("""
        CREATE TABLE IF NOT EXISTS project_edits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            project_id INTEGER NOT NULL,
            field TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            contributor_login TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'pending',
            created_at TEXT NOT NULL,
            reviewed_by TEXT,
            reviewed_at TEXT,
            FOREIGN KEY (project_id) REFERENCES projects(id)
        )
    """)
    conn.commit()


def is_contributor(conn, project_id, login):
    row = conn.execute(
        "SELECT 1 FROM repo_contributors rc JOIN projects p ON p.repo_id=rc.repo_id "
        "WHERE p.id=? AND rc.login=?", (project_id, login)).fetchone()
    return bool(row)


def submit_edit(conn, project_id, login, field, new_value, old_value=None):
    if field not in EDITABLE:
        raise ValueError(f"field {field} not editable")
    if not is_contributor(conn, project_id, login):
        raise PermissionError("not a contributor")
    conn.execute(
        "INSERT INTO project_edits (project_id, field, old_value, new_value, "
        "contributor_login, status, created_at) VALUES (?,?,?,?,?,?,?)",
        (project_id, field, old_value, new_value, login, "pending", _now()))
    conn.commit()


def pending_edits(conn):
    return conn.execute(
        "SELECT * FROM project_edits WHERE status='pending' ORDER BY created_at").fetchall()


def approve(conn, edit_id, maintainer_login):
    row = conn.execute("SELECT * FROM project_edits WHERE id=?", (edit_id,)).fetchone()
    if not row:
        return False
    conn.execute(
        "UPDATE project_edits SET status='approved', reviewed_by=?, reviewed_at=? WHERE id=?",
        (maintainer_login, _now(), edit_id))
    conn.commit()
    return True


def reject(conn, edit_id, maintainer_login):
    conn.execute(
        "UPDATE project_edits SET status='rejected', reviewed_by=?, reviewed_at=? WHERE id=?",
        (maintainer_login, _now(), edit_id))
    conn.commit()


def approved_overrides(conn, project_id):
    rows = conn.execute(
        "SELECT field, new_value FROM project_edits WHERE project_id=? AND status='approved' "
        "ORDER BY created_at", (project_id,)).fetchall()
    out = {}
    for field, val in rows:
        out[field] = val
    return out


def apply_overrides(project, overrides):
    for k, v in overrides.items():
        if k in EDITABLE:
            project[k] = v
    return project