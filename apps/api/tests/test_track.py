import pytest

from hackproof.github.track import declared_track


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("HackMeridian 2026, Genesis path, Stellar Composed", "genesis"),
        ("**Tracks:** Scale, Stellar Composed", "scale"),
        ("Builder track: **Scale**. Thematic track: **Stellar Composed**", "scale"),
        ("Path: `Genesis (Idea -> MVP)`", "genesis"),
        ("Built for HackMeridian 2026 · Genesis · Stellar Unlocked", "genesis"),
        ("HackMeridian 2026 · Category: Scale · Track: Stellar Composed", "scale"),
        ("Track: Stellar Composed, payments at scale", None),
        ("Genesis block of the chain, scaling plans", None),
        ("Genesis path, later moving to the Scale track", None),
        ("No track mentioned", None),
    ],
)
def test_reads_the_track_a_readme_declares(text, expected):
    assert declared_track({"README.md": text}) == expected


def test_prefers_the_shallowest_doc_and_ignores_code():
    files = {
        "docs/notes.md": "Scale track",
        "README.md": "Genesis track",
        "src/app.ts": "const track = 'scale'",
    }

    assert declared_track(files) == "genesis"
    assert declared_track({"src/app.ts": "Scale track"}) is None
