from fastapi import APIRouter, Depends, HTTPException

from app.exceptions import (
    CannotMakeOrderWithoutAddress,
    CannotMakeOrderWithoutItems,
    NotEnoughProductsInStock,
)
from app.orders.dao import OrdersDAO
from app.orders.schemas import SOrderResponse
from app.products.dao import ProductDAO
from app.tasks.tasks import send_order_confirmation_email
from app.users.dependencies import get_current_user
from app.models.users import Users

router = APIRouter(
    prefix="/orders",
    tags=["Заказы"]
)


@router.get("")
async def get_orders(user: Users = Depends(get_current_user)):
    orders = await OrdersDAO.find_all(user_id=user.id)

    for order in orders:
        if "order_items" not in order or not order["order_items"]:
            continue  # Пропускаем заказ, если в нем нет товаров

        for item in order["order_items"]:
            product_id = item.get("product_id")
            if product_id is None:
                continue

            product = await ProductDAO.find_one_or_none(product_id=product_id)

            product_image_url = f"/static/images/{product['image']}.webp"

            item["product_image_url"] = product_image_url

    return orders


@router.post("/checkout")
async def make_order(user: Users = Depends(get_current_user)) -> SOrderResponse:
    if user.delivery_address is None:
        raise CannotMakeOrderWithoutAddress

    try:
        order = await OrdersDAO.make_order(user_id=user.id)
    except NotEnoughProductsInStock:
        raise HTTPException(status_code=400, detail="Недостаточно товара на складе")

    if not order:
        raise CannotMakeOrderWithoutItems

    order_response = SOrderResponse.model_validate(order)

    # Отправка письма с подтверждением
    send_order_confirmation_email.delay(order_response.model_dump(), user.email)
    return order_response
