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
COPY client.py .

# Debug: List files to verify server.py is copied
RUN ls -la /app/

#
RUN uv sync

# # Make the server executable
# RUN chmod +x server.py

# Environment variables (can be overridden at runtime)
ENV GATEWAY_BASE_URL=""
ENV GATEWAY_PORT=""
ENV GATEWAY_ENDPOINT=""
ENV MCP_SERVER_PORT=""

# Expose the port (if needed for health checks)
EXPOSE ${MCP_SERVER_PORT}

# # Run the server with uv (specify python explicitly)
# CMD ["uv", "run", "--", "python", "server.py"]

CMD ["uv", "run", "--", "python", "/app/server.py"]