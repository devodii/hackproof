import os

from stellar_sdk import Keypair, StrKey

from hackproof.github.models import Ref
from hackproof.github.refs import extract_refs

ACCOUNT = Keypair.random().public_key
CONTRACT = StrKey.encode_contract(os.urandom(32))


def refs(text: str) -> set[Ref]:
    return set(extract_refs(text, "README.md"))


def test_finds_contracts_accounts_and_assets():
    found = refs(f"deployed {CONTRACT} by {ACCOUNT}, token USDX:{ACCOUNT}")
    assert Ref(kind="contract", value=CONTRACT, path="README.md") in found
    assert Ref(kind="account", value=ACCOUNT, path="README.md") in found
    assert Ref(kind="asset", value=f"USDX:{ACCOUNT}", path="README.md") in found


def test_ignores_strings_with_a_bad_checksum():
    broken = ACCOUNT[:-1] + ("A" if ACCOUNT[-1] != "A" else "B")
    assert refs(f"key {broken}") == set()


def test_detects_the_network_from_passphrases_and_hosts():
    testnet = refs("passphrase = 'Test SDF Network ; September 2015'")
    mainnet = refs("https://horizon.stellar.org")
    assert Ref(kind="network", value="testnet", path="README.md") in testnet
    assert Ref(kind="network", value="mainnet", path="README.md") in mainnet
