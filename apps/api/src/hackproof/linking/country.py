import pycountry

ALIASES = {
    "usa": "US",
    "u.s.": "US",
    "u.s.a.": "US",
    "uk": "GB",
    "england": "GB",
    "scotland": "GB",
    "wales": "GB",
    "uae": "AE",
    "korea": "KR",
    "russia": "RU",
    "vietnam": "VN",
    "turkey": "TR",
    "czechia": "CZ",
}


def resolve_country(location: str | None) -> str | None:
    if not location:
        return None
    for token in reversed([part.strip() for part in location.split(",")]):
        if not token:
            continue
        alias = ALIASES.get(token.lower())
        if alias:
            return alias
        try:
            return pycountry.countries.lookup(token).alpha_2
        except LookupError:
            continue
    return None
