from fastapi import APIRouter, Depends
from shared import get_user_id, get_logger

from app.dependencies import get_carts_service
from app.schemas.carts import UpdateCartItemRequest, SCartItemWithProduct
from app.services.cart_service import CartService

router = APIRouter(
    prefix="/cart",
    tags=["Корзина"]
)

logger = get_logger(__name__)


@router.get("/", response_model=list[SCartItemWithProduct])
async def get_cart(
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
) -> list[SCartItemWithProduct]:
    logger.info(f"GET /cart/ request from user {user_id}")
    try:
        cart_items = await cart_service.get_cart_items_with_products(user_id)
        logger.info(f"Returned {len(cart_items)} cart items for user {user_id}")
        return cart_items
    except Exception as e:
        logger.error(f"Error fetching cart by API for user {user_id}: {e}", exc_info=True)
        raise


@router.post("/add/{product_id}")
async def add_to_cart(
        product_id: int,
        quantity: int = 1,
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
):
    logger.info(f"POST /cart/add/{product_id} request from user {user_id}, quantity: {quantity}")
    try:
        await cart_service.add_to_cart(user_id, product_id, quantity)
        logger.info(f"Product {product_id} added to cart by API for user {user_id}")
        return {"message": "Product added to cart"}
    except Exception as e:
        logger.error(f"Error adding product {product_id} to cart by API for user {user_id}: {e}", exc_info=True)
        raise


@router.delete("/remove/{product_id}")
async def remove_from_cart(
        product_id: int,
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
):
    logger.info(f"DELETE /cart/remove/{product_id} request from user {user_id}")
    try:
        await cart_service.remove_cart_item(user_id, product_id)
        logger.info(f"Product {product_id} removed from cart by API for user {user_id}")
        return {"message": "Product removed from cart"}
    except Exception as e:
        logger.error(f"Error removing product {product_id} from cart by API for user {user_id}: {e}", exc_info=True)
        raise


@router.put("/update/{product_id}")
async def update_cart_item(
        product_id: int,
        request: UpdateCartItemRequest,
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
):
    logger.info(f"PUT /cart/update/{product_id} request from user {user_id}, quantity: {request.quantity}")
    try:
        total_cost = await cart_service.update_quantity(user_id, product_id, request.quantity)
        cart_total = await cart_service.get_total_cost(user_id)
        logger.info(f"Cart item updated by API for user {user_id}, total_cost: {total_cost}, cart_total: {cart_total}")
        return {
            "message": "Cart updated",
            "total_cost": total_cost,
            "cart_total": cart_total
        }
    except Exception as e:
        logger.error(f"Error updating cart item by API for user {user_id}: {e}", exc_info=True)
        raise


@router.delete("/clear")
async def clear_cart(
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
):
    logger.info(f"DELETE /cart/clear request from user {user_id}")
    try:
        await cart_service.clear_user_cart(user_id)
        logger.info(f"Cart cleared by API for user {user_id}")
        return {"message": "Cart cleared"}
    except Exception as e:
        logger.error(f"Error clearing cart by API for user {user_id}: {e}", exc_info=True)
        raise

