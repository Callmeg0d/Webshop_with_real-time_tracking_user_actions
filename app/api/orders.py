from fastapi import APIRouter, Depends

from app.dependencies import get_orders_service, get_current_user
from app.models import Users
from app.services.order_service import OrderService

router = APIRouter(
    prefix="/orders",
    tags=["Заказы"]
)


@router.post("/create")
async def create_order(
        user: Users = Depends(get_current_user),
        order_service: OrderService = Depends(get_orders_service)
):
    order = await order_service.create_order(user.id)
    return {
        "message": "Order created successfully",
        "order_id": order.order_id,
        "total_cost": order.total_cost
    }


@router.get("/")
async def get_user_orders(
        user: Users = Depends(get_current_user),
        order_service: OrderService = Depends(get_orders_service)
):
    return await order_service.get_user_orders(user.id)

