import base64
import hashlib
from datetime import datetime, timedelta

from fastapi.testclient import TestClient
from stellar_sdk import Keypair

from hackproof.db import pool
from hackproof.hackathon import get_hackathon
from hackproof.main import app
from hackproof.proof import SEP53_PREFIX


def sign(keypair: Keypair, message: str) -> str:
    payload = hashlib.sha256(SEP53_PREFIX + message.encode()).digest()
    return base64.b64encode(keypair.sign(payload)).decode()


def test_claim_rejects_keys_that_never_deployed():
    keypair = Keypair.random()
    with TestClient(app) as client:
        message = client.post("/api/proof/challenge", json={"address": keypair.public_key}).json()[
            "message"
        ]
        response = client.post(
            "/api/proof/claim",
            json={
                "address": keypair.public_key,
                "message": message,
                "signature": sign(keypair, message),
            },
        )
        assert response.status_code == 403
        assert client.get(f"/api/proof/{keypair.public_key}").status_code == 404


def test_claim_rejects_a_forged_signature():
    keypair = Keypair.random()
    with TestClient(app) as client:
        message = client.post("/api/proof/challenge", json={"address": keypair.public_key}).json()[
            "message"
        ]
        response = client.post(
            "/api/proof/claim",
            json={
                "address": keypair.public_key,
                "message": message,
                "signature": sign(Keypair.random(), message),
            },
        )
    assert response.status_code == 400


async def seed_deploy(address: str, at: datetime) -> None:
    async with pool().acquire() as connection:
        await connection.execute(
            "INSERT INTO contracts VALUES ($1, $2, $3, $4, $5, $6)",
            f"C{address[1:]}",
            address,
            "ab" * 32,
            "cd" * 32,
            1,
            at,
        )


async def clear(address: str) -> None:
    async with pool().acquire() as connection:
        await connection.execute("DELETE FROM contracts WHERE deployer = $1", address)
        await connection.execute("DELETE FROM proofs WHERE address = $1", address)


def test_deployer_can_claim_and_read_back_a_proof():
    keypair = Keypair.random()
    address = keypair.public_key
    with TestClient(app) as client:
        client.portal.call(seed_deploy, address, get_hackathon().window.start + timedelta(hours=1))
        try:
            message = client.post("/api/proof/challenge", json={"address": address}).json()[
                "message"
            ]
            claimed = client.post(
                "/api/proof/claim",
                json={"address": address, "message": message, "signature": sign(keypair, message)},
            )
            assert claimed.status_code == 200
            assert claimed.json()["contracts"] == 1
            assert client.get(f"/api/proof/{address}").json() == claimed.json()
        finally:
            client.portal.call(clear, address)
