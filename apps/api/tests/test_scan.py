from hackproof.github.demo import is_public_http
from hackproof.github.models import DependencyFingerprint, RepoScan
from hackproof.github.scan import DEMO_URL, contributors_from, select_files, store_scan
from hackproof.integrations.models import Detection
from tests.helpers import add_repo


def blob(path: str, size: int = 100) -> dict:
    return {"type": "blob", "path": path, "size": size}


def test_select_files_prioritises_manifests_and_skips_noise():
    texts, wasms = select_files(
        [
            blob("src/deep/nested/main.rs"),
            blob("Cargo.toml"),
            blob("README.md"),
            blob("node_modules/pkg/index.js"),
            blob("package-lock.json"),
            blob("dist/app.min.js"),
            blob("assets/logo.png"),
            blob("target/out.wasm"),
            blob("build/contract.wasm", 2_000),
            {"type": "tree", "path": "src"},
        ]
    )
    assert texts == ["Cargo.toml", "README.md", "src/deep/nested/main.rs"]
    assert wasms == ["target/out.wasm", "build/contract.wasm"]


def test_select_files_drops_oversized_files():
    texts, wasms = select_files([blob("big.json", 600_000), blob("huge.wasm", 9_000_000)])
    assert texts == [] and wasms == []


def test_demo_urls_must_be_public_http():
    assert is_public_http("https://my-app.vercel.app/")
    assert not is_public_http("http://localhost:3000")
    assert not is_public_http("http://127.0.0.1/admin")
    assert not is_public_http("http://169.254.169.254/latest")
    assert not is_public_http("file:///etc/passwd")


def test_contributors_keep_people_and_drop_bots():
    people = contributors_from(
        [
            {
                "login": "ana",
                "html_url": "https://github.com/ana",
                "avatar_url": "a",
                "type": "User",
                "contributions": 12,
            },
            {"login": "dependabot[bot]", "html_url": "x", "type": "Bot", "contributions": 40},
        ]
    )
    assert [(p.login, p.contributions) for p in people] == [("ana", 12)]
    assert contributors_from(None) == []


def test_demo_url_pattern_only_matches_ascii_hosts():
    assert DEMO_URL.search("see https://my-app.vercel.app/docs for the demo").group() == (
        "https://my-app.vercel.app/docs"
    )
    assert DEMO_URL.search("https://你的用户名.github.io`、`SITE_BASE=") is None


async def test_a_rescan_replaces_the_stored_integrations(scratch_db):
    db = scratch_db
    await add_repo(db, "team/app")
    detection = Detection(slug="privy", method="package", evidence="@privy-io/node", path="a.json")

    def scan(*found: Detection) -> RepoScan:
        return RepoScan(
            full_name="team/app",
            refs=[],
            dependencies=DependencyFingerprint(),
            stellar_added_in_window=None,
            integrations=list(found),
            contributors=[],
        )

    await store_scan(db, scan(detection))
    await store_scan(db, scan(detection))
    assert await db.fetchval("SELECT count(*) FROM repo_integrations") == 1

    await store_scan(db, scan())
    assert await db.fetchval("SELECT count(*) FROM repo_integrations") == 0
