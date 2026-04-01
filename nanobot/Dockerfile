# Adapted from backend/Dockerfile and qwen-code-api/Dockerfile
# Also see https://docs.astral.sh/uv/guides/integration/docker/

# ---
# Stage 1: build the application in the `/app` directory.
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}astral/uv:python3.14-bookworm-slim AS builder
ENV UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy

# Omit development dependencies
ENV UV_NO_DEV=1

# Disable Python downloads - use the system interpreter across both images.
ENV UV_PYTHON_DOWNLOADS=0

WORKDIR /app

# Copy workspace root files for dependency resolution (from workspace context)
COPY --from=workspace pyproject.toml uv.lock /app/

# Copy nanobot package files (from workspace context)
COPY --from=workspace nanobot/pyproject.toml /app/nanobot/pyproject.toml

# Copy MCP packages that nanobot depends on (from workspace context)
COPY --from=workspace mcp/mcp-lms/pyproject.toml /app/mcp/mcp-lms/pyproject.toml
COPY --from=workspace mcp/mcp-obs/pyproject.toml /app/mcp/mcp-obs/pyproject.toml

# Copy webchat channel packages (from workspace context)
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml /app/nanobot-websocket-channel/nanobot-channel-protocol/pyproject.toml
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat/pyproject.toml /app/nanobot-websocket-channel/nanobot-webchat/pyproject.toml
COPY --from=workspace nanobot-websocket-channel/mcp-webchat/pyproject.toml /app/nanobot-websocket-channel/mcp-webchat/pyproject.toml

# Sync nanobot package with its dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-install-workspace --package nanobot-agent

# Copy the rest of nanobot source (from workspace context)
COPY --from=workspace nanobot/ /app/nanobot/

# Copy mcp-lms source (from workspace context)
COPY --from=workspace mcp/mcp-lms/ /app/mcp/mcp-lms/

# Copy mcp-obs source (from workspace context)
COPY --from=workspace mcp/mcp-obs/ /app/mcp/mcp-obs/

# Copy nanobot-websocket-channel packages (from workspace context)
COPY --from=workspace nanobot-websocket-channel/nanobot-channel-protocol/ /app/nanobot-websocket-channel/nanobot-channel-protocol/
COPY --from=workspace nanobot-websocket-channel/nanobot-webchat/ /app/nanobot-websocket-channel/nanobot-webchat/
COPY --from=workspace nanobot-websocket-channel/mcp-webchat/ /app/nanobot-websocket-channel/mcp-webchat/

# Install nanobot with its workspace dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --package nanobot-agent --package mcp-lms --package mcp-obs --package nanobot-webchat --package mcp-webchat --package nanobot-channel-protocol

# ---
# Stage 2: use a final image without uv
# ---

ARG REGISTRY_PREFIX_DOCKER_HUB
FROM ${REGISTRY_PREFIX_DOCKER_HUB}python:3.14.2-slim-bookworm

# Set environment variables for Python and application
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
# Make sure we use UTF-8 encoding
ENV LANG=C.UTF-8

# Accept build args for user/group IDs (to match host user for bind mounts)
ARG APP_UID=999
ARG APP_GID=999

# Setup a non-root user with configurable UID/GID (skip if root)
RUN if [ "${APP_UID}" != "0" ]; then \
        groupadd --system --gid ${APP_GID} nonroot \
        && useradd --system --gid ${APP_GID} --uid ${APP_UID} --create-home nonroot; \
    fi

# Copy the application from the builder
COPY --from=builder --chown=${APP_UID}:${APP_GID} /app /app

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Use the configured user (root if APP_UID=0, otherwise nonroot)
USER ${APP_UID}:${APP_GID}

WORKDIR /app

# Run the entrypoint script which resolves config and starts nanobot gateway
CMD ["python", "/app/nanobot/entrypoint.py"]
