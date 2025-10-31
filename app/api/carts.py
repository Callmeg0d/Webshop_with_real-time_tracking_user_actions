from fastapi import APIRouter, Depends
from app.dependencies import get_carts_service, get_current_user, get_products_service
from app.models import Users
from app.schemas.carts import UpdateCartItemRequest
from app.services.cart_service import CartService
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/cart",
    tags=["Корзина"]
)


@router.get("/")
async def get_cart(
        user: Users = Depends(get_current_user),
        cart_service: CartService = Depends(get_carts_service)
):
    return await cart_service.get_cart_items_with_products(user.id)


@router.post("/add/{product_id}")
async def add_to_cart(
        product_id: int,
        quantity: int = 1,
        user: Users = Depends(get_current_user),
        cart_service: CartService = Depends(get_carts_service),
        product_service: ProductService = Depends(get_products_service)
):
    product = await product_service.get_product_by_id(product_id)
    
    # Проверяем, есть ли уже этот товар в корзине
    existing_item = await cart_service.get_cart_item_by_id(user.id, product_id)
    
    if existing_item:
        # Обновляем количество
        await cart_service.update_cart_item(
            user_id=user.id,
            product_id=product_id,
            quantity_add=quantity,
            cost_add=product.price * quantity
        )
    else:
        # Добавляем новый товар
        await cart_service.add_cart_item(
            user_id=user.id,
            product_id=product_id,
            quantity=quantity,
            total_cost=product.price * quantity
        )
    
    return {"message": "Product added to cart"}


@router.delete("/remove/{product_id}")
async def remove_from_cart(
        product_id: int,
        user: Users = Depends(get_current_user),
        cart_service: CartService = Depends(get_carts_service)
):
    await cart_service.remove_cart_item(user.id, product_id)
    return {"message": "Product removed from cart"}


@router.put("/update/{product_id}")
async def update_cart_item(
        product_id: int,
        request: UpdateCartItemRequest,
        user: Users = Depends(get_current_user),
        cart_service: CartService = Depends(get_carts_service)
):
    total_cost = await cart_service.update_quantity(user.id, product_id, request.quantity)
    cart_total = await cart_service.get_total_cost(user.id)
    return {
        "message": "Cart updated",
        "total_cost": total_cost,
        "cart_total": cart_total
    }


@router.delete("/clear")
async def clear_cart(
        user: Users = Depends(get_current_user),
        cart_service: CartService = Depends(get_carts_service)
):
    await cart_service.clear_user_cart(user.id)
    return {"message": "Cart cleared"}

