# Add to existing imports
from fastapi import APIRouter
from hackproof.db import pool

router = APIRouter()

# Add new route
@router.get("/errors")
async def get_error_taxonomy():
    """Returns Soroban error taxonomy with failure counts"""
    # Load error definitions
    with open("config/soroban-errors.yaml") as f:
        error_config = yaml.safe_load(f)["errors"]
    
    # Get failure counts
    query = """
        SELECT result_code, COUNT(*) as count 
        FROM failed_txs 
        GROUP BY result_code
    """
    async with pool().acquire() as conn:
        counts = {row["result_code"]: row["count"] for row in await conn.fetch(query)}
    
    # Merge config with counts
    errors = []
    for error in error_config:
        error_count = counts.get(error["code"], 0)
        errors.append({
            **error,
            "count": error_count
        })
    
    return {"errors": errors}
