from functools import cache
from pathlib import Path

SQL_DIR = Path(__file__).with_name("sql")


@cache
def load_sql(name: str) -> str:
    return (SQL_DIR / f"{name}.sql").read_text()
