FROM nvidia/cuda:12.3.2-cudnn9-runtime-ubuntu22.04

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

ADD uv.lock pyproject.toml .python-version README.md /app/
WORKDIR /app

ENV UV_LINK_MODE=copy

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync

ADD . /app

ENTRYPOINT [ "uv", "run", "main.py" ]
