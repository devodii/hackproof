import re
from pathlib import PurePosixPath
from typing import Literal

Track = Literal["genesis", "scale"]

TRACK = r"(genesis|scale)"
DECLARATION = re.compile(
    rf"\b{TRACK}\s+(?:path|track|category)\b"
    rf"|\b(?:path|track|tracks|category)\b[\s*_`:\-–|]*[\[(]?\s*{TRACK}\b"
    rf"|\bhack\s?meridian[^\n]{{0,40}}[·|•]\s*{TRACK}\b",
    re.IGNORECASE,
)


def _declared(text: str) -> Track | None:
    found = {
        value.lower() for match in DECLARATION.finditer(text) for value in match.groups() if value
    }
    return found.pop() if len(found) == 1 else None  # type: ignore[return-value]


def declared_track(files: dict[str, str]) -> Track | None:
    docs = sorted(
        (path for path in files if PurePosixPath(path).suffix.lower() == ".md"),
        key=lambda path: (len(PurePosixPath(path).parts), path),
    )
    for path in docs:
        if track := _declared(files[path]):
            return track
    return None
