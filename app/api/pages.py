from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.dependencies import (
    get_current_user,
    get_products_service,
    get_carts_service,
    get_reviews_service
)
from app.models.users import Users
from app.services.product_service import ProductService
from app.services.cart_service import CartService
from app.services.review_service import ReviewService

router = APIRouter(
    prefix="/pages",
    tags=["Фронтенд"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("auth/login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("auth/register.html", {"request": request})


@router.get("/products")
async def get_product_page(
        request: Request,
        product_service: ProductService = Depends(get_products_service)
):
    products = await product_service.get_all_products()
    return templates.TemplateResponse(
        name="products.html",
        context={"request": request, "products": products}
    )


@router.get("/cart")
async def get_cart_page(
        request: Request,
        user: Users = Depends(get_current_user),
        cart_service: CartService = Depends(get_carts_service)
):
    cart_items = await cart_service.get_cart_items_with_products(user.id)
    total_cart_cost = sum(item.get("total_cost", 0) for item in cart_items)
    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "cart_items": cart_items,
            "total_cart_cost": total_cart_cost
        },
    )


@router.get("/product/{product_id}")
async def get_product_detail_page(
        request: Request,
        product_id: int,
        product_service: ProductService = Depends(get_products_service),
        review_service: ReviewService = Depends(get_reviews_service)
):
    product = await product_service.get_product_by_id(product_id)
    reviews = await review_service.get_reviews(product_id)
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
        "reviews": reviews
    })


@router.get("/profile")
async def get_profile(request: Request, user: Users = Depends(get_current_user)):
    return (templates.TemplateResponse
            ("profile.html",
             {"request": request, "user": user})
            )
