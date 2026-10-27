import json

import asyncpg

from hackproof.github.client import GithubClient
from hackproof.linking.country import resolve_country

BATCH = 100


def _query(logins: list[str]) -> str:
    lookups = (
        f"u{i}: user(login: {json.dumps(login)}) {{ login location }}"
        for i, login in enumerate(logins)
    )
    return "query {" + " ".join(lookups) + "}"


async def resolve_profiles(github: GithubClient, connection: asyncpg.Connection) -> int:
    rows = await connection.fetch(
        """
        SELECT DISTINCT login FROM repo_contributors
        WHERE login NOT IN (SELECT login FROM github_users)
        """
    )
    logins = [row["login"] for row in rows]
    for start in range(0, len(logins), BATCH):
        batch = logins[start : start + BATCH]
        data = await github.graphql(_query(batch))
        locations = {node["login"].lower(): node["location"] for node in data.values() if node}
        await connection.executemany(
            "INSERT INTO github_users (login, location, country) VALUES ($1, $2, $3)"
            " ON CONFLICT (login) DO NOTHING",
            [
                (login, locations.get(login.lower()), resolve_country(locations.get(login.lower())))
                for login in batch
            ],
        )
    return len(logins)
