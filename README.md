# IB_MCP

## Overview

This project provides an Interactive Brokers (IB) API interface using the Model Context Protocol (MCP). It allows you to access real-time and historical market data from IB through a FastAPI-based service, designed to be used with MCP clients like Claude Desktop.

## Architecture

The project consists of two main components:

*   **ib_client_service:** A FastAPI application that connects to the IB API (TWS or IB Gateway) using the `ib_async` library. It exposes REST endpoints for retrieving market data. This service runs in a Docker container.
*   **mcp_server:** A FastMCP server that acts as an MCP interface to the `ib_client_service`. It exposes tools that can be called by MCP clients, which in turn call the REST endpoints of the `ib_client_service`. This service also runs in a Docker container.

## Setup

1.  **Create .env file:**
    Create a file named `.env` in the project root directory (`/Users/rubencontesti/Code/IB_MCP/`) and populate it with your IB API connection details. You can create this file by copying the content of `.env.example` and replacing the placeholder values with your actual IB connection information. The following variables are required:

    ```
    IB_HOST=127.0.0.1
    IB_PORT=7497  # Or your TWS/Gateway API port
    IB_CLIENT_ID=1 # Must be unique
    ```

2.  **Install Docker and Docker Compose:**
    Make sure you have Docker and Docker Compose installed on your system.

3.  **Build and Run:**
    In your terminal, navigate to the project root directory (`/Users/rubencontesti/Code/IB_MCP/`) and run:

    ```bash
    docker-compose up --build
    ```

    This command will build the Docker images for both services and start the containers.

## Testing

Once the services are running and connected to IB (check the logs for connection success), you can test the following endpoints:

### Health Check

```bash
curl http://localhost:5001/health
```

### Tick Data

```bash
# Stock Tick Data (Snapshot, Delayed) - Replace conId with a valid Bond conId
curl "http://localhost:5001/data/ticks/STK?conId=265598&exchange=SMART&currency=USD&marketDataType=3"

# Bond Tick Data (Snapshot, Delayed) - Replace conId with a valid Bond conId
curl "http://localhost:5001/data/ticks/BOND?conId=443719449&exchange=SMART&currency=USD&marketDataType=3"
```

### Historical Data

```bash
# Stock Historical Data
curl "http://localhost:5001/data/historical/STK?conId=265598&exchange=SMART&currency=USD&durationStr=1%20M&barSizeSetting=1%20day&whatToShow=TRADES"

# Bond Historical Data - Replace conId with a valid Bond conId
curl "http://localhost:5001/data/historical/BOND?conId=443719449&exchange=SMART&currency=USD&durationStr=1%20M&barSizeSetting=1%20day&whatToShow=MIDPOINT"
```

## Future Work

*   Implement MCP tools in the `mcp_server` to expose the `ib_client_service` endpoints.
*   Add endpoints for order placement and management.
*   Add endpoints for position retrieval.
*   Implement streaming tick data via Server-Sent Events (SSE).

## Resources:

### MCP
- [MCP Markdown instructions for LLMs](https://modelcontextprotocol.io/llms-full.txt)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [MCP Introduction](https://www.philschmid.de/mcp-introduction)

### Interactive Brokers
- [ib_async](https://github.com/ib-api-reloaded/ib_async)
- [ib_async documentation txt](https://ib-api-reloaded.github.io/ib_async/_sources/api.rst.txt)
