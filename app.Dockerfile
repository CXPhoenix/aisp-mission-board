FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

ARG PORT=8000

COPY ./pyproject.toml /pyproject.toml
RUN uv pip install -r /pyproject.toml --system

WORKDIR /app
COPY ./app /app

CMD ["uvicorn"]
EXPOSE ${PORT}