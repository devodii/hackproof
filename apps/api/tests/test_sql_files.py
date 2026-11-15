from hackproof.sql_loader import SQL_DIR


async def test_every_statement_prepares(scratch_db):
    for path in sorted(SQL_DIR.rglob("*.sql")):
        await scratch_db.prepare(path.read_text())
