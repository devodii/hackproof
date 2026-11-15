import json

from hackproof.integrations.catalog import Agent, Catalog, Partner, Tool, get_catalog
from hackproof.integrations.detect import detect, detect_agents, detect_tools
from hackproof.integrations.models import Detection

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
        Detection(
            slug="acme", method="package", evidence="@acme/sdk", path="package.json"
        )
    ]


def test_the_shipped_catalog_is_valid_and_unique():
    catalog = get_catalog()
    slugs = [partner.slug for partner in catalog.partners]

    assert len(slugs) == len(set(slugs)) >= 10
    assert (
        catalog.partner("trustless-work").packages["js"][0] == "@trustless-work/escrow"
    )


def test_tools_are_found_apart_from_partners():
    catalog = Catalog(
        partners=CATALOG.partners,
        tools=[
            Tool(
                slug="scaffold",
                name="Scaffold",
                site="https://scaffold.example",
                packages={"js": ["@scaffold/app-lib"]},
            )
        ],
    )
    files = {
        "package.json": json.dumps(
            {"dependencies": {"@scaffold/app-lib": "1", "@acme/sdk": "1"}}
        )
    }

    assert {d.slug for d in detect_tools(files, catalog, "team")} == {"scaffold"}
    assert {d.slug for d in detect(files, catalog, "team")} == {"acme"}


AGENT_CATALOG = Catalog(
    partners=[],
    agents=[
        Agent(
            slug="cursor",
            name="Cursor",
            site="https://cursor.example",
            files=[".cursor/*", ".cursorrules"],
            authors=["cursoragent"],
        ),
        Agent(
            slug="claude",
            name="Claude",
            site="https://claude.example",
            files=["CLAUDE.md"],
        ),
    ],
)


def test_agents_are_found_by_file_and_by_commit_author():
    paths = [
        "src/app.ts",
        "CLAUDE.md",
        ".cursor/rules/style.mdc",
        "apps/web/.cursorrules",
    ]

    found = detect_agents(paths, ["Someone", "CursorAgent"], AGENT_CATALOG)

    assert {(d.slug, d.method, d.evidence, d.path) for d in found} == {
        ("cursor", "file", ".cursor/*", ".cursor/rules/style.mdc"),
        ("cursor", "file", ".cursorrules", "apps/web/.cursorrules"),
        ("cursor", "author", "cursoragent", ""),
        ("claude", "file", "CLAUDE.md", "CLAUDE.md"),
    }


def test_agent_files_inside_dependencies_are_ignored():
    paths = ["node_modules/pkg/CLAUDE.md", "vendor/.cursor/rules.mdc"]

    assert detect_agents(paths, [], AGENT_CATALOG) == []


def test_the_shipped_catalog_lists_unique_agents():
    agents = get_catalog().agents

    assert {"claude-code", "cursor", "codex", "github-copilot"} <= {
        agent.slug for agent in agents
    }
    assert len({agent.slug for agent in agents}) == len(agents)


def test_stellar_raven_and_skills_are_found_in_agent_config_files():
    files = {
        ".mcp.json": '{"mcpServers": {"stellar-raven": {"url": "https://raven.stellar.org/mcp"}}}',
        "skills-lock.json": '{"skills": {"dapp": {"source": "stellar/stellar-dev-skill"}}}',
    }

    found = {(d.slug, d.path) for d in detect_tools(files, get_catalog(), "team")}

    assert found == {
        ("stellar-raven", ".mcp.json"),
        ("stellar-skills", "skills-lock.json"),
    }
