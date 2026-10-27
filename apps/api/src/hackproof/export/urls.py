EXPLORER = "https://stellar.expert/explorer/testnet"


def contract_url(contract_id: str) -> str:
    return f"{EXPLORER}/contract/{contract_id}"


def account_url(address: str) -> str:
    return f"{EXPLORER}/account/{address}"


def tx_url(tx_hash: str) -> str:
    return f"{EXPLORER}/tx/{tx_hash}"


def ledger_url(sequence: int) -> str:
    return f"{EXPLORER}/ledger/{sequence}"


def asset_url(asset: str) -> str:
    return f"{EXPLORER}/asset/{asset.replace(':', '-')}"


def repo_file_url(repo_url: str, path: str) -> str:
    return f"{repo_url}/blob/HEAD/{path}"
