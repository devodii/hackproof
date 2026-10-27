import re
from collections.abc import Iterator

from stellar_sdk import StrKey

from hackproof.github.models import Ref

CONTRACT = re.compile(r"\bC[A-Z2-7]{55}\b")
ACCOUNT = re.compile(r"\bG[A-Z2-7]{55}\b")
ASSET = re.compile(r"\b([A-Za-z0-9]{1,12}):(G[A-Z2-7]{55})\b")

NETWORK_MARKERS = {
    "Test SDF Network ; September 2015": "testnet",
    "Public Global Stellar Network ; September 2015": "mainnet",
    "soroban-testnet.stellar.org": "testnet",
    "horizon-testnet.stellar.org": "testnet",
    "friendbot.stellar.org": "testnet",
    "mainnet.sorobanrpc.com": "mainnet",
    "horizon.stellar.org": "mainnet",
}


def extract_refs(text: str, path: str) -> Iterator[Ref]:
    for match in CONTRACT.finditer(text):
        if StrKey.is_valid_contract(match[0]):
            yield Ref(kind="contract", value=match[0], path=path)
    for match in ACCOUNT.finditer(text):
        if StrKey.is_valid_ed25519_public_key(match[0]):
            yield Ref(kind="account", value=match[0], path=path)
    for match in ASSET.finditer(text):
        if StrKey.is_valid_ed25519_public_key(match[2]):
            yield Ref(kind="asset", value=match[0], path=path)
    for marker, network in NETWORK_MARKERS.items():
        if marker in text:
            yield Ref(kind="network", value=network, path=path)
