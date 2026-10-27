from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException
from stellar_sdk import StrKey

from hackproof import proofs
from hackproof.proof import build_message, message_is_fresh, signature_is_valid
from hackproof.schemas import Challenge, ChallengeRequest, ClaimRequest, Proof

router = APIRouter(prefix="/proof")


def _require_address(address: str) -> None:
    if not StrKey.is_valid_ed25519_public_key(address):
        raise HTTPException(status_code=422, detail="not a valid stellar account")


@router.post("/challenge")
async def challenge(request: ChallengeRequest) -> Challenge:
    _require_address(request.address)
    return Challenge(message=build_message(request.address, datetime.now(UTC)))


@router.post("/claim")
async def claim(request: ClaimRequest) -> Proof:
    _require_address(request.address)
    now = datetime.now(UTC)
    if not message_is_fresh(request.address, request.message, now):
        raise HTTPException(status_code=400, detail="challenge expired, request a new one")
    if not signature_is_valid(request.address, request.message, request.signature):
        raise HTTPException(status_code=400, detail="signature does not match this account")
    if await proofs.activity(request.address) is None:
        raise HTTPException(status_code=403, detail="this key did not deploy during the hack")
    await proofs.store_claim(request.address, request.signature, now)
    return Proof(**await proofs.load_proof(request.address))


@router.get("/{address}")
async def proof(address: str) -> Proof:
    _require_address(address)
    found = await proofs.load_proof(address)
    if found is None:
        raise HTTPException(status_code=404, detail="no proof claimed for this key")
    return Proof(**found)
