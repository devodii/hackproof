import pytest

from hackproof.linking.country import resolve_country


@pytest.mark.parametrize(
    ("location", "expected"),
    [
        ("Lagos, Nigeria", "NG"),
        ("Lisbon, Portugal", "PT"),
        ("San Francisco, CA, USA", "US"),
        ("London, UK", "GB"),
        ("Remote", None),
        (None, None),
    ],
)
def test_resolve_country(location, expected):
    assert resolve_country(location) == expected
