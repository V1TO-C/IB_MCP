# contract.py
from fastapi import APIRouter, Query, Body, Path
from typing import List, Optional
import httpx
from pydantic import BaseModel, Field
from mcp_server.config import BASE_URL

router = APIRouter()

# --- Pydantic Models ---

class ContractRulesRequest(BaseModel):
    """Request model for the Contract Rules endpoint."""
    conid: int = Field(..., description="The contract ID for which to retrieve trading rules.")
    isBuy: bool = Field(..., description="Specify true for buy side rules, false for sell side rules.")

    class Config:
        schema_extra = {
            "example": {
                "conid": 265598, # IBM
                "isBuy": True
            }
        }


# --- Contract Router Endpoints ---

@router.get(
    "/iserver/secdef/search",
    tags=["Contract"],
    summary="Search by Symbol or Name",
    description="Search for contracts by symbol or company name. Returns a list of matching contracts."
)
async def search_contract_by_symbol_or_name(
    symbol: str = Query(..., description="The symbol or company name to search for."),
    name: Optional[bool] = Query(False, description="Set to true to search by company name instead of symbol."),
    secType: Optional[str] = Query(None, description="The security type to filter by (e.g., STK, OPT, FUT).")
):
    """
    Searches for contracts based on a symbol or name. This is a primary method for finding a contract's conid.
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
    "/trsrv/stocks",
    tags=["Contract"],
    summary="Stocks by Symbol",
    description="Returns a list of stock contracts for the given symbols."
)
async def get_stocks_by_symbol(
    symbols: str = Query(..., description="A comma-separated list of stock symbols.")
):
    """
    Fetches stock contracts for a list of symbols. This is more direct than a general search if you know you are looking for stocks.
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
    "/iserver/contract/{conid}/info",
    tags=["Contract"],
    summary="Contract Information",
    description="Get full contract details for a given contract ID (conid)."
)
async def get_contract_info(
    conid: int = Path(..., description="The contract ID.")
):
    """
    Retrieves detailed information about a specific contract using its conid.
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


@router.post(
    "/iserver/contract/rules",
    tags=["Contract"],
    summary="Contract Rules",
    description="Returns trading rules for a contract. The request body requires the conid and a boolean for the side."
)
async def get_contract_rules(body: ContractRulesRequest = Body(...)):
    """
    Fetches the trading rules for a given contract, such as order types and sizes.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/contract/rules",
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
    "/iserver/secdef/info",
    tags=["Contract"],
    summary="Secdef Info",
    description="Provides security definition and rules information for a given conid."
)
async def get_secdef_info(
    conid: str = Query(..., description="The contract ID."),
    secType: str = Query(..., description="The security type."),
    month: Optional[str] = Query(None, description="The expiration month for options/futures (e.g., 'DEC23')."),
    exchange: Optional[str] = Query(None, description="The exchange to query."),
    strike: Optional[float] = Query(None, description="The strike price for options."),
    right: Optional[str] = Query(None, description="The right for options: 'C' for Call, 'P' for Put.")
):
    """
    A comprehensive endpoint to get instrument metadata and rules in one call.
    """
    params = {"conid": conid, "secType": secType}
    if month:
        params["month"] = month
    if exchange:
        params["exchange"] = exchange
    if strike:
        params["strike"] = strike
    if right:
        params["right"] = right

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/secdef/info", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.get(
    "/iserver/secdef/strikes",
    tags=["Contract"],
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
    Retrieves available strike prices for an options contract based on the underlying conid, security type, and expiration.
    """
    params = {"conid": conid, "secType": secType, "month": month}
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


@router.get(
    "/iserver/secdef/futures",
    tags=["Contract"],
    summary="Futures by Symbol",
    description="Returns a list of non-expired future contracts for the given symbol(s)."
)
async def get_futures_by_symbol(
    symbols: str = Query(..., description="A comma-separated list of underlying symbols.")
):
    """
    Search for future contracts for one or more underlying symbols.
    """
    params = {"symbols": symbols}
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/secdef/futures", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.get(
    "/trsrv/futures",
    tags=["Contract"],
    summary="Futures Details by Symbol",
    description="Returns a list of futures for the given symbols."
)
async def get_trsrv_futures_by_symbol(
    symbols: str = Query(..., description="A comma-separated list of underlying symbols.")
):
    """
    Get detailed information about futures contracts for given symbols.
    """
    params = {"symbols": symbols}
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/trsrv/futures", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.get(
    "/trsrv/options",
    tags=["Contract"],
    summary="Options by Symbol",
    description="Returns a list of options for a given underlying conid."
)
async def get_options_by_conid(
    conid: str = Query(..., description="The contract ID of the underlying security."),
    secType: Optional[str] = Query(None, description="The security type, e.g., 'OPT'"),
    month: Optional[str] = Query(None, description="The expiration month (YYYYMM)."),
    exchange: Optional[str] = Query(None, description="The exchange to query.")
):
    """
    Get a list of option contracts for a specific underlying.
    """
    params = {"conid": conid}
    if secType:
        params["secType"] = secType
    if month:
        params["month"] = month
    if exchange:
        params["exchange"] = exchange

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/trsrv/options", params=params, timeout=20)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}


@router.get(
    "/iserver/secdef/search/strikes",
    tags=["Contract"],
    summary="Search Strikes",
    description="Search for available strikes for a given option contract."
)
async def search_strikes(
    conid: str = Query(..., description="The contract ID of the underlying security."),
    secType: str = Query(..., description="The security type (e.g., OPT)."),
    month: str = Query(..., description="The expiration month (YYYYMM)."),
    exchange: Optional[str] = Query(None, description="The exchange to query.")
):
    """
    Search for option strikes by underlying conid, security type, and expiration month.
    """
    params = {"conid": conid, "secType": secType, "month": month}
    if exchange:
        params["exchange"] = exchange
        
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/secdef/search/strikes", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.get(
    "/iserver/secdef/bonds",
    tags=["Contract"],
    summary="Search Bonds",
    description="Search for bond contracts by symbol or CUSIP."
)
async def search_bonds(
    symbol: str = Query(..., description="The symbol or CUSIP of the bond.")
):
    """
    Fetches bond contracts matching a symbol or CUSIP.
    """
    params = {"symbol": symbol}
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/secdef/bonds", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.get(
    "/iserver/secdef/currency",
    tags=["Contract"],
    summary="Search Currency Pairs",
    description="Search for currency pairs."
)
async def search_currency(
    symbol: str = Query(..., description="The currency pair (e.g., EUR.USD).")
):
    """
    Retrieves information about a currency pair.
    """
    params = {"symbol": symbol}
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/secdef/currency", params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}
