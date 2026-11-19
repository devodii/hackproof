from hackproof.integrations.catalog import get_catalog
from hackproof.integrations.profile import build_profile

MAINNET_FX = "CBKGPWGKSKZF52CFHMTRR23TBWTPMRDIYZ4O2P5VS65BMHYH4DXMCJZC"
TESTNET_FX = "CCSSOHTBL3LEWUCBBEB5NJFC2OKFRC74OWEIJIZLRJBGAAU4VMU5NV4W"


def _statuses(evidence: list[tuple[str, str]]) -> dict[str, str]:
    profile = build_profile(get_catalog().partner("reflector"), evidence, "testnet")
    assert profile
    return {check.slug: check.status for check in profile.checks}


def test_a_reader_with_no_age_check_and_seven_decimals_is_flagged():
    found = _statuses(
        [
            ("signal", "reads-last-price"),
            ("signal", "hardcoded-decimals"),
            ("contract", TESTNET_FX),
        ]
    )
    assert found == {"no-age-check": "warn", "assumed-decimals": "warn"}


def test_the_guards_turn_a_check_into_a_pass():
    found = _statuses(
        [
            ("signal", "reads-last-price"),
            ("signal", "checks-age"),
            ("signal", "hardcoded-decimals"),
            ("signal", "reads-decimals"),
        ]
    )
    assert found == {"no-age-check": "pass", "assumed-decimals": "pass"}


def test_mainnet_only_feeds_on_a_testnet_event_fail():
    assert _statuses([("contract", MAINNET_FX)]) == {"wrong-network": "fail"}
    assert _statuses([("contract", MAINNET_FX), ("contract", TESTNET_FX)]) == {}


def test_captures_group_by_name_and_deduplicate():
    profile = build_profile(
        get_catalog().partner("reflector"),
        [
            ("capture", "tickers:EUR"),
            ("capture", "tickers:EUR"),
            ("capture", "tickers:BRL"),
        ],
        "testnet",
    )
    assert profile and profile.captures == {"tickers": ["BRL", "EUR"]}
