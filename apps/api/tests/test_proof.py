import base64
import hashlib
from datetime import UTC, datetime, timedelta

from stellar_sdk import Keypair

from hackproof.proof import SEP53_PREFIX, build_message, message_is_fresh, signature_is_valid


def sign(keypair: Keypair, message: str) -> str:
    payload = hashlib.sha256(SEP53_PREFIX + message.encode()).digest()
    return base64.b64encode(keypair.sign(payload)).decode()


def test_message_is_fresh_only_for_its_own_address_and_window():
    keypair = Keypair.random()
    now = datetime.now(UTC)
    message = build_message(keypair.public_key, now)
    assert message_is_fresh(keypair.public_key, message, now + timedelta(minutes=1))
    assert not message_is_fresh(keypair.public_key, message, now + timedelta(minutes=11))
    assert not message_is_fresh(Keypair.random().public_key, message, now)
    assert not message_is_fresh(keypair.public_key, "hello", now)


def test_signature_must_come_from_the_claimed_key():
    signer, other = Keypair.random(), Keypair.random()
    message = build_message(signer.public_key, datetime.now(UTC))
    signature = sign(signer, message)
    assert signature_is_valid(signer.public_key, message, signature)
    assert not signature_is_valid(other.public_key, message, signature)
    assert not signature_is_valid(signer.public_key, message + "x", signature)
    assert not signature_is_valid(signer.public_key, message, "not base64!")
