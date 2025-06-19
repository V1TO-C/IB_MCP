# Interactive Brokers Model Context Protocol

[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

## Project Status
This project is currently under active development. Features may be incomplete, and breaking changes may occur. Use at your own risk.

## Table of Contents
- [Interactive Brokers Model Context Protocol](#interactive-brokers-model-context-protocol)
  - [Project Status](#project-status)
  - [Table of Contents](#table-of-contents)
  - [Overview](#overview)
  - [Architecture](#architecture)
    - [📦 Interactive Brokers Client Portal Gateway Docker Container](#-interactive-brokers-client-portal-gateway-docker-container)
        - [🔧 What This Container Does](#-what-this-container-does)
    - [📦 IB MCP Server Docker Container](#-ib-mcp-server-docker-container)
        - [🔧 What This Container Does](#-what-this-container-does-1)
  - [Setup](#setup)
  - [Usage Example (WIP)](#usage-example-wip)
    - [Limitations (Given the multi container set up)](#limitations-given-the-multi-container-set-up)
    - [Reopen session:](#reopen-session)
  - [Roadmap](#roadmap)
    - [Current Priorities](#current-priorities)
    - [Future Work](#future-work)
  - [References](#references)
  - [License](#license)

## Overview

This project provides an Interactive Brokers (IB) API interface using the Model Context Protocol (MCP). There are several ways to interact with Interactive Brokers, like the TWS API, the WEB API, Excel RTD and FIX among others. This project is built on top of Interactive Brokers WEB API.

IB offers two types of Authentication to their WebAPI, one for retail and individual clients and one for institutional and third party developers. This development uses the retail authentication process which is managed using the Client Portal Gateway, a small Java program used to route local web requests with appropriate authentication. 

## Architecture

The project consists of 3 main components:

*   **api_gateway:** Runs the Interactive Brokers Client Portal Gateway in a Docker container to enable secure access to the IB REST API.
*   **ticker_service:** This service is responsible for maintaining the Interactive Brokers session by periodically calling the `/tickle` endpoint to prevent session timeouts, as detailed in the 'Reopen Session' section. This service runs in a Docker container.
*   **mcp_server:** MCP server that interacts with API gateway. This service also runs in a Docker container.


### 📦 Interactive Brokers Client Portal Gateway Docker Container

This Docker container sets up and runs the **Interactive Brokers (IB) Client Portal Gateway**, which is required for applications to connect via the IB REST API.

##### 🔧 What This Container Does

- **Base Image**: Uses `eclipse-temurin:21` (Java 21) for compatibility with the IB Gateway.
- **Installs Dependencies**: Installs `unzip` for extracting the gateway archive.
- **Downloads Gateway**: Fetches the latest version of the Client Portal Gateway from the official Interactive Brokers source and unzips it.
- **Configuration**:
  - Copies a custom `conf.yaml` into the expected path (`gateway/root/conf.yaml`) to configure the gateway.
  - Adds a custom `run_gateway.sh` script as the container entrypoint.
- **Port Exposure**: Exposes port `5055` (default port used by the gateway). Override as needed in .env.
- **Startup Command**: Runs the gateway using the configuration file.

This setup provides a self-contained, reproducible environment for securely running the Interactive Brokers REST API gateway in a containerized environment.


### 📦 IB MCP Server Docker Container
This Docker container sets up and runs the **Interactive Brokers (IB) Model Context Protocol (MCP) Server**, which provides an interface for interacting with the IB API gateway.

##### 🔧 What This Container Does

- **Base Image**: (Specify base image, e.g., `python:3.9-slim-buster`)
- **Installs Dependencies**: (Specify dependencies, e.g., `pip install -r requirements.txt`)
- **Configuration**: (Describe any specific configuration steps or files)
- **Port Exposure**: (Specify exposed ports, e.g., `5008`)
- **Startup Command**: (Describe how the server is started)

This setup provides a containerized environment for the MCP server, enabling it to communicate with the IB Client Portal Gateway.


## Setup
0. Copy this `.env.example` file to `.env` and fill in your actual values
1. Build the image with: `docker compose up --build -d`
2. Auth with your IB account and credentials to:
    After the image is up and running, navigate to `https://{GATEWAY_BASE_URL}:{GATEWAY_PORT}`⁠ (e.g.: `https://localhost:9999/`) to login.
    If successful you should be redirected to a URL that reads: "Client login succeeds"

3. Add MCP server config file (only the first time)

    Given the following environment parameters
    ```
    MCP_SERVER_HOST=0.0.0.0
    MCP_SERVER_PORT=5008
    MCP_SERVER_PATH=/mcp
    MCP_TRANSPORT_PROTOCOL=streamable-http
    ```

    the VS Code MCP server snippet in `settings.json` would look like:

    ```json
    "ib-mcp-server": {
        "type": "http",
        "url": "http://localhost:5008/mcp/",
    }
    ```

## Usage Example (WIP)

### Limitations (Given the multi container set up)

- Users must log in through the browser on the same machine as Client Portal Gateway in order to authenticate.
- All API Endpoint calls must be made on the same machine where the Client Portal Gateway was authenticated.
- None of the endpoints beginning with /gw/api, /oauth, or /oauth2 are supported for use in the Client Portal Gateway.

### Reopen session:

The additional /iserver/auth/ssodh/init endpoint is used to subsequently reopen a brokerage session with the backend, through which you can access the protected /iserver endpoints.

Sessions will time out after approximately 6 minutes without sending new requests or maintaining the /tickle endpoint at least every 5 minutes.

In order to prevent the session from timing out, the endpoint /tickle should be called on a regular basis. It is recommended to call this endpoint approximately every minute.

If the brokerage session has timed out but the session is still connected to the IBKR backend, the response to /auth/status returns ‘connected’:true and ‘authenticated’:false. Calling the /iserver/auth/ssodh/init endpoint will initialize a new brokerage session.


## Roadmap

### Current Priorities
- Automatically generate routers from OpenApi specification.
- Be able to check the automatic tools generation

### Future Work
- Test MCP server functionality.
- Test MCP server with LLM.
- Add OAuth

## References
- [IB WEB API Docker implementation](https://github.com/hackingthemarkets/interactive-brokers-web-api)
  
- [FAST MCP](https://github.com/jlowin/fastmcp)
- [FAST MCP Documentation](https://gofastmcp.com/servers/fastmcp)
- [FAST MCP openapi integration](https://gofastmcp.com/servers/openapi) 
- [IB WEB API Reference](https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-ref/)
- [IB WEB API openapi docs](https://api.ibkr.com/gw/api/v3/api-docs)

- [ibeam](https://github.com/Voyz/ibeam): Facilitates continuous headless run of the Gateway. Not so secure - "Yupp, you'll need to store the credentials somewhere, and that's a risk. Read more about it in Security."- 

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
