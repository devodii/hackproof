from stellar_sdk import xdr

from hackproof.indexer.wasm import contract_meta

MAGIC = b"\x00asm\x01\x00\x00\x00"


def leb128(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        out.append(byte | (0x80 if value else 0))
        if not value:
            return bytes(out)


def custom_section(name: str, payload: bytes) -> bytes:
    body = leb128(len(name)) + name.encode() + payload
    return b"\x00" + leb128(len(body)) + body


def meta_entry(key: str, value: str) -> bytes:
    entry = xdr.SCMetaEntry(
        kind=xdr.SCMetaKind.SC_META_V0,
        v0=xdr.SCMetaV0(key=key.encode(), val=value.encode()),
    )
    return entry.to_xdr_bytes()


def test_reads_every_entry_of_the_meta_section():
    payload = meta_entry("source_repo", "github:acme/vault") + meta_entry("rsver", "1.93.0")
    wasm = MAGIC + custom_section("name", b"ignored") + custom_section("contractmetav0", payload)
    assert contract_meta(wasm) == {"source_repo": "github:acme/vault", "rsver": "1.93.0"}


def test_wasm_without_meta_section_is_empty():
    assert contract_meta(MAGIC + custom_section("producers", b"x")) == {}


def test_truncated_wasm_does_not_raise():
    assert contract_meta(MAGIC + b"\x00\xff") == {}
