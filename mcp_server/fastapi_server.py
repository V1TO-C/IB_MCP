from fastapi import FastAPI
from fastmcp import FastMCP
from mcp_server.config import MCP_SERVER_HOST, MCP_SERVER_PORT, MCP_TRANSPORT_PROTOCOL
import trading_orders_base
import portfolio
# import account_management
# import trading

app = FastAPI(
    title="IBKR Trading Orders API",
    description="Retrieves open orders and filled or cancelled orders submitted during the current brokerage session.",
    version="1.0.0"
)

app.include_router(trading_orders_base.router)
app.include_router(portfolio.router)

mcp = FastMCP.from_fastapi(app=app)

if __name__ == "__main__":
    mcp.run(
        transport=MCP_TRANSPORT_PROTOCOL,
        host=MCP_SERVER_HOST,
        port=MCP_SERVER_PORT,
        log_level="DEBUG",
    )
