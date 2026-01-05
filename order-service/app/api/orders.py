from fastapi import APIRouter, Depends

from app.dependencies import get_orders_service
from shared import get_user_id, get_logger
from app.services.order_service import OrderService
from app.schemas.orders import SUserOrder

router = APIRouter(
    prefix="/orders",
    tags=["Заказы"]
)

logger = get_logger(__name__)


@router.post("/create")
async def create_order(
        user_id: int = Depends(get_user_id),
        order_service: OrderService = Depends(get_orders_service)
):
    logger.info(f"POST /orders/create request from user {user_id}")
    try:
        order = await order_service.create_order(user_id)
        logger.info(f"Order {order.order_id} created via API for user {user_id}")
        return {
            "message": "Order created successfully",
            "order_id": order.order_id,
            "total_cost": order.total_cost
        }
    except Exception as e:
        logger.error(f"Error creating order by API for user {user_id}: {e}", exc_info=True)
        raise


@router.get("/", response_model=list[SUserOrder])
async def get_user_orders(
        user_id: int = Depends(get_user_id),
        order_service: OrderService = Depends(get_orders_service)
) -> list[SUserOrder]:
    logger.info(f"GET /orders/ request from user {user_id}")
    try:
        orders = await order_service.get_user_orders(user_id)
        logger.info(f"Returned {len(orders)} orders for user {user_id}")
        return orders
    except Exception as e:
        logger.error(f"Error fetching orders by API for user {user_id}: {e}", exc_info=True)
        raise

