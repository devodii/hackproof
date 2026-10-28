from functools import cache
from pathlib import Path

PROMPT_FILE = Path(__file__).with_name("system-prompt.md")


@cache
def sections() -> dict[str, str]:
    found: dict[str, str] = {}
    name: str | None = None
    lines: list[str] = []
    for line in PROMPT_FILE.read_text().splitlines():
        if line.startswith("## "):
            if name:
                found[name] = "\n".join(lines).strip()
            name, lines = line[3:].strip(), []
        elif name:
            lines.append(line)
    if name:
        found[name] = "\n".join(lines).strip()
    return found


def prompt(name: str, **values: str) -> str:
    return sections()[name].format(**values)
