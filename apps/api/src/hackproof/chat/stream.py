import json
from collections.abc import AsyncIterator
from typing import Any
from uuid import uuid4

from anthropic import AsyncAnthropic
from pydantic import BaseModel

from hackproof.chat.briefs import Page
from hackproof.chat.tools import TOOL_SPECS, run_tool
from hackproof.hackathon import get_hackathon

MAX_STEPS = 6
MAX_TOKENS = 2048

SYSTEM = """You answer questions about HackMeridian 2026, a Stellar hackathon, using data rebuilt \
from Stellar testnet and linked to GitHub repos by exact matches.

The hack window is {start} to {end} UTC. Projects have an evidence tier: verified (an exact \
repo-to-chain match plus activity in the window), likely (a Stellar dependency and commits in the \
window, created or Stellar added during it), possible, and unattributed. The official submission \
list is not public, so say when a number is a reconstruction.

Always use the tools for facts and numbers; never guess. Be brief and concrete. Link projects as \
markdown to /project/<project_id> (for example /project/repo:owner/name) and builders to \
/builder/<address>. Use short lists or tables when comparing.

{page}"""


class Part(BaseModel):
    type: str
    text: str | None = None


class Message(BaseModel):
    role: str
    parts: list[Part] = []


class ChatRequest(BaseModel):
    messages: list[Message]
    page: Page | None = None


def event(payload: dict[str, Any]) -> str:
    return f"data: {json.dumps(payload, default=str)}\n\n"


def to_anthropic(messages: list[Message]) -> list[dict[str, Any]]:
    converted: list[dict[str, Any]] = []
    for message in messages:
        text = "".join(part.text or "" for part in message.parts if part.type == "text").strip()
        if message.role in ("user", "assistant") and text:
            converted.append({"role": message.role, "content": text})
    return converted


async def stream_reply(
    client: AsyncAnthropic, model: str, messages: list[dict[str, Any]], page: str = ""
) -> AsyncIterator[str]:
    window = get_hackathon().window
    system = SYSTEM.format(start=window.start.isoformat(), end=window.end.isoformat(), page=page)
    yield event({"type": "start", "messageId": uuid4().hex})

    try:
        for _ in range(MAX_STEPS):
            yield event({"type": "start-step"})
            text_id = uuid4().hex
            text_open = False

            async with client.messages.stream(
                model=model,
                system=system,
                messages=messages,
                tools=TOOL_SPECS,
                max_tokens=MAX_TOKENS,
            ) as stream:
                async for chunk in stream:
                    if chunk.type == "text":
                        if not text_open:
                            yield event({"type": "text-start", "id": text_id})
                            text_open = True
                        yield event({"type": "text-delta", "id": text_id, "delta": chunk.text})
                    elif (
                        chunk.type == "content_block_start"
                        and chunk.content_block.type == "tool_use"
                    ):
                        yield event(
                            {
                                "type": "tool-input-start",
                                "toolCallId": chunk.content_block.id,
                                "toolName": chunk.content_block.name,
                            }
                        )
                final = await stream.get_final_message()

            if text_open:
                yield event({"type": "text-end", "id": text_id})

            calls = [block for block in final.content if block.type == "tool_use"]
            if final.stop_reason != "tool_use" or not calls:
                yield event({"type": "finish-step"})
                break

            results = []
            for call in calls:
                yield event(
                    {
                        "type": "tool-input-available",
                        "toolCallId": call.id,
                        "toolName": call.name,
                        "input": call.input,
                    }
                )
                try:
                    output = await run_tool(call.name, call.input)
                    yield event(
                        {"type": "tool-output-available", "toolCallId": call.id, "output": output}
                    )
                    content, is_error = json.dumps(output, default=str), False
                except Exception as error:
                    yield event(
                        {
                            "type": "tool-output-error",
                            "toolCallId": call.id,
                            "errorText": str(error),
                        }
                    )
                    content, is_error = str(error), True
                results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": call.id,
                        "content": content,
                        "is_error": is_error,
                    }
                )

            messages = [
                *messages,
                {"role": "assistant", "content": [block.model_dump() for block in final.content]},
                {"role": "user", "content": results},
            ]
            yield event({"type": "finish-step"})
    except Exception:
        yield event({"type": "error", "errorText": "The assistant ran into a problem. Try again."})

    yield event({"type": "finish"})
    yield "data: [DONE]\n\n"
