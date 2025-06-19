from fastapi import APIRouter, Query
from typing import Optional, List
import httpx
from mcp_server.config import BASE_URL

router = APIRouter()

@router.get(
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
