from hackproof.github.dependencies import fingerprint

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
