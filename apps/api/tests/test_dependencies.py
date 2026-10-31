from hackproof.github.dependencies import (
    FREIGHTER_PACKAGES,
    PASSKEY_PACKAGES,
    WALLETS_KIT_PACKAGES,
    detect_ai_tooling,
    detect_framework,
    detect_openzeppelin,
    fingerprint,
    parse_major_version,
)

WANTED = {
    "rust": ["soroban-sdk"],
    "js": ["@stellar/stellar-sdk", "stellar-base"],
    "python": ["stellar-sdk"],
    "go": ["github.com/stellar/go"],
}


def test_reads_rust_and_js_manifests():
    result = fingerprint(
        {
            "contracts/Cargo.toml": '[dependencies]\nsoroban-sdk = "22.0.0"\nserde = "1"',
            "web/package.json": (
                '{"dependencies": {"@stellar/stellar-sdk": "^14.0.0", "react": "19"}}'
            ),
        },
        WANTED,
    )
    assert result.ecosystems == ["rust", "js"]
    assert result.packages == {"soroban-sdk": "22.0.0", "@stellar/stellar-sdk": "^14.0.0"}


def test_reads_table_style_cargo_dependencies_and_workspaces():
    result = fingerprint(
        {
            "Cargo.toml": (
                '[workspace.dependencies]\nsoroban-sdk = { version = "23.1.0", features = ["x"] }'
            )
        },
        WANTED,
    )
    assert result.packages == {"soroban-sdk": "23.1.0"}


def test_reads_python_and_go_manifests():
    result = fingerprint(
        {
            "requirements.txt": "requests==2.0\nstellar-sdk>=12.0.0\n",
            "go.mod": "module x\n\nrequire (\n\tgithub.com/stellar/go v0.0.0-2024\n)\n",
        },
        WANTED,
    )
    assert result.ecosystems == ["python", "go"]
    assert result.packages["stellar-sdk"] == "12.0.0"


def test_broken_manifests_are_skipped():
    assert fingerprint({"package.json": "{not json"}, WANTED).packages == {}


def test_repos_without_stellar_dependencies_have_no_fingerprint():
    assert (
        fingerprint({"package.json": '{"dependencies": {"react": "19"}}'}, WANTED).ecosystems == []
    )


def test_detects_openzeppelin_in_cargo_and_package_json():
    # 1. Cargo.toml table fixture
    cargo_fixture = """
    [dependencies]
    soroban-sdk = "22.0.0"
    openzeppelin-stellar-contracts = { version = "0.2.0" }
    """
    assert detect_openzeppelin({"Cargo.toml": cargo_fixture}) is True

    # 2. Cargo.toml inline string fixture
    cargo_str = """
    [dependencies]
    stellar-contracts = "0.1.0"
    """
    assert detect_openzeppelin({"Cargo.toml": cargo_str}) is True

    # 3. package.json fixture
    pkg_fixture = """
    {
      "dependencies": {
        "@openzeppelin/contracts": "^5.0.0"
      }
    }
    """
    assert detect_openzeppelin({"package.json": pkg_fixture}) is True

    # 4. Manifest without OpenZeppelin
    normal_cargo = '[dependencies]\nsoroban-sdk = "22.0.0"'
    assert detect_openzeppelin({"Cargo.toml": normal_cargo}) is False


def test_detects_wallets_kit_and_freighter_and_passkey():
    pkg_fixture = {
        "package.json": """
        {
          "dependencies": {
            "@creit.tech/stellar-wallets-kit": "^1.1.0",
            "@stellar/freighter-api": "^3.0.0",
            "passkey-kit": "^0.4.0"
          }
        }
        """
    }
    result = fingerprint(
        pkg_fixture,
        {
            "js": [
                *WALLETS_KIT_PACKAGES,
                *FREIGHTER_PACKAGES,
                *PASSKEY_PACKAGES,
            ]
        },
    )
    assert "@creit.tech/stellar-wallets-kit" in result.packages
    assert "@stellar/freighter-api" in result.packages
    assert "passkey-kit" in result.packages


def test_detects_next_and_vite_frameworks():
    next_fixture = '{"dependencies": {"next": "15.0.0", "react": "19"}}'
    assert detect_framework({"package.json": next_fixture}) == "Next.js"

    vite_fixture = '{"devDependencies": {"vite": "^6.0.0", "react": "19"}}'
    assert detect_framework({"frontend/package.json": vite_fixture}) == "Vite"

    other_fixture = '{"dependencies": {"express": "^4.18.0"}}'
    assert detect_framework({"package.json": other_fixture}) == "Other"

    no_pkg = {"Cargo.toml": '[dependencies]\nsoroban-sdk = "22"'}
    assert detect_framework(no_pkg) == "Other"


def test_detects_ai_tooling_in_paths():
    paths = [
        "src/index.ts",
        "CLAUDE.md",
        ".agents/AGENTS.md",
        ".cursorrules",
        ".github/copilot-instructions.md",
    ]
    detected = detect_ai_tooling(paths)
    assert "CLAUDE.md" in detected
    assert "AGENTS.md" in detected
    assert "Cursor rules" in detected
    assert "Copilot instructions" in detected

    empty_paths = ["src/main.rs", "Cargo.toml", "README.md"]
    assert detect_ai_tooling(empty_paths) == []


def test_parse_major_version():
    assert parse_major_version("^22.0.0") == "v22"
    assert parse_major_version("~21.3.1") == "v21"
    assert parse_major_version("20.1") == "v20"
    assert parse_major_version("v14.0.0") == "v14"
    assert parse_major_version(">=13.0.0") == "v13"
    assert parse_major_version(None) == "Unknown"
    assert parse_major_version("git-ref") == "Unknown"
