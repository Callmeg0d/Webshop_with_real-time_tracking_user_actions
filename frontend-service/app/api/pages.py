from math import ceil

from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app.services.user_client import get_current_user, login_user, register_user
from app.services.product_client import get_all_products, get_product, get_products_count
from app.services.cart_client import get_cart
from app.services.review_client import get_reviews

router = APIRouter(
    tags=["Фронтенд"]
)

templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def get_login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        result = await login_user(email, password)
        response = RedirectResponse(url="/products", status_code=302)
        # Cookies устанавливаются user-service, но нужно их проксировать
        return response
    except Exception:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Неверный email или пароль"}
        )


@router.get("/register", response_class=HTMLResponse)
async def get_register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.post("/register")
async def post_register(
    request: Request,
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        await register_user(email, password)
        return RedirectResponse(url="/login", status_code=302)
    except Exception:
        return templates.TemplateResponse(
            "register.html",
            {"request": request, "error": "Ошибка регистрации"}
        )


@router.get("/products")
async def get_product_page(
    request: Request,
    page: int = 1,
    per_page: int = 10,
):
    page = max(1, page)
    per_page = min(max(1, per_page), 50)

    total = await get_products_count()
    pages = max(1, int(ceil(total / per_page)) if per_page else 1)
    page = min(page, pages)

    products = await get_all_products(page=page, per_page=per_page)

    start_page = max(1, page - 2)
    end_page = min(pages, page + 2)
    return templates.TemplateResponse(
        name="products.html",
        context={
            "request": request,
            "products": products,
            "page": page,
            "per_page": per_page,
            "total": total,
            "pages": pages,
            "start_page": start_page,
            "end_page": end_page,
            "has_prev": page > 1,
            "has_next": page < pages,
        },
    )


@router.get("/cart")
async def get_cart_page(request: Request):
    user = await get_current_user(request.cookies)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    cart_items = await get_cart(user["id"])
    total_cart_cost = sum(item.get("total_cost", 0) for item in cart_items)
    return templates.TemplateResponse(
        "cart.html",
        {
            "request": request,
            "cart_items": cart_items,
            "total_cart_cost": total_cart_cost,
        },
    )


@router.get("/product/{product_id}")
async def get_product_detail_page(
    request: Request,
    product_id: int
):
    product = await get_product(product_id)
    reviews = await get_reviews(product_id)
    return templates.TemplateResponse("product_detail.html", {
        "request": request,
        "product": product,
        "reviews": reviews
    })


@router.get("/profile")
async def get_profile(request: Request):
    user = await get_current_user(request.cookies)
    if not user:
        return RedirectResponse(url="/login", status_code=302)

    return templates.TemplateResponse(
        "profile.html",
        {"request": request, "user": user},
    )


@router.get("/tracker-debug", response_class=HTMLResponse)
async def get_tracker_debug_page(request: Request):
    return templates.TemplateResponse("tracker_debug.html", {"request": request})

