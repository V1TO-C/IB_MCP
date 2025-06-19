FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy uv files first for better caching
COPY pyproject.toml ./

# Copy the server code
COPY server.py .
COPY fastapi_server.py .
COPY testing_client.py .

# Debug: List files to verify server.py is copied
RUN ls -la /app/

# 
ENV UV_CACHE_DIR=/tmp/uv-cache

#
RUN uv sync

# # Make the server executable
# RUN chmod +x server.py

# Environment variables (can be overridden at runtime)
ENV GATEWAY_BASE_URL=""
ENV GATEWAY_PORT=""
ENV GATEWAY_ENDPOINT=""
ENV GATEWAY_TEST_ENDPOINT=""
ENV MCP_SERVER_PORT=""
ENV MCP_SERVER_HOST=""
ENV MCP_TRANSPORT_PROTOCOL=""
ENV MCP_SERVER_BASE_URL=""
ENV MCP_SERVER_INTERNAL_BASE_URL=""

# Expose the port (if needed for health checks)
EXPOSE ${MCP_SERVER_PORT}

# # Run the server with uv (specify python explicitly)
# CMD ["uv", "run", "--", "python", "server.py"]

CMD ["uv", "run", "--", "python", "/app/fastapi_server.py"]

# CMD ["uv", "run", "--", "python", "/app/testing_client.py"]