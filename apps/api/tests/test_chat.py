import json
from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from hackproof.chat import routes, stream
from hackproof.chat.ratelimit import RateLimiter
from hackproof.chat.stream import Message, Part, stream_reply, to_anthropic
from hackproof.chat.tools import TOOL_SPECS, run_tool
from hackproof.main import app


def parse(chunks: list[str]) -> list[dict | str]:
    parsed = []
    for chunk in chunks:
        body = chunk.removeprefix("data: ").strip()
        parsed.append(body if body == "[DONE]" else json.loads(body))
    return parsed


class FakeStream:
    def __init__(self, chunks, final):
        self.chunks, self.final = chunks, final

    async def __aenter__(self):
        return self

    async def __aexit__(self, *_):
        return None

    def __aiter__(self):
        async def generate():
            for chunk in self.chunks:
                yield chunk

        return generate()

    async def get_final_message(self):
        return self.final


class FakeClient:
    def __init__(self, steps):
        self.steps = iter(steps)
        self.messages = SimpleNamespace(stream=lambda **_: next(self.steps))


def block(**fields):
    return SimpleNamespace(model_dump=lambda: fields, **fields)


def test_every_tool_has_a_schema():
    names = {spec["name"] for spec in TOOL_SPECS}
    assert {"query_projects", "query_contracts", "get_stats"} <= names
    assert all(spec["input_schema"]["type"] == "object" for spec in TOOL_SPECS)


def test_to_anthropic_keeps_text_only():
    messages = [
        Message(role="user", parts=[Part(type="text", text="hi")]),
        Message(role="assistant", parts=[Part(type="tool-query_projects")]),
        Message(role="assistant", parts=[Part(type="text", text="hello")]),
    ]
    assert to_anthropic(messages) == [
        {"role": "user", "content": "hi"},
        {"role": "assistant", "content": "hello"},
    ]


async def test_rejects_unknown_arguments_before_querying():
    with pytest.raises(ValueError):
        await run_tool("query_projects", {"limit": 500})


async def test_streams_text_then_tool_then_answer(monkeypatch):
    async def fake_run_tool(name, raw):
        return {"total": 1, "items": [{"project_id": "repo:a/b"}]}

    monkeypatch.setattr(stream, "run_tool", fake_run_tool)
    call = block(type="tool_use", id="t1", name="query_projects", input={"limit": 1})
    client = FakeClient(
        [
            FakeStream(
                [
                    SimpleNamespace(type="text", text="Checking."),
                    SimpleNamespace(type="content_block_start", content_block=call),
                ],
                SimpleNamespace(stop_reason="tool_use", content=[call]),
            ),
            FakeStream(
                [SimpleNamespace(type="text", text="One project.")],
                SimpleNamespace(stop_reason="end_turn", content=[]),
            ),
        ]
    )

    events = parse([c async for c in stream_reply(client, "m", [{"role": "user", "content": "x"}])])
    types = [e["type"] if isinstance(e, dict) else e for e in events]

    assert types[0] == "start" and types[-2:] == ["finish", "[DONE]"]
    assert types.index("tool-input-start") < types.index("tool-input-available")
    assert types.index("tool-input-available") < types.index("tool-output-available")
    deltas = [e["delta"] for e in events if isinstance(e, dict) and e["type"] == "text-delta"]
    assert deltas == ["Checking.", "One project."]


async def test_tool_failure_is_reported_not_raised(monkeypatch):
    async def failing(name, raw):
        raise ValueError("bad arguments")

    monkeypatch.setattr(stream, "run_tool", failing)
    call = block(type="tool_use", id="t1", name="query_projects", input={})
    client = FakeClient(
        [
            FakeStream([], SimpleNamespace(stop_reason="tool_use", content=[call])),
            FakeStream([], SimpleNamespace(stop_reason="end_turn", content=[])),
        ]
    )
    events = parse([c async for c in stream_reply(client, "m", [{"role": "user", "content": "x"}])])
    assert any(isinstance(e, dict) and e["type"] == "tool-output-error" for e in events)


def post(client: TestClient):
    return client.post(
        "/api/chat",
        json={"messages": [{"role": "user", "parts": [{"type": "text", "text": "hi"}]}]},
    )


def test_chat_is_rate_limited(monkeypatch):
    monkeypatch.setattr(routes, "limiter", RateLimiter())
    monkeypatch.setattr(routes, "get_settings", lambda: SimpleNamespace(anthropic_api_key=None))
    with TestClient(app) as client:
        statuses = [post(client).status_code for _ in range(11)]
        denied = post(client)
    assert statuses[:10] == [503] * 10
    assert denied.status_code == 429
    assert denied.json()["window"] == "minute"
    assert denied.headers["retry-after"] == str(denied.json()["retryAfter"])


def test_chat_passes_the_current_page_to_the_model(monkeypatch):
    seen = {}

    async def fake_describe(page):
        seen["page"] = page
        return "on a project page"

    async def fake_stream(client, model, messages, page=""):
        seen["context"] = page
        yield "data: [DONE]\n\n"

    monkeypatch.setattr(routes, "limiter", RateLimiter())
    monkeypatch.setattr(routes, "describe_page", fake_describe)
    monkeypatch.setattr(routes, "stream_reply", fake_stream)
    monkeypatch.setattr(
        routes, "get_settings", lambda: SimpleNamespace(anthropic_api_key="k", chat_model="m")
    )
    body = {
        "page": {"kind": "project", "id": "repo:a/b"},
        "messages": [{"role": "user", "parts": [{"type": "text", "text": "hi"}]}],
    }
    with TestClient(app) as client:
        assert client.post("/api/chat", json=body).status_code == 200
    assert (seen["page"].kind, seen["page"].id) == ("project", "repo:a/b")
    assert seen["context"] == "on a project page"
