from hackproof.export.urls import (
    EXPLORER,
    account_url,
    asset_url,
    contract_url,
    ledger_url,
    repo_file_url,
    tx_url,
)


def test_chain_items_link_to_stellar_expert_on_testnet():
    assert EXPLORER == "https://stellar.expert/explorer/testnet"
    assert contract_url("CABC") == f"{EXPLORER}/contract/CABC"
    assert account_url("GABC") == f"{EXPLORER}/account/GABC"
    assert tx_url("ff00") == f"{EXPLORER}/tx/ff00"
    assert ledger_url(5380000) == f"{EXPLORER}/ledger/5380000"


def test_assets_use_the_dash_separator_stellar_expert_expects():
    assert asset_url("USDC:GISSUER") == f"{EXPLORER}/asset/USDC-GISSUER"


def test_repo_files_link_to_the_default_branch():
    url = repo_file_url("https://github.com/team/app", "contracts/deploy.sh")
    assert url == "https://github.com/team/app/blob/HEAD/contracts/deploy.sh"
