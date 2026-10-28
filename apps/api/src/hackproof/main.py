from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hackproof.chat.routes import router as chat_router
from hackproof.config import get_settings
from hackproof.db import close_pool, open_pool
from hackproof.export.routes import router as export_router
from hackproof.hackathon import get_hackathon
from hackproof.routes import router

api = APIRouter(prefix="/api")


@api.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@api.get("/window")
async def window() -> dict[str, str]:
    hackathon = get_hackathon()
    return {
        "name": hackathon.name,
        "start": hackathon.window.start.isoformat(),
        "end": hackathon.window.end.isoformat(),
    }


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await open_pool()
    yield
    await close_pool()


app = FastAPI(title="hackproof", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=get_settings().cors_origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
api.include_router(router)
api.include_router(export_router)
api.include_router(chat_router)
app.include_router(api)
