# trading_contracts.py
from fastapi import APIRouter, Query, Path
from typing import Optional
import httpx
from mcp_server.config import BASE_URL

router = APIRouter()

@router.get(
    "/iserver/secdef/search",
    tags=["Trading Contracts"],
    summary="Search by Symbol or Name",
    description="Search for contracts by symbol or company name. Returns a list of matching contracts."
)
async def search_contract_by_symbol(
    symbol: str = Query(..., description="The symbol or company name to search for."),
    name: Optional[bool] = Query(False, description="Set to true to search by company name instead of symbol."),
    secType: Optional[str] = Query(None, description="The security type to filter by (e.g., STK, OPT, FUT).")
):
    """
    Searches for contracts based on a symbol or name. This is a prerequisite for many other contract-related calls.
    """
    params = {"symbol": symbol}
    if name is not None:
        params["name"] = str(name).lower()
    if secType:
        params["secType"] = secType

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/secdef/search", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.get(
    "/iserver/contract/{conid}/info",
    tags=["Trading Contracts"],
    summary="Contract Information",
    description="Get full contract details for a given contract ID (conid)."
)
async def get_contract_info(
    conid: int = Path(..., description="The contract ID.")
):
    """
    Retrieves detailed information about a specific contract.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/contract/{conid}/info", timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.get(
    "/trsrv/stocks",
    tags=["Trading Contracts"],
    summary="Stocks by Symbol",
    description="Returns a list of stock contracts for the given symbols."
)
async def get_stocks_by_symbol(
    symbols: str = Query(..., description="A comma-separated list of stock symbols.")
):
    """
    Fetches stock contracts for a list of symbols.
    """
    params = {"symbols": symbols}
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/trsrv/stocks", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.get(
    "/iserver/secdef/strikes",
    tags=["Trading Contracts"],
    summary="Option Strikes",
    description="Get a list of available option strikes for a given underlying contract ID (conid)."
)
async def get_strikes(
    conid: int = Query(..., description="The contract ID of the underlying security."),
    secType: str = Query(..., description="The security type (e.g., OPT, WAR)."),
    month: str = Query(..., description="The expiration month in 'MMMYY' format (e.g., JAN25)."),
    exchange: Optional[str] = Query(None, description="The exchange to filter by. Defaults to SMART.")
):
    """
    Retrieves available strike prices for an options contract.
    """
    params = {
        "conid": conid,
        "secType": secType,
        "month": month,
    }
    if exchange:
        params["exchange"] = exchange
        
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/secdef/strikes", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}
