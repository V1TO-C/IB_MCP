# trading_accounts.py
from fastapi import APIRouter, Query, Path, Body
from typing import Optional, List
import httpx
from pydantic import BaseModel, Field
from mcp_server.config import BASE_URL

router = APIRouter()

# --- Pydantic Models ---
class SwitchAccountRequest(BaseModel):
    acctId: str

# --- Router Endpoints ---

@router.get(
    "/iserver/accounts",
    tags=["Trading Accounts"],
    summary="Brokerage Accounts",
    description="Returns a list of accounts the user has trading access to, their respective aliases, and the currently selected account."
)
async def get_brokerage_accounts():
    """
    Fetches all brokerage accounts for the current user.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/accounts", timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}

@router.post(
    "/iserver/account",
    tags=["Trading Accounts"],
    summary="Switch Account",
    description="Switch the active account. This is for Financial Advisor and multi-account structures."
)
async def switch_account(body: SwitchAccountRequest = Body(...)):
    """
    Sets the active account for the session.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/account",
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
    "/iserver/account/pnl/partitioned",
    tags=["Trading Accounts"],
    summary="Account PnL",
    description="Returns an object containing PnL for the selected account and its models (if any)."
)
async def get_account_pnl():
    """
    Fetches the partitioned Profit and Loss for the currently selected account.
    """
    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(f"{BASE_URL}/iserver/account/pnl/partitioned", timeout=10)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as exc:
            return {"error": "IBKR API Error", "status_code": exc.response.status_code, "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": "Request Error", "detail": str(exc)}
