from hackproof.integrations.catalog import Catalog, Partner, get_catalog
from hackproof.integrations.detect import Detection, detect

CATALOG = Catalog(
    partners=[
        Partner(
            slug="acme",
            name="Acme",
            category="payments",
            site="https://acme.example",
            packages={
                "js": ["@acme/sdk"],
                "rust": ["acme-core"],
                "python": ["acme-sdk"],
                "go": ["github.com/acme/go-sdk"],
            },
            endpoints=["api.acme.example"],
            github_owners=["acme"],
        )
    ]
)


def found(files: dict[str, str], owner: str = "team") -> set[tuple[str, str, str]]:
    return {(d.method, d.evidence, d.path) for d in detect(files, CATALOG, owner)}


def test_packages_are_found_in_every_ecosystem():
    files = {
        "package.json": '{"dependencies": {"@acme/sdk": "^1"}}',
        "contracts/Cargo.toml": '[dependencies]\nacme-core = "0.2"\n',
        "requirements.txt": "Acme_SDK==1.0\n",
        "go.mod": "require github.com/acme/go-sdk/v2 v2.1.0\n",
    }

    assert found(files) == {
        ("package", "@acme/sdk", "package.json"),
        ("package", "acme-core", "contracts/Cargo.toml"),
        ("package", "Acme_SDK", "requirements.txt"),
        ("package", "github.com/acme/go-sdk/v2", "go.mod"),
    }


def test_raw_endpoint_calls_are_found_in_code_and_config():
    files = {
        "client.go": 'http.Get("https://api.acme.example/v1/pay")',
        ".env.example": "ACME_URL=https://API.acme.example",
    }

    assert found(files) == {("endpoint", "api.acme.example", "client.go")}


def test_prose_mentions_are_not_an_integration():
    files = {
        "README.md": "We call api.acme.example and use @acme/sdk",
        "docs/notes.txt": "api.acme.example",
    }

    assert found(files) == set()


def test_lookalike_hosts_and_packages_do_not_match():
    files = {
        "app.ts": "fetch('https://notapi.acme.example') and 'api.acme.example.evil.com'",
        "package.json": '{"dependencies": {"@acme/sdk-extras": "1"}}',
        "go.mod": "require github.com/acme/go-sdkx v1.0.0\n",
    }

    assert found(files) == set()


def test_the_partners_own_repos_are_not_integrations():
    files = {"package.json": '{"dependencies": {"@acme/sdk": "1"}}'}

    assert found(files, owner="Acme") == set()


def test_broken_manifests_are_skipped():
    assert found({"package.json": "{not json", "Cargo.toml": "[[["}) == set()


def test_a_detection_is_reported_once_with_the_first_file():
    files = {
        "package.json": '{"dependencies": {"@acme/sdk": "1"}}',
        "web/package.json": '{"dependencies": {"@acme/sdk": "1"}}',
    }

    assert detect(files, CATALOG, "team") == [
        Detection(slug="acme", method="package", evidence="@acme/sdk", path="package.json")
    ]


def test_the_shipped_catalog_is_valid_and_unique():
    catalog = get_catalog()
    slugs = [partner.slug for partner in catalog.partners]

    assert len(slugs) == len(set(slugs)) >= 10
    assert catalog.partner("trustless-work").packages["js"][0] == "@trustless-work/escrow"
