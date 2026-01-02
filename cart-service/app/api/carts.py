from fastapi import APIRouter, Depends

from app.dependencies import get_carts_service
from shared import get_user_id
from app.schemas.carts import UpdateCartItemRequest, SCartItemWithProduct
from app.services.cart_service import CartService

router = APIRouter(
    prefix="/cart",
    tags=["Корзина"]
)


@router.get("/", response_model=list[SCartItemWithProduct])
async def get_cart(
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
) -> list[SCartItemWithProduct]:
    return await cart_service.get_cart_items_with_products(user_id)


@router.post("/add/{product_id}")
async def add_to_cart(
        product_id: int,
        quantity: int = 1,
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
):
    await cart_service.add_to_cart(user_id, product_id, quantity)
    return {"message": "Product added to cart"}


@router.delete("/remove/{product_id}")
async def remove_from_cart(
        product_id: int,
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
):
    await cart_service.remove_cart_item(user_id, product_id)
    return {"message": "Product removed from cart"}


@router.put("/update/{product_id}")
async def update_cart_item(
        product_id: int,
        request: UpdateCartItemRequest,
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
):
    total_cost = await cart_service.update_quantity(user_id, product_id, request.quantity)
    cart_total = await cart_service.get_total_cost(user_id)
    return {
        "message": "Cart updated",
        "total_cost": total_cost,
        "cart_total": cart_total
    }


@router.delete("/clear")
async def clear_cart(
        user_id: int = Depends(get_user_id),
        cart_service: CartService = Depends(get_carts_service)
):
    await cart_service.clear_user_cart(user_id)
    return {"message": "Cart cleared"}

