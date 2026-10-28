from anthropic import AsyncAnthropic
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import JSONResponse, StreamingResponse

from hackproof.chat.briefs import describe_page
from hackproof.chat.ratelimit import RateLimiter
from hackproof.chat.stream import ChatRequest, stream_reply, to_anthropic
from hackproof.config import get_settings

router = APIRouter()
limiter = RateLimiter()


def client_key(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


@router.post("/chat")
async def chat(body: ChatRequest, request: Request):
    denied = limiter.check(client_key(request))
    if denied:
        return JSONResponse(
            status_code=429,
            headers={"Retry-After": str(denied.retry_after)},
            content={
                "detail": "rate_limited",
                "window": denied.window,
                "limit": denied.limit,
                "retryAfter": denied.retry_after,
            },
        )

    settings = get_settings()
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=503, detail="chat_unavailable")

    messages = to_anthropic(body.messages)
    if not messages or messages[-1]["role"] != "user":
        raise HTTPException(status_code=422, detail="last message must be from the user")

    return StreamingResponse(
        stream_reply(
            AsyncAnthropic(api_key=settings.anthropic_api_key),
            settings.chat_model,
            messages,
            await describe_page(body.page),
        ),
        media_type="text/event-stream",
        headers={"x-vercel-ai-ui-message-stream": "v1", "Cache-Control": "no-cache"},
    )
