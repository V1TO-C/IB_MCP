# trading_orders.py
from fastapi import APIRouter, Query, Path, Body, Header, Cookie
from typing import Optional, List, Any, Dict
import httpx
# Assuming BASE_URL is configured in mcp_server.config
from mcp_server.config import BASE_URL

router = APIRouter()

@router.get(
    "/iserver/account/order/status/{orderId}",
    tags=["Trading Orders"],
    summary="Retrieve The Status Of A Single Order."
)
async def get_order_status_by_order_id(
    order_id: str = Path(
        default=...,
        description="The IB-assigned order ID of the desired order ticket.",
        examples=["1799796559"],
    )
):
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/iserver/account/order/status/{order_id}",
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.get(
    "/iserver/account/orders",
    tags=["Trading Orders"],
    summary="Retrieves Open Orders And Filled Or Cancelled Orders Submitted During The Current Brokerage Session."
)
async def get_iserver_account_orders(
    filters: Optional[str] = Query(
        default=None,
        description="Filter results using a comma-separated list of Order Status values. Also accepts a value to sort results by time.",
        enum=['Inactive', 'PendingSubmit', 'PreSubmitted', 'Submitted', 'Filled', 'PendingCancel', 'Cancelled', 'WarnState', 'SortByTime'],
        examples=["Filled,SortByTime"],
    ),
    force: Optional[bool] = Query(
        default=None,
        description="Instructs IB to clear cache of orders and obtain updated view from brokerage backend. Response will be an empty array.",
    ),
    account_id: Optional[str] = Query(
        default=None,
        description="Retrieve orders for a specific account in the structure.",
        examples=["DU123456"],
    )
):
    params = {}
    if filters is not None:
        params["filters"] = filters
    if force is not None:
        params["force"] = str(force).lower()  # IBKR expects "true"/"false" for booleans
    if account_id is not None:
        params["accountId"] = account_id

    headers = {}

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
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.get(
    "/iserver/account/trades",
    tags=["Trading Orders"],
    summary="Retrieve A List Of Trades."
)
async def get_iserver_account_trades(
    days: Optional[str] = Query(
        default=None,
        description="The number of prior days prior to include in response, up to a maximum of 7. If omitted, only the current day's executions will be returned.",
        examples=["3"],
    ),
    account_id: Optional[str] = Query(
        default=None,
        description="Filter trades by account ID or allocation group.",
        examples=["DU123456"],
    )
):
    params = {}
    if days is not None:
        params["days"] = days
    if account_id is not None:
        params["accountId"] = account_id

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.get(
                f"{BASE_URL}/iserver/account/trades",
                params=params,
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.post(
    "/iserver/account/{account_id}/order/{order_id}",
    tags=["Trading Orders"],
    summary="Modify An Existing, Unfilled Order."
)
async def post_iserver_account_order_by_account_id_and_order_id(
    account_id: str = Path(
        default=...,
        description="The account to which the order will clear.",
        examples=["DU123456"],
    ),
    order_id: str = Path(
        default=...,
        description="The IB-assigned order ID of the desired order ticket.",
        examples=["1799796559"],
    ),
    body_data: Dict[str, Any] = Body(..., description="A single order ticket.")
):
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/account/{account_id}/order/{order_id}",
                json=body_data,
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.delete(
    "/iserver/account/{account_id}/order/{order_id}",
    tags=["Trading Orders"],
    summary="Cancel An Existing, Unfilled Order."
)
async def delete_iserver_account_order_by_account_id_and_order_id(
    account_id: str = Path(
        default=...,
        description="The account to which the order will clear.",
        examples=["DU123456"],
    ),
    order_id: str = Path(
        default=...,
        description="The IB-assigned order ID of the desired order ticket.",
        examples=["1799796559"],
    )
):
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.delete(
                f"{BASE_URL}/iserver/account/{account_id}/order/{order_id}",
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.post(
    "/iserver/account/{account_id}/orders",
    tags=["Trading Orders"],
    summary="Submit A New Order(s) Ticket, Bracket, Or OCA Group."
)
async def post_iserver_account_orders_by_account_id(
    account_id: str = Path(
        default=...,
        description="The account to which the order will clear.",
        examples=["DU123456"],
    ),
    body_data: List[Dict[str, Any]] = Body(..., description="Array of order tickets objects. Only one order ticket object may be submitted per request, unless constructing a bracket.")
):
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/account/{account_id}/orders",
                json=body_data,
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.post(
    "/iserver/account/{account_id}/orders/whatif",
    tags=["Trading Orders"],
    summary="Preview The Projected Effects Of An Order Ticket Or Bracket Of Orders, Including Cost And Changes To Margin And Account Equity."
)
async def post_iserver_account_orders_whatif_by_account_id(
    account_id: str = Path(
        default=...,
        description="The account to which the order will clear.",
        examples=["DU123456"],
    ),
    body_data: List[Dict[str, Any]] = Body(..., description="Array of order tickets objects. Only one order ticket object may be submitted per request, unless constructing a bracket.")
):
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/account/{account_id}/orders/whatif",
                json=body_data,
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.post(
    "/iserver/notification",
    tags=["Trading Orders"],
    summary="Respond To A Server Prompt."
)
async def post_iserver_notification(
    body_data: Dict[str, Any] = Body(..., description="Request body")
):
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/notification",
                json=body_data,
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.post(
    "/iserver/questions/suppress",
    tags=["Trading Orders"],
    summary="Suppress The Specified Order Reply Messages."
)
async def post_iserver_questions_suppress(
    body_data: Dict[str, Any] = Body(..., description="Request body")
):
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/questions/suppress",
                json=body_data,
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.post(
    "/iserver/questions/suppress/reset",
    tags=["Trading Orders"],
    summary="Removes Suppression Of All Order Reply Messages."
)
async def post_iserver_questions_suppress_reset():
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/questions/suppress/reset",
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()

@router.post(
    "/iserver/reply/{reply_id}",
    tags=["Trading Orders"],
    summary="Confirm An Order Reply Message."
)
async def post_iserver_reply_by_reply_id(
    reply_id: str = Path(
        default=...,
        description="The UUID of the reply message to be confirmed, obtained from an order submission response.",
        examples=["99097238-9824-4830-84ef-46979aa22593"],
    ),
    body_data: Dict[str, Any] = Body(..., description="Request body")
):
    params = {}

    headers = {}

    async with httpx.AsyncClient(verify=False) as client:
        try:
            response = await client.post(
                f"{BASE_URL}/iserver/reply/{reply_id}",
                json=body_data,
                timeout=10
            )
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            return {"error": f"IBKR API error {exc.response.status_code}", "detail": exc.response.text}
        except httpx.RequestError as exc:
            return {"error": f"An error occurred while requesting {exc.request.url!r}.", "detail": str(exc)}

    return response.json()
