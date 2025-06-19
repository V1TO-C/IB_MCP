from fastapi import FastAPI, Query
from typing import Optional, List
import httpx
import os
import uvicorn
from fastmcp import FastMCP


# Load environment variables
# GATEWAY_BASE_URL = os.environ.get("GATEWAY_BASE_URL")
GATEWAY_PORT = os.environ.get("GATEWAY_PORT")
GATEWAY_ENDPOINT = os.environ.get("GATEWAY_ENDPOINT")
GATEWAY_INTERNAL_BASE_URL = os.environ.get("GATEWAY_INTERNAL_BASE_URL")
# GATEWAY_TEST_ENDPOINT = os.environ.get("GATEWAY_TEST_ENDPOINT")

MCP_SERVER_BASE_URL = os.environ.get("MCP_SERVER_BASE_URL")
MCP_SERVER_INTERNAL_BASE_URL = os.environ.get("MCP_SERVER_INTERNAL_BASE_URL")
MCP_SERVER_HOST = os.environ.get("MCP_SERVER_HOST")
MCP_TRANSPORT_PROTOCOL = os.environ.get("MCP_TRANSPORT_PROTOCOL")
MCP_SERVER_PORT = os.environ.get("MCP_SERVER_PORT")


BASE_URL = f"{GATEWAY_INTERNAL_BASE_URL}:{GATEWAY_PORT}{GATEWAY_ENDPOINT}"

app = FastAPI(
    title="IBKR Trading Orders API",
    description="Retrieves open orders and filled or cancelled orders submitted during the current brokerage session.",
    version="1.0.0"
)

@app.get(
    "/iserver/account/orders",
    tags=["Trading Orders"],
    summary="Retrieves Open Orders And Filled Or Cancelled Orders Submitted During The Current Brokerage Session."
)
async def get_orders(
    filters: Optional[str] = Query(
        default=None,
        description="Filter results using a comma-separated list of Order Status values. Also accepts a value to sort results by time.",
        enum=[
            "Inactive", "PendingSubmit", "PreSubmitted", "Submitted", "Filled",
            "PendingCancel", "Cancelled", "WarnState", "SortByTime"
        ]
    ),
    force: Optional[bool] = Query(
        default=None,
        description="Instructs IB to clear cache of orders and obtain updated view from brokerage backend."
    ),
    accountId: Optional[str] = Query(
        default=None,
        description="Retrieve orders for a specific account in the structure.",
        examples=["DU123456"]
    )
):
    params = {}
    if filters:
        params["filters"] = filters
    if force is not None:
        params["force"] = str(force).lower()  # IBKR expects "true"/"false"
    if accountId:
        params["accountId"] = accountId

    # TODO: We need to add verification in production
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/iserver/account/orders",
                params=params,
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}

    return response.json()


mcp = FastMCP.from_fastapi(app=app)
# if __name__ == "__main__":
#     uvicorn.run("fastapi_server:app", 
#                 host=MCP_SERVER_HOST,   
#                 port=int(MCP_SERVER_PORT), 
#                 log_level="debug", 
#                 reload=True)

if __name__ == "__main__":
    mcp.run(
        transport=MCP_TRANSPORT_PROTOCOL,
        host=MCP_SERVER_HOST,           # Bind to all interfaces
        port=MCP_SERVER_PORT,                # Custom port
        log_level="DEBUG",        # Override global log level
    )
