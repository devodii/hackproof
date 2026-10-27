from stellar_sdk import xdr
from xdrlib3 import Unpacker

CUSTOM_SECTION = 0
META_SECTION = "contractmetav0"


def _leb128(data: bytes, offset: int) -> tuple[int, int]:
    value = shift = 0
    while True:
        byte = data[offset]
        offset += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, offset
        shift += 7


def contract_meta(wasm: bytes) -> dict[str, str]:
    meta: dict[str, str] = {}
    offset = 8
    try:
        while offset < len(wasm):
            section_id = wasm[offset]
            size, offset = _leb128(wasm, offset + 1)
            end = offset + size
            if section_id == CUSTOM_SECTION:
                name_length, cursor = _leb128(wasm, offset)
                name = wasm[cursor : cursor + name_length].decode()
                if name == META_SECTION:
                    meta.update(_decode_meta(wasm[cursor + name_length : end]))
            offset = end
    except (IndexError, UnicodeDecodeError, ValueError):
        pass
    return meta


def _decode_meta(payload: bytes) -> dict[str, str]:
    entries: dict[str, str] = {}
    unpacker = Unpacker(payload)
    while unpacker.get_position() < len(payload):
        entry = xdr.SCMetaEntry.unpack(unpacker)
        v0 = entry.v0
        entries[v0.key.decode()] = v0.val.decode()
    return entries
