from enum import StrEnum


class LinkMethod(StrEnum):
    CONTRACT_IN_REPO = "contract_in_repo"
    WASM_HASH_MATCH = "wasm_hash_match"
    WASM_META = "wasm_meta"
    DEPLOYER_IN_REPO = "deployer_in_repo"
    ASSET_IN_REPO = "asset_in_repo"
    FOOTPRINT = "footprint"
    MANUAL = "manual"


CONFIDENCE = {
    LinkMethod.CONTRACT_IN_REPO: 1.0,
    LinkMethod.WASM_HASH_MATCH: 1.0,
    LinkMethod.WASM_META: 1.0,
    LinkMethod.MANUAL: 1.0,
    LinkMethod.ASSET_IN_REPO: 0.95,
    LinkMethod.DEPLOYER_IN_REPO: 0.9,
    LinkMethod.FOOTPRINT: 0.8,
}
