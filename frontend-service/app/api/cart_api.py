from fastapi import APIRouter, Request, Response, Body
from fastapi.responses import JSONResponse
from shared import get_logger

from app.services.user_client import get_current_user
from app.services.cart_client import get_cart, add_to_cart, update_quantity, remove_from_cart
from app.services.product_client import get_products_by_ids
from app.services.recommend_client import get_recommendations_for_session

router = APIRouter(prefix="/api/cart", tags=["Cart API"])
logger = get_logger(__name__)


async def require_user(request: Request) -> dict | None:
    user = await get_current_user(request.cookies)
    return user


@router.get("/cart/")
async def api_get_cart(request: Request):
    """GET /api/cart/cart/ — корзина текущего пользователя (по cookies)"""
    user = await require_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Необходима авторизация"})
    try:
        items = await get_cart(user["id"])
        return items
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"detail": str(e) or "Ошибка сервиса корзины"},
        )


@router.post("/cart/session-recommendations")
async def api_session_recommendations(request: Request, product_ids: list[int] = Body(..., embed=True)):
    """
    Рекомендации по товарам, добавленным в корзину в этой сессии (id приходят из sessionStorage)
    Исключаем из выдачи всё, что уже в корзине
    """
    user = await require_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Необходима авторизация"})
    if not product_ids:
        return []
    try:
        cart_items = await get_cart(user["id"])
        cart_product_ids = {item["product_id"] for item in cart_items}
        products = await get_products_by_ids(product_ids[:30])
        # Товары сессии (sessionStorage), на основе которых строится запрос к recommendations-service
        session_basis = [
            {
                "product_id": p.get("product_id"),
                "name": (p.get("name") or "")[:120],
            }
            for p in products
        ]
        logger.info(
            "Session recommendations: user_id=%s session_product_ids=%s basis_products=%s "
            "(исключаем из выдачи id корзины: %s)",
            user.get("id"),
            product_ids[:30],
            session_basis,
            sorted(cart_product_ids),
        )
        session_products = [
            {"name": p.get("name", ""), "description": p.get("description", "")}
            for p in products
        ]
        if not session_products:
            return []
        recs = await get_recommendations_for_session(
            products=session_products,
            limit=8,
            exclude_product_ids=cart_product_ids,
        )
        return recs
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"detail": str(e) or "Ошибка рекомендаций"},
        )


@router.post("/cart/{product_id}")
async def api_add_to_cart(request: Request, product_id: int, quantity: int = 1):
    user = await require_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Необходима авторизация"})
    try:
        await add_to_cart(user["id"], product_id, quantity)
        return {"message": "Product added to cart"}
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"detail": str(e) or "Не удалось добавить товар в корзину"},
        )


@router.put("/cart/{product_id}")
async def api_update_cart_item(request: Request, product_id: int):
    """PUT /api/cart/cart/{product_id} — body: { quantity: number }"""
    user = await require_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Необходима авторизация"})
    body = await request.json() if request.headers.get("content-type", "").startswith("application/json") else {}
    quantity = body.get("quantity")
    if quantity is None:
        return JSONResponse(status_code=422, content={"detail": "Укажите quantity"})
    try:
        data = await update_quantity(user["id"], product_id, int(quantity))
        return data
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"detail": str(e) or "Ошибка обновления корзины"},
        )


@router.delete("/cart/{product_id}")
async def api_remove_from_cart(request: Request, product_id: int):
    """DELETE /api/cart/cart/{product_id}"""
    user = await require_user(request)
    if not user:
        return JSONResponse(status_code=401, content={"detail": "Необходима авторизация"})
    try:
        await remove_from_cart(user["id"], product_id)
        return Response(status_code=204)
    except Exception as e:
        return JSONResponse(
            status_code=502,
            content={"detail": str(e) or "Ошибка удаления из корзины"},
        )
