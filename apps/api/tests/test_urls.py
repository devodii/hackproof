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


def test_file_paths_are_percent_encoded_so_every_link_is_a_valid_url():
    url = repo_file_url("https://github.com/team/app", "board/Leo's notes #1 (v2).md")

    assert (
        url
        == "https://github.com/team/app/blob/HEAD/board/Leo%27s%20notes%20%231%20%28v2%29.md"
    )
    assert " " not in url


def test_evidence_found_in_a_demo_bundle_links_to_the_bundle_itself():
    bundle = "https://demo.example.app/assets/index-abc.js"

    assert repo_file_url("https://github.com/team/app", bundle) == bundle
