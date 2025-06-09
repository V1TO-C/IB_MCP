import httpx
import logging
import urllib3
import os
import sys
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap
# from fastmcp.server.openapi import RouteMap, MCPType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL")
GATEWAY_PORT = os.environ.get("GATEWAY_PORT")
GATEWAY_ENDPOINT = os.environ.get("GATEWAY_ENDPOINT")
IB_OPEN_API_SPECIFICATION_URL = "https://api.ibkr.com/gw/api/v3/api-docs"

# Validate environment variables
if not GATEWAY_BASE_URL or not GATEWAY_PORT or not GATEWAY_ENDPOINT:
    print("Error: One or more required environment variables are not set.")
    sys.exit(1)

BASE_API_URL = f"{GATEWAY_BASE_URL}:{GATEWAY_PORT}{GATEWAY_ENDPOINT}"
print(f"Using API base URL: {BASE_API_URL}")


# # Create an HTTP client for your API
client = httpx.AsyncClient(base_url=BASE_API_URL)

# Load your OpenAPI spec 
openapi_spec = httpx.get(IB_OPEN_API_SPECIFICATION_URL).json()

# We need to modify openapi_spec default servers:
"""
  "servers": [
    {
      "url": "https://api.ibkr.com",
      "description": "Production"
    },
    {
      "url": "https://qa.interactivebrokers.com",
      "description": "Sandbox"
    }
"""
openapi_spec["servers"] = [
    {
        "url": BASE_API_URL,
        "description": "Custom Server" #
    }
]


# # TODO: Add with version 2.5
# # Exclude some routes like those of order execution
# route_maps=[
#     RouteMap(pattern=r"^/orders*", mcp_type=MCPType.EXCLUDE),
#     RouteMap(tags={"Trading Orders"}, mcp_type=MCPType.EXCLUDE),
# ]


# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="IB MCP Server",
    version="1.0.0",
    # route_maps=route_maps,
)

if __name__ == "__main__":
    mcp.run()