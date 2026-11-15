import re

from pydantic import BaseModel

RULES = [
    (r"\bDROP\s+TABLE\b", "drops a table and every row in it"),
    (r"\bDROP\s+COLUMN\b", "drops a column and its data"),
    (r"\bDROP\s+TYPE\b", "drops a type"),
    (r"\bDROP\s+SCHEMA\b", "drops a schema"),
    (r"\bDROP\s+SEQUENCE\b", "drops a sequence"),
    (r"\bDROP\s+MATERIALIZED\s+VIEW\b", "drops stored view data"),
    (
        r"\bALTER\s+COLUMN\b[^;]*\bTYPE\b",
        "changes a column type and can rewrite or lose data",
    ),
    (r"\bTRUNCATE\b", "empties a table"),
    (r"\bDELETE\s+FROM\b", "deletes rows"),
    (r"\bUPDATE\s+\S+\s+SET\b", "rewrites rows"),
]


class Finding(BaseModel):
    reason: str
    statement: str


def strip_comments(sql: str) -> str:
    return re.sub(r"--[^\n]*", "", sql)


def destructive_statements(sql: str) -> list[Finding]:
    """
    Every statement in a plan that could lose data. Dropping an index, view,
    trigger, function or constraint loses none, so those pass.
    """
    findings = []
    for statement in strip_comments(sql).split(";"):
        for pattern, reason in RULES:
            if re.search(pattern, statement, re.IGNORECASE):
                findings.append(
                    Finding(reason=reason, statement=" ".join(statement.split())[:200])
                )
    return findings
