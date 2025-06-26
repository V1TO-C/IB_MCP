# market_data.py
from fastapi import APIRouter, Query, Body, Path
from typing import List, Dict, Any, Union, Optional
import httpx
from pydantic import BaseModel, Field
from mcp_server.config import BASE_URL

router = APIRouter()

# --- Pydantic Models ---

class UnsubscribeRequest(BaseModel):
    """Request model for unsubscribing from a market data conid."""
    conid: str = Field(..., description="The contract ID to unsubscribe from.")


# --- Market Data Field and Availability Information ---

# Data extracted from the "Market Data Fields" table in the API documentation
MARKET_DATA_FIELDS = [
    {"field_code": "31", "type": "String", "name": "Last Price"},
    {"field_code": "55", "type": "String", "name": "Symbol"},
    {"field_code": "58", "type": "String", "name": "Text"},
    {"field_code": "70", "type": "Integer", "name": "High"},
    {"field_code": "71", "type": "Integer", "name": "Low"},
    {"field_code": "72", "type": "Integer", "name": "Position"},
    {"field_code": "73", "type": "Integer", "name": "Market Value"},
    {"field_code": "74", "type": "Double", "name": "Avg Price"},
    {"field_code": "75", "type": "Integer", "name": "Unrealized PNL"},
    {"field_code": "76", "type": "String", "name": "Formatted Position"},
    {"field_code": "77", "type": "String", "name": "Formatted Unrealized PNL"},
    {"field_code": "78", "type": "String", "name": "Daily PNL"},
    {"field_code": "79", "type": "Double", "name": "Realized PNL"},
    {"field_code": "80", "type": "Integer", "name": "Unrealized PNL %"},
    {"field_code": "81", "type": "String", "name": "Change"},
    {"field_code": "82", "type": "String", "name": "Change %"},
    {"field_code": "83", "type": "String", "name": "Implied Volatility %"},
    {"field_code": "84", "type": "String", "name": "Bid Price"},
    {"field_code": "85", "type": "String", "name": "Ask Price"},
    {"field_code": "86", "type": "String", "name": "Ask Size"},
    {"field_code": "87", "type": "String", "name": "Volume"},
    {"field_code": "88", "type": "String", "name": "Bid Size"},
    {"field_code": "6004", "type": "String", "name": "Exchange"},
    {"field_code": "6008", "type": "String", "name": "Conid"},
    {"field_code": "6070", "type": "String", "name": "Security Type"},
    {"field_code": "6072", "type": "Integer", "name": "Months"},
    {"field_code": "6073", "type": "String", "name": "Regular Expiry"},
    {"field_code": "6119", "type": "Double", "name": "Market Cap"},
    {"field_code": "6457", "type": "String", "name": "Listing Exchange"},
    {"field_code": "6508", "type": "Array", "name": "Service Params"},
    {"field_code": "6509", "type": "String", "name": "Market Data Availability"},
    {"field_code": "7051", "type": "String", "name": "Company Name"},
    {"field_code": "7084", "type": "String", "name": "Ask Exch"},
    {"field_code": "7085", "type": "String", "name": "Ask Imp Vol"},
    {"field_code": "7086", "type": "String", "name": "Ask Opt Risk"},
    {"field_code": "7087", "type": "String", "name": "Ask Yield"},
    {"field_code": "7088", "type": "String", "name": "Bid Exch"},
    {"field_code": "7089", "type": "String", "name": "Bid Imp Vol"},
    {"field_code": "7094", "type": "String", "name": "Last Exch"},
    {"field_code": "7219", "type": "String", "name": "Auction Imbalance"},
    {"field_code": "7220", "type": "String", "name": "Auction Volume"},
    {"field_code": "7221", "type": "String", "name": "Auction Price"},
    {"field_code": "7280", "type": "String", "name": "Change since Open"},
    {"field_code": "7281", "type": "String", "name": "Prior Day Close"},
    {"field_code": "7282", "type": "String", "name": "Prior Day Change %"},
    {"field_code": "7284", "type": "String", "name": "Implied Vol % (IV / 13 wk TWS hist volatility)"},
    {"field_code": "7285", "type": "String", "name": "Historic Vol % (13 wk)"},
    {"field_code": "7286", "type": "String", "name": "Historic Vol % (26 wk)"},
    {"field_code": "7287", "type": "String", "name": "Historic Vol % (52 wk)"},
    {"field_code": "7288", "type": "String", "name": "Option Open Interest"},
    {"field_code": "7289", "type": "String", "name": "Option Volume"},
    {"field_code": "7290", "type": "String", "name": "Has Options"},
    {"field_code": "7291", "type": "String", "name": "Last Yield"},
    {"field_code": "7292", "type": "String", "name": "Prior Day Volume"},
    {"field_code": "7293", "type": "String", "name": "Put/Call Ratio"},
    {"field_code": "7294", "type": "String", "name": "Dividend Amount"},
    {"field_code": "7295", "type": "String", "name": "Dividend Yield %"},
    {"field_code": "7296", "type": "String", "name": "Ex-date of dividend"},
    {"field_code": "7633", "type": "String", "name": "VWAP"},
]

