from pathlib import Path

from trawl.db.sql import sql_loader

SQL_DIR = Path(__file__).with_name("sql")
load_sql = sql_loader(SQL_DIR)
