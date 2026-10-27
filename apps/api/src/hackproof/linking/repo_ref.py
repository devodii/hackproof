import re

REPO_PATTERN = re.compile(
    r"^(?:(?:https?://)?(?:www\.)?github\.com/|github:)?"
    r"(?P<owner>[A-Za-z0-9](?:[A-Za-z0-9-]{0,38}))/"
    r"(?P<repo>[A-Za-z0-9._-]+?)(?:\.git)?/?(?:[/#?].*)?$"
)


def normalize_repo(value: str) -> str | None:
    match = REPO_PATTERN.match(value.strip())
    if match is None:
        return None
    return f"{match['owner']}/{match['repo']}"
