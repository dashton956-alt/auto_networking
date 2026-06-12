FROM python:3.13-slim AS base

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir uv && \
    uv pip install --system -e "."

FROM base AS dev
RUN uv pip install --system -e ".[dev]"
COPY . .
CMD ["uvicorn", "anif_platform.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

FROM base AS production
COPY src/ src/
CMD ["uvicorn", "anif_platform.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
