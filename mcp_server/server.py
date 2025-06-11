import httpx
import logging
import urllib3
import os
import sys
from fastmcp import FastMCP
from fastmcp.server.openapi import RouteMap
from fastmcp.server.openapi import RouteMap, MCPType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Disable warnings for self-signed certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Load environment variables
GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL")
GATEWAY_PORT = os.environ.get("GATEWAY_PORT")
GATEWAY_ENDPOINT = os.environ.get("GATEWAY_ENDPOINT")
MCP_SERVER_BASE_URL = os.environ.get("MCP_SERVER_BASE_URL")
MCP_SERVER_INTERNAL_BASE_URL = os.environ.get("MCP_SERVER_INTERNAL_BASE_URL")
MCP_SERVER_HOST = os.environ.get("MCP_SERVER_HOST")
MCP_TRANSPORT_PROTOCOL = os.environ.get("MCP_TRANSPORT_PROTOCOL")
MCP_SERVER_PORT = os.environ.get("MCP_SERVER_PORT")


IB_OPEN_API_SPECIFICATION_URL = "https://api.ibkr.com/gw/api/v3/api-docs"

# Validate environment variables
if not GATEWAY_BASE_URL or not GATEWAY_PORT or not GATEWAY_ENDPOINT:
    print("Error: One or more required environment variables are not set.")
    sys.exit(1)

# Add validation and type conversion for MCP_SERVER_PORT
if not MCP_SERVER_PORT:
    print("Error: MCP_SERVER_PORT environment variable is not set.")
    sys.exit(1)
try:
    MCP_SERVER_PORT = int(MCP_SERVER_PORT)
except ValueError:
    print("Error: MCP_SERVER_PORT must be a valid integer.")
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



# Exclude some routes like those of order execution
route_maps=[
    RouteMap(pattern=r"^/orders*", mcp_type=MCPType.EXCLUDE),
    RouteMap(tags={"Trading Orders"}, mcp_type=MCPType.EXCLUDE),
]


# Create the MCP server
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=client,
    name="IB MCP Server",
    route_maps=route_maps,
)

if __name__ == "__main__":
    mcp.run(
        transport=MCP_TRANSPORT_PROTOCOL,
        host=MCP_SERVER_HOST,           # Bind to all interfaces
        port=MCP_SERVER_PORT,                # Custom port
        log_level="DEBUG",        # Override global log level
    )
