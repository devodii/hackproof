import base64
import binascii
import hashlib
import re
from datetime import UTC, datetime, timedelta

from stellar_sdk import Keypair
from stellar_sdk.exceptions import BadSignatureError, Ed25519PublicKeyInvalidError

SEP53_PREFIX = b"Stellar Signed Message:\n"
MESSAGE_TTL = timedelta(minutes=10)
MESSAGE_PATTERN = re.compile(
    r"^hackproof\.vercel\.app proof of hack\n"
    r"address: (?P<address>G[A-Z2-7]{55})\n"
    r"issued: (?P<issued>\S+)$"
)


def build_message(address: str, now: datetime) -> str:
    issued = now.astimezone(UTC).isoformat(timespec="seconds")
    return f"hackproof.vercel.app proof of hack\naddress: {address}\nissued: {issued}"


def message_is_fresh(address: str, message: str, now: datetime) -> bool:
    match = MESSAGE_PATTERN.match(message)
    if match is None or match["address"] != address:
        return False
    try:
        issued = datetime.fromisoformat(match["issued"])
    except ValueError:
        return False
    return timedelta(0) <= now - issued <= MESSAGE_TTL


def signature_is_valid(address: str, message: str, signature: str) -> bool:
    payload = hashlib.sha256(SEP53_PREFIX + message.encode()).digest()
    try:
        raw = base64.b64decode(signature, validate=True)
        Keypair.from_public_key(address).verify(payload, raw)
    except (binascii.Error, BadSignatureError, Ed25519PublicKeyInvalidError, ValueError):
        return False
    return True


def proof_id(address: str) -> str:
    return hashlib.sha256(f"hackproof:{address}".encode()).hexdigest()[:12]
