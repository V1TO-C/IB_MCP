import os
import sys

# Add routers path
# Load routers path and inject into sys.path
ROUTERS_PATH = os.environ.get("ROUTERS_PATH")
if os.path.isdir(ROUTERS_PATH):
    sys.path.insert(0, ROUTERS_PATH)
else:
    print(f"⚠️ Warning: ROUTERS_PATH '{ROUTERS_PATH}' does not exist.")


# Load environment variables
GATEWAY_PORT = os.environ.get("GATEWAY_PORT")
GATEWAY_ENDPOINT = os.environ.get("GATEWAY_ENDPOINT")
GATEWAY_INTERNAL_BASE_URL = os.environ.get("GATEWAY_INTERNAL_BASE_URL")

MCP_SERVER_BASE_URL = os.environ.get("MCP_SERVER_BASE_URL")
MCP_SERVER_INTERNAL_BASE_URL = os.environ.get("MCP_SERVER_INTERNAL_BASE_URL")
MCP_SERVER_HOST = os.environ.get("MCP_SERVER_HOST")
MCP_TRANSPORT_PROTOCOL = os.environ.get("MCP_TRANSPORT_PROTOCOL")
MCP_SERVER_PORT = os.environ.get("MCP_SERVER_PORT")

# Add validation and type conversion for MCP_SERVER_PORT
if not MCP_SERVER_PORT:
    print("Error: MCP_SERVER_PORT environment variable is not set.")
    sys.exit(1)
try:
    MCP_SERVER_PORT = int(MCP_SERVER_PORT)
except ValueError:
    print("Error: MCP_SERVER_PORT must be a valid integer.")
    sys.exit(1)


BASE_URL = f"{GATEWAY_INTERNAL_BASE_URL}:{GATEWAY_PORT}{GATEWAY_ENDPOINT}"
