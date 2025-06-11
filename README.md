🚧 **Work in Progress**  
This repository is actively being developed and may not be fully functional at this time. Use at your own risk.

# Interactive Brokers Model Context Protocol

## Overview

This project provides an Interactive Brokers (IB) API interface using the Model Context Protocol (MCP). There are several ways to interact with Interactive Brokers, like the TWS API, the WEB API, Excel RTD and FIX among others. This project is build on top of Interactive Brokers WEP API.

IB offers two types of Authentication to their WebAPI, one for retail and individual clients and one for instritutional and third party developers. This development uses the retail authentification process which is managed using the Client Portal Gateway, a small java program used to route local web requests with appropriate authentication. 

## Architecture

The project consists of 3 main components:

*   **api_gateway:** Runs the Interactive Brokers Client Portal Gateway in a Docker container to enable secure access to the IB REST API.
*   **ticker_service:** It ensures that the api_gateway remains open. See reopen sessions section. This service runs in a Docker container.
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


###  📦  IB MCP Server Docker Container (WIP)



## Setup
0. Copy this .env.example file to .env and fill in your actual values
1. Build the image with: `docker compose up --build -d`
2. Auth with your IB account and credentials to:
    After the image is up and running, navigate to https://{GATEWAY_BASE_URL}:{GATEWAY_PORT}⁠ (e.g.: https://localhost:9999/) to login.
    If succesful you should be redirected to a url that reads: "Client login succeeds" 


3. After a successful auth browse to:

    https://{GATEWAY_BASE_URL}:{GATEWAY_PORT}/v1/api/iserver/account/orders or
    https://host.docker.internal:5055/v1/api/iserver/account/orders

    You should get:
    ```
    {
        "orders" : []
        "snapshot": False
    }
    ```


    Or to getMarket Data (hit twice)

    https://{GATEWAY_BASE_URL}:{GATEWAY_PORT}/v1/api/iserver/marketdata/snapshot?conids=265598,8314&fields=31,84,86

    You should get:
    ```
        [
        {
            "6509": "DPB",
            "conidEx": "265598",
            "conid": 265598,
            "_updated": 1749478449143,
            "6119": "q0",
            "server_id": "q0",
            "31": "204.85",
            "6508": "&serviceID1=122&serviceID2=123&serviceID3=203&serviceID4=775&serviceID5=204&serviceID6=206&serviceID7=108&serviceID8=109"
        },
        {
            "6509": "DPB",
            "conidEx": "8314",
            "conid": 8314,
            "_updated": 1749478447227,
            "6119": "q1",
            "server_id": "q1",
            "31": "270.00",
            "6508": "&serviceID1=20773&serviceID2=773&serviceID3=108&serviceID4=207&serviceID5=109"
        }
        ]
    ```


### Limitations (Given the multi container set up)

- Users must log in through the browser on the same machine as Client Portal Gateway in order to authenticate.
- All API Endpoint calls must be made on the same machine where the Client Portal Gateway was authenticated.
- None of the endpoints beginning with /gw/api, /oauth, or /oauth2 are supported for use in the Client Portal Gateway.

### Reopen session:

The additional /iserver/auth/ssodh/init endpoint is used to subsequently reopen a brokerage session with the backend, through which you can access the protected /iserver endpoints.

Sessions will time out after approximately 6 minutes without sending new requests or maintaining the /tickle endpoint at least every 5 minutes.

In order to prevent the session from timing out, the endpoint /tickle should be called on a regular basis. It is recommended to call this endpoint approximately every minute.

If the brokerage session has timed out but the session is still connected to the IBKR backend, the response to /auth/status returns ‘connected’:true and ‘authenticated’:false. Calling the /iserver/auth/ssodh/init endpoint will initialize a new brokerage session.

# Future Work

- [ ] Test MCP server functionality.
- [ ] Test MCP server with LLM. 

# References
- [IB WEB API Docker implementation](https://github.com/hackingthemarkets/interactive-brokers-web-api)
  
- [FAST MCP](https://github.com/jlowin/fastmcp)
- [FAST MCP Documentation](https://gofastmcp.com/servers/fastmcp)
- [FAST MCP openapi integration](https://gofastmcp.com/servers/openapi) 
- [IB WEB API Reference](https://www.interactivebrokers.com/campus/ibkr-api-page/webapi-ref/)
- [IB WEB API openapi docs](https://api.ibkr.com/gw/api/v3/api-docs)

- [ibeam](https://github.com/Voyz/ibeam): Facilitates continuous headless run of the Gateway. Not so secure - "Yupp, you'll need to store the credentials somewhere, and that's a risk. Read more about it in Security."- 