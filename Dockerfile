# syntax=docker/dockerfile:1.7

ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN python -m ensurepip --upgrade && pip install --upgrade pip

# ------------------------------
FROM base AS builder
COPY . /app
RUN pip install build && python -m build

# ------------------------------
FROM base AS api
WORKDIR /app
COPY --from=builder /app/dist /dist
RUN pip install /dist/kali_agents_mcp-*.whl uvicorn[standard]
EXPOSE 8000
ENV KALI_AGENTS_API_KEY=dev-token
CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# ------------------------------
FROM base AS cli
WORKDIR /app
COPY --from=builder /app/dist /dist
RUN pip install /dist/kali_agents_mcp-*.whl
ENTRYPOINT ["kali-agents"]
