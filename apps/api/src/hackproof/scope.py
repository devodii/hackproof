from contextvars import ContextVar

from fastapi import HTTPException, Query

from hackproof.hackathon import Hackathon, get_hackathon, hackathons

_selected: ContextVar[str | None] = ContextVar("hackathon", default=None)


def current() -> Hackathon:
    slug = _selected.get()
    return get_hackathon() if slug is None else hackathons()[slug]


def selected_slug() -> str | None:
    return _selected.get()


async def select_hackathon(hackathon: str | None = Query(None, max_length=60)) -> None:
    if hackathon is not None and hackathon not in hackathons():
        raise HTTPException(404, "unknown hackathon")
    _selected.set(hackathon)