# Data extracted from the "Market Data Availability" table
MARKET_DATA_AVAILABILITY = {
    "L": {"name": "Live", "description": "Real-time streaming data. Requires Market Data subscription."},
    "D": {"name": "Delayed", "description": "Delayed streaming data."},
    "Z": {"name": "Frozen", "description": "Last recorded data from the previous day's closing session."},
    "Y": {"name": "Delayed Frozen", "description": "Delayed data from the previous day's closing session."},
    "N": {"name": "Not Subscribed", "description": "Market data is not available."},
    "x": {"name": "Snapshot", "description": "A static snapshot of the current market data."},
    "d": {"name": "Delayed Snapshot", "description": "A static snapshot of delayed market data."}
}

VALID_PERIOD_UNITS = {
    "s": "seconds",
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks",
    "M": "months",
    "y": "years"
}

VALID_BAR_UNITS = {
    "s": "seconds",
    "m": "minutes",
    "h": "hours",
    "d": "days",
    "w": "weeks",
    "M": "months"
}

# --- Market Data Router Endpoints ---

@router.get(
    "/iserver/marketdata/fields",
    tags=["Market Data"],
    summary="Available Market Data Fields",
    description="Returns a list of all available fields for the Market Data Snapshot endpoint."
)
async def get_available_fields() -> List[Dict[str, str]]:
    """
    Provides a list of all possible fields that can be requested from the
    `/iserver/marketdata/snapshot` endpoint. This is a helper endpoint to
    make API usage easier.
    """
    return MARKET_DATA_FIELDS

@router.get(
    "/iserver/marketdata/availability",
    tags=["Market Data"],
    summary="Market Data Availability Codes",
    description="Returns a dictionary explaining the codes used in the 'Market Data Availability' field (6509)."
)
async def get_availability_codes() -> Dict[str, Dict[str, str]]:
    """
    Provides a reference for the market data availability codes returned by the
    API, particularly in field `6509`.
    """
    return MARKET_DATA_AVAILABILITY

@router.get(
    "/iserver/marketdata/periods",
    tags=["Market Data"],
    summary="Valid Historical Data Period Units",
    description="Returns a dictionary of valid period units for historical data requests."
)
async def get_valid_period_units() -> Dict[str, str]:
    """
    Provides a reference for the valid units for the `period` parameter in historical data requests.
    """
    return VALID_PERIOD_UNITS

@router.get(
    "/iserver/marketdata/bars",
    tags=["Market Data"],
    summary="Valid Historical Data Bar Units",
    description="Returns a dictionary of valid bar units for historical data requests."
)
async def get_valid_bar_units() -> Dict[str, str]:
    """
    Provides a reference for the valid units for the `bar` parameter in historical data requests.
    """
    return VALID_BAR_UNITS


