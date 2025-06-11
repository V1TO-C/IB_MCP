import asyncio
import os
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport # Import the specific transport

# Construct the server URL from environment variables
MCP_SERVER_HOST = os.environ.get("MCP_SERVER_HOST", "localhost") # Default to localhost if not set
MCP_SERVER_PORT = os.environ.get("MCP_SERVER_PORT", "5002") # Default to 5002 if not set
# MCP_TRANSPORT_PROTOCOL is not directly used in the URL for StreamableHttpTransport

server_url = f"http://{MCP_SERVER_HOST}:{MCP_SERVER_PORT}"
print(f"Connecting to MCP server at: {server_url}")

# Explicitly create the StreamableHttpTransport
transport = StreamableHttpTransport(url=server_url)
client = Client(transport)

async def main():
    # Give the server a moment to fully initialize
    await asyncio.sleep(5)
    # Connection is established here
    async with client:
        print(f"Client connected: {client.is_connected()}")

        # Try to ping the server to verify basic connectivity
        try:
            await client.ping()
            print("Server is reachable via ping.")
        except Exception as e:
            print(f"Ping failed: {e}")

        # Make MCP calls within the context
        # tools = await client.list_tools()
        # print(f"Available tools: {tools}")

        # Example: Call an Interactive Brokers API endpoint
        # Replace 'get_iserver_accounts' with an actual tool name from your OpenAPI spec
        # You can find available tool names by inspecting the 'tools' variable.
        # For example, if the OpenAPI spec has a GET /iserver/accounts endpoint,
        # the tool name might be 'get_iserver_accounts'.
        # result = await client.call_tool("get_iserver_accounts")
        # print(f"Accounts result: {result}")
            
    # Connection is closed automatically here
    print(f"Client connected: {client.is_connected()}")

if __name__ == "__main__":
    asyncio.run(main())
    
# Test with:
# uv run -- python /app/client.py
