from fastapi import APIRouter, HTTPException

from hackproof.integrations.chain import Reading
from hackproof.integrations.insights import (
    IntegrationDetail,
    deep_partner,
    fetch_detail,
    fetch_live,
)

router = APIRouter(prefix="/integrations")


@router.get("/{slug}")
async def integration(slug: str) -> IntegrationDetail:
    partner = deep_partner(slug)
    if partner is None:
        raise HTTPException(status_code=404, detail="no deep profile for this partner")
    return await fetch_detail(partner)


@router.get("/{slug}/live")
async def integration_live(slug: str) -> list[Reading]:
    partner = deep_partner(slug)
    if partner is None:
        raise HTTPException(status_code=404, detail="no deep profile for this partner")
    return await fetch_live(partner)
