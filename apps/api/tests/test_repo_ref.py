import pytest

from hackproof.linking.repo_ref import normalize_repo


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("github:acme/vault", "acme/vault"),
        ("https://github.com/acme/vault", "acme/vault"),
        ("https://github.com/acme/vault.git", "acme/vault"),
        ("https://github.com/acme/vault/tree/main/contracts", "acme/vault"),
        ("acme/vault", "acme/vault"),
        ("https://gitlab.com/acme/vault", None),
        ("not a repo", None),
    ],
)
def test_normalize_repo(raw, expected):
    assert normalize_repo(raw) == expected
