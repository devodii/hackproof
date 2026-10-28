FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim

ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    UV_PYTHON_DOWNLOADS=never \
    PATH="/app/apps/api/.venv/bin:$PATH"

WORKDIR /app/apps/api

COPY apps/api/pyproject.toml apps/api/uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY apps/api/src ./src
RUN uv sync --frozen --no-dev

COPY config /app/config

RUN useradd --create-home app && chown -R app /app
USER app

EXPOSE 8000
CMD ["sh", "-c", "exec uvicorn hackproof.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
