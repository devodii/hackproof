from enum import StrEnum


class LinkMethod(StrEnum):
    """Ordered strongest first: the earliest method wins when several link the same item."""

    CONTRACT_IN_REPO = "contract_in_repo"
    WASM_HASH_MATCH = "wasm_hash_match"
    WASM_META = "wasm_meta"
    ASSET_IN_REPO = "asset_in_repo"
    DEPLOYER_IN_REPO = "deployer_in_repo"
    FOOTPRINT = "footprint"


METHOD_RANK_SQL = "array_position(ARRAY[{}], l.method)".format(
    ", ".join(f"'{method}'" for method in LinkMethod)
)