@router.get(
    "/iserver/marketdata/snapshot",
    tags=["Market Data"],
    summary="Live Market Data Snapshot",
    description="Get a snapshot of market data for one or more contracts. The snapshot will provide the latest available price, size, and other data points for the given contracts."
)
async def get_marketdata_snapshot(
    conids: str = Query(..., description="A comma-separated list of contract IDs (conids). Example: '265598,265599'"),
    fields: str = Query(..., description="A comma-separated list of field codes to retrieve. Use the '/iserver/marketdata/fields' endpoint to see available fields. Example: '31,84,86'")
) -> List[Dict[str, Any]]:
    """
    ### Get Market Data Snapshot
    Fetches a snapshot of market data for a list of contracts.
    Based on observed behavior, this endpoint is called twice. The first call acts
    as a "pre-flight" or "warm-up" request, and the second call retrieves the full data.

    - **conids**: Provide one or more contract IDs.
    - **fields**: Specify which data fields you want to receive.

    The response is an array of objects, where each object corresponds to a `conid` and contains the requested fields.
    """
    params = {
        "conids": conids,
        "fields": fields
    }
    async with httpx.AsyncClient(verify=False) as client:
        try:
            # First call acts as a "pre-flight" or "warm-up" request to prepare the data feed.
            await client.get(
                f"{BASE_URL}/iserver/marketdata/snapshot",
                params=params,
                timeout=10
            )

            # Second call retrieves the actual market data.
            response = await client.get(
                f"{BASE_URL}/iserver/marketdata/snapshot",
                params=params,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.get(
    "/md/snapshot",
    tags=["Market Data"],
    summary="Market Data Snapshot (Streaming)",
    description="Get a snapshot of market data for a list of conids. This is a non-streaming alternative to the /ws endpoint."
)
async def get_md_snapshot(
    conids: str = Query(..., description="A comma-separated list of contract IDs."),
    fields: Optional[str] = Query(None, description="A comma-separated list of field codes.")
):
    """
    Fetches a non-streaming snapshot of market data, useful for polling updates.
    """
    params = {"conids": conids}
    if fields:
        params["fields"] = fields
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/md/snapshot", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.get(
    "/iserver/marketdata/history",
    tags=["Market Data"],
    summary="Market Data History",
    description="Get historical market data for a contract."
)
async def get_marketdata_history(
    conid: str = Query(..., description="The contract ID."),
    period: str = Query(..., description="The time period for the request, e.g., '1d', '2w', '6M'. Use '/iserver/marketdata/periods' for valid units."),
    bar: Optional[str] = Query(None, description="The bar size, e.g., '1m', '30m', '1h'. Use '/iserver/marketdata/bars' for valid units."),
    exchange: Optional[str] = Query(None, description="The exchange to query. Defaults to the contract's primary exchange."),
    outsideRth: Optional[bool] = Query(False, description="Set to true to include data outside regular trading hours."),
    barType: Optional[str] = Query("trades", description="The type of data to return, e.g., 'trades', 'midpoint', 'bid', 'ask'.")
):
    """
    Fetches historical market data for a single contract.
    """
    params = {
        "conid": conid,
        "period": period,
        "outsideRth": str(outsideRth).lower()
    }
    if bar:
        params["bar"] = bar
    if exchange:
        params["exchange"] = exchange
    if barType:
        params["barType"] = barType

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/marketdata/history", params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.get(
    "/hmds/history",
    tags=["Market Data"],
    summary="Deeper Market Data History",
    description="Get historical market data for a contract from the Historical Market Data Service (HMDS)."
)
async def get_hmds_history(
    conid: str = Query(..., description="The contract ID."),
    period: str = Query(..., description="The time period, e.g., '2d', '1w'."),
    bar: Optional[str] = Query(None, description="The bar size, e.g., '5m', '1h'."),
    outsideRth: Optional[bool] = Query(False, description="Set to true to include data outside regular trading hours."),
    barType: Optional[str] = Query("trades", description="The type of data to return."),
    startTime: Optional[str] = Query(None, description="Specify the start time of the query in 'YYYYMMDD-hh:mm:ss' format.")
):
    """
    Fetches deeper historical market data using the HMDS.
    It first calls /hmds/auth/init to authenticate the session.
    """
    params = {
        "conid": conid,
        "period": period,
        "outsideRth": str(outsideRth).lower()
    }
    if bar:
        params["bar"] = bar
    if barType:
        params["barType"] = barType
    if startTime:
        params["startTime"] = startTime
        
    async with httpx.AsyncClient(verify=False) as client:
        try:
            # Initialize HMDS session to prevent 404 error on the first call
            await client.get(f"{BASE_URL}/hmds/auth/init", timeout=10)
            
            # Now, make the actual history request
            response = await client.get(f"{BASE_URL}/hmds/history", params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.post(
    "/iserver/marketdata/unsubscribe",
    tags=["Market Data"],
    summary="Unsubscribe from Market Data",
    description="Unsubscribes from a specific market data feed."
)
async def unsubscribe_market_data(body: UnsubscribeRequest = Body(...)):
    """
    Unsubscribes from streaming market data for a single contract.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(f"{BASE_URL}/iserver/marketdata/unsubscribe", json=body.dict(), timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.post(
    "/iserver/marketdata/unsubscribeall",
    tags=["Market Data"],
    summary="Unsubscribe from All Market Data",
    description="Unsubscribes from all current market data subscriptions."
)
async def unsubscribe_all_market_data():
    """
    Unsubscribes from all active streaming market data subscriptions.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(f"{BASE_URL}/iserver/marketdata/unsubscribeall", timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}
