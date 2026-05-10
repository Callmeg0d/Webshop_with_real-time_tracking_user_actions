from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, Response
import httpx

from app.config import settings
from app.services.user_client import get_current_user
from shared import get_logger
from shared.constants import HttpHeaders, HttpTimeout

logger = get_logger(__name__)

router = APIRouter(prefix="/api/order", tags=["Order API"])


def _order_base() -> str:
    return settings.ORDER_SERVICE_URL.rstrip("/")


@router.post("/orders/")
async def create_order(request: Request):
    user = await get_current_user(request.cookies)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Необходима авторизация"})
    try:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{_order_base()}/orders/",
                headers={HttpHeaders.X_USER_ID.value: str(user["id"])},
                timeout=HttpTimeout.GATEWAY.value,
            )
        return Response(
            content=r.content,
            status_code=r.status_code,
            media_type=r.headers.get("content-type") or "application/json",
        )
    except httpx.RequestError as e:
        logger.error("Order service unreachable (create): %s", e)
        return JSONResponse(status_code=502, content={"detail": "Сервис заказов недоступен"})


@router.get("/orders")
@router.get("/orders/")
async def list_orders(request: Request):
    user = await get_current_user(request.cookies)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Необходима авторизация"})
    try:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{_order_base()}/orders/",
                headers={HttpHeaders.X_USER_ID.value: str(user["id"])},
                timeout=HttpTimeout.GATEWAY.value,
            )
        return Response(
            content=r.content,
            status_code=r.status_code,
            media_type=r.headers.get("content-type") or "application/json",
        )
    except httpx.RequestError as e:
        logger.error("Order service unreachable (list): %s", e)
        return JSONResponse(status_code=502, content={"detail": "Сервис заказов недоступен"})
