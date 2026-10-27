from hackproof.github.demo import is_public_http
from hackproof.github.scan import select_files


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
