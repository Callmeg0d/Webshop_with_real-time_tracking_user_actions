from fastapi import APIRouter, Depends

from app.dependencies import get_orders_service
from shared import get_user_id
from app.services.order_service import OrderService
from app.schemas.orders import SUserOrder

router = APIRouter(
    prefix="/orders",
    tags=["Заказы"]
)


@router.post("/create")
async def create_order(
        user_id: int = Depends(get_user_id),
        order_service: OrderService = Depends(get_orders_service)
):
    order = await order_service.create_order(user_id)
    return {
        "message": "Order created successfully",
        "order_id": order.order_id,
        "total_cost": order.total_cost
    }


@router.get("/", response_model=list[SUserOrder])
async def get_user_orders(
        user_id: int = Depends(get_user_id),
        order_service: OrderService = Depends(get_orders_service)
) -> list[SUserOrder]:
    return await order_service.get_user_orders(user_id)

