import json
from datetime import UTC, datetime, timedelta

from hackproof.integrations.catalog import (
    Agent,
    Catalog,
    Partner,
    Profile,
    Tool,
    get_catalog,
)
from hackproof.integrations.detect import (
    depth_hints,
    detect,
    detect_agents,
    detect_tools,
)
from hackproof.integrations.insights import is_stale
from hackproof.integrations.models import Detection
from hackproof.integrations.profile import build_profile

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


def test_reflector_is_found_deeply_from_source():
    files = {
        "package.json": '{"dependencies": {"@reflector/contract-client": "^2.2.0"}}',
        "src/oracle.ts": (
            'import { PulseClient } from "@reflector/contract-client"\n'
            'const id = "CCSSOHTBL3LEWUCBBEB5NJFC2OKFRC74OWEIJIZLRJBGAAU4VMU5NV4W"\n'
            'const quote = await client.lastPrice("BRL")\n'
            "const human = Number(quote.price) / 1e7\n"
        ),
        "README.md": "uses reflector, client.lastPrice('XYZ')",
    }
    found = {
        (item.method, item.evidence) for item in detect(files, get_catalog(), "someone")
    }
    assert ("package", "@reflector/contract-client") in found
    assert (
        "contract",
        "CCSSOHTBL3LEWUCBBEB5NJFC2OKFRC74OWEIJIZLRJBGAAU4VMU5NV4W",
    ) in found
    assert ("signal", "client-pulse") in found
    assert ("signal", "reads-last-price") in found
    assert ("signal", "hardcoded-decimals") in found
    assert ("capture", "tickers:BRL") in found
    assert ("capture", "tickers:XYZ") not in found


def test_a_repo_that_only_mentions_reflector_in_prose_is_not_an_integration():
    files = {"README.md": "We looked at reflector.network and PulseClient"}
    assert detect(files, get_catalog(), "someone") == []


def test_a_partner_with_only_a_catalog_profile_needs_no_adapter():
    files = {
        "Makefile": "deploy:\n\tstellar registry deploy --contract-name vault --wasm-name v\n",
    }
    found = {
        (item.slug, item.method, item.evidence)
        for item in detect_tools(files, get_catalog(), "someone")
    }
    assert ("stellar-registry", "signal", "cli-deploy") in found
    assert ("stellar-registry", "capture", "contract-names:vault") in found


def test_a_prose_mention_of_a_deep_partner_asks_for_a_deeper_scan():
    files = {"README.md": "We settle with Trustless Work escrows"}
    hints = depth_hints(files, get_catalog(), [])
    assert hints is not None and "escrow" in hints
    assert depth_hints({"README.md": "hello"}, get_catalog(), []) is None


def test_a_profile_written_before_the_newer_fields_still_loads():
    older = {
        "adapter": "reflector",
        "context": ["reflector"],
        "networks": {
            "testnet": {
                "rpc_url": "https://rpc",
                "passphrase": "p",
                "explorer": "https://e",
            }
        },
        "contracts": [
            {
                "slug": "fx",
                "id": "C1",
                "name": "FX",
                "network": "testnet",
                "kind": "feed",
            }
        ],
        "checks": [
            {"slug": "age", "label": "Age", "severity": "warn", "requires": ["a"]}
        ],
    }
    profile = Profile.model_validate(older)
    assert profile.surfaces == [] and profile.hints == []
    assert profile.contracts[0].url is None
    assert profile.checks[0].forbids == []


def test_trustless_work_is_read_deeply_from_source():
    files = {
        "package.json": '{"dependencies": {"@trustless-work/escrow": "^3.0.5"}}',
        ".env.example": "NEXT_PUBLIC_TRUSTLESS_WORK_API_KEY=\n",
        "src/escrow.ts": (
            "const base = 'https://dev.api.trustlesswork.com'\n"
            "await fetch(`${base}/escrow/single-release/fund-escrow`, { headers })\n"
            "await fetch(`${base}/escrow/single-release/v2/release-funds`, { headers })\n"
            "const note = 'v1 hosts are dev.api and api.trustlesswork.com'\n"
        ),
        "README.md": "Built on Trustless Work. Webhooks soon.",
    }
    catalog = get_catalog()
    found = [
        (item.method, item.evidence)
        for item in detect(files, catalog, "someone")
        if item.slug == "trustless-work"
    ]
    assert ("package", "@trustless-work/escrow") in found
    assert ("signal", "public-api-key") in found
    assert ("signal", "testnet-api") in found
    assert ("signal", "mainnet-api") not in found
    assert ("capture", "operation:fund-escrow") in found
    assert ("capture", "operation:release-funds") in found
    assert ("capture", "react-sdk-version:3.0.5") in found
    checks = {
        check.slug: check.status
        for check in build_profile(
            catalog.partner("trustless-work"), found, "testnet", include_private=True
        ).checks
    }
    assert checks["exposes-api-key"] == "fail"
    assert checks["release-without-validation"] == "warn"
    assert checks["no-rate-limit"] == "warn"
    assert "v2-on-mainnet-host" not in checks


def test_observed_state_goes_stale_after_an_hour():
    now = datetime(2026, 11, 19, 12, 0, tzinfo=UTC)
    assert is_stale(None, now)
    assert not is_stale(now - timedelta(minutes=59), now)
    assert is_stale(now - timedelta(minutes=61), now)


def test_private_signals_and_checks_never_reach_the_public_profile():
    catalog = get_catalog()
    found = [("signal", "calls-api"), ("signal", "public-api-key")]
    public = build_profile(catalog.partner("trustless-work"), found, "testnet")
    internal = build_profile(
        catalog.partner("trustless-work"), found, "testnet", include_private=True
    )
    assert public and internal
    assert {item.slug for item in public.signals} == {"calls-api"}
    assert public.checks == []
    assert "public-api-key" in {item.slug for item in internal.signals}
    assert "public-api-key" in catalog.private_signals()["trustless-work"]
