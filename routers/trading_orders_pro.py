# trading_orders.py
from fastapi import APIRouter, Query, Body, Path
from typing import Optional, List, Dict, Any
import httpx
from pydantic import BaseModel, Field
from mcp_server.config import BASE_URL

router = APIRouter()

# --- Pydantic Models for Order Requests ---

class StrategyParameter(BaseModel):
    """Model for individual strategy parameters."""
    name: str = Field(..., description="Name of the parameter")
    value: Any = Field(..., description="Value of the parameter")

class OrderModel(BaseModel):
    """
    Pydantic model representing a single order for placement or modification.
    Based on the structure provided in the IBKR Web API documentation.
    """
    acctId: Optional[str] = Field(None, description="Account ID for the order. Should match the accountId in the path.")
    conid: Optional[int] = Field(None, description="Contract ID for the security. Use either conid or conidex.")
    conidex: Optional[str] = Field(None, description="Contract ID with exchange, e.g., '265598@SMART'. Use for direct routing.")
    secType: Optional[str] = Field(None, description="Security type, e.g., '265598:STK'.")
    cOID: Optional[str] = Field(None, description="Customer-specific order ID. Must be unique for 24 hours.")
    parentId: Optional[str] = Field(None, description="Parent order ID for child orders in bracket or OCA groups.")
    orderType: str = Field(..., description="The type of order, e.g., LMT, MKT, STP.")
    listingExchange: Optional[str] = Field(None, description="Primary routing exchange. Defaults to SMART.")
    outsideRTH: Optional[bool] = Field(False, description="Set to true to allow execution outside regular trading hours.")
    price: Optional[float] = Field(None, description="The limit price for LMT orders, or the stop price for STP orders.")
    auxPrice: Optional[float] = Field(None, description="The auxiliary price, used for STOP_LIMIT and TRAILLMT orders.")
    side: str = Field(..., description="The side of the order: BUY or SELL.")
    ticker: Optional[str] = Field(None, description="The ticker symbol for the contract.")
    tif: str = Field(..., description="The time in force for the order, e.g., GTC, DAY, IOC.")
    quantity: float = Field(..., description="The number of shares or contracts to trade.")
    useAdaptive: Optional[bool] = Field(False, description="Set to true to use the Price Management Algo.")
    strategy: Optional[str] = Field(None, description="The IB Algo strategy to use.")
    strategyParameters: Optional[Dict[str, Any]] = Field(None, description="A dictionary of parameters for the specified IB Algo strategy.")
    # Fields for Futures as per CME Group Rule 536-B
    manualIndicator: Optional[bool] = Field(None, description="Required for Futures/Options on Futures. Indicates manual (true) or automated (false) submission.")
    extOperator: Optional[str] = Field(None, description="Required for Futures/Options on Futures. Identifier of the external operator.")


class OrdersRequest(BaseModel):
    """Request model for placing one or more orders."""
    orders: List[OrderModel]

class ReplyRequest(BaseModel):
    """Request model for confirming an order with a reply ID."""
    confirmed: bool = Field(..., description="Set to true to confirm and submit the order.")

# --- Trading Orders Router Endpoints ---

@router.get(
    "/iserver/account/orders",
    tags=["Trading Orders"],
    summary="Live Orders",
    description="Retrieves a list of live orders (including filled, cancelled, and submitted) for the current brokerage session."
)
async def get_live_orders(
    filters: Optional[str] = Query(
        default=None,
        description="Filter results by a comma-separated list of order statuses. Valid values: Inactive, PendingSubmit, PreSubmitted, Submitted, Filled, PendingCancel, Cancelled, WarnState, SortByTime.",
    ),
    force: Optional[bool] = Query(
        default=False,
        description="Set to true to clear the cache of orders and fetch an updated list."
    )
):
    """
    Fetches live orders from the IBKR API.
    This endpoint is based on the pre-existing trading_orders_base.py.
    """
    params = {}
    if filters:
        params["filters"] = filters
    if force:
        params["force"] = str(force).lower()

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/account/orders", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.post(
    "/iserver/account/{accountId}/orders",
    tags=["Trading Orders"],
    summary="Place Order(s)",
    description="Place one or more orders. For bracket or OCA orders, use the cOID of the parent in the parentId field of the child orders."
)
async def place_order(
    accountId: str = Path(..., description="The account ID to place the order for."),
    body: OrdersRequest = Body(...)
):
    """
    Places one or more orders for the specified account.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/account/{accountId}/orders",
                json=body.dict(exclude_none=True),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.post(
    "/iserver/account/{accountId}/orders/whatif",
    tags=["Trading Orders"],
    summary="Preview Order / What-If",
    description="Preview an order without submitting it to get commission and margin impact information."
)
async def preview_order(
    accountId: str = Path(..., description="The account ID for the what-if analysis."),
    body: OrdersRequest = Body(...)
):
    """
    Previews an order to see its potential impact on the account.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/account/{accountId}/orders/whatif",
                json=body.dict(exclude_none=True),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.get(
    "/iserver/account/order/status/{orderId}",
    tags=["Trading Orders"],
    summary="Order Status",
    description="Retrieves the status of a single order."
)
async def get_order_status(
    orderId: str = Path(..., description="The order ID of the order to check.")
):
    """
    Fetches the status for a specific order.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/account/order/status/{orderId}", timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.post(
    "/iserver/account/{accountId}/order/{orderId}",
    tags=["Trading Orders"],
    summary="Modify Order",
    description="Modifies an existing open order."
)
async def modify_order(
    accountId: str = Path(..., description="The account ID of the order."),
    orderId: str = Path(..., description="The order ID of the order to modify."),
    body: OrderModel = Body(...)
):
    """
    Modifies an existing order. The request body should contain the updated order details.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/account/{accountId}/order/{orderId}",
                json=body.dict(exclude_none=True),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.delete(
    "/iserver/account/{accountId}/order/{orderId}",
    tags=["Trading Orders"],
    summary="Cancel Order",
    description="Cancels an open order."
)
async def cancel_order(
    accountId: str = Path(..., description="The account ID of the order."),
    orderId: str = Path(..., description="The order ID of the order to cancel.")
):
    """
    Cancels an active order.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.delete(
                f"{BASE_URL}/iserver/account/{accountId}/order/{orderId}",
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.post(
    "/iserver/reply/{replyId}",
    tags=["Trading Orders"],
    summary="Place Order Reply",
    description="Reply to a confirmation message received after attempting to place an order."
)
async def place_order_reply(
    replyId: str = Path(..., description="The ID of the message to reply to."),
    body: ReplyRequest = Body(...)
):
    """
    Confirms an order that requires a secondary confirmation (e.g., due to price constraints).
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/reply/{replyId}",
                json=body.dict(),
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.get(
    "/iserver/account/trades",
    tags=["Trading Orders"],
    summary="List of Trades",
    description="Returns a list of trades for the currently selected account for the current and previous six days."
)
async def get_trades(
    days: Optional[str] = Query(None, description="Number of days to retrieve trades for, up to a maximum of 7.")
):
    """
    Retrieves a list of recent trades.
    """
    params = {}
    if days:
        params["days"] = days
        
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/account/trades", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}
