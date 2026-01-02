from fastapi import APIRouter, Depends, Body
from typing import Annotated

from app.dependencies import get_products_service
from app.schemas.products import SProducts
from app.schemas.stock import StockUpdateRequest
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Товары"]
)


@router.get("/", response_model=list[SProducts])
async def get_products(
        product_service: ProductService = Depends(get_products_service)
):
    return await product_service.get_all_products()


@router.get("/{product_id}", response_model=SProducts)
async def get_product(
        product_id: int,
        product_service: ProductService = Depends(get_products_service)
):
    return await product_service.get_product_by_id(product_id)


@router.post("/stock/batch")
async def get_stock_batch(
        product_ids: Annotated[list[int], Body()],
        product_service: ProductService = Depends(get_products_service)
) -> dict[int, int]:
    """Получает остатки товаров по списку ID (batch endpoint)"""
    return await product_service.get_stock_by_ids(product_ids)


@router.patch("/{product_id}/stock")
async def update_stock(
        product_id: int,
        request: StockUpdateRequest,
        product_service: ProductService = Depends(get_products_service)
):
    """Обновляет остаток товара (уменьшает если quantity отрицательный)"""
    if request.quantity < 0:
        await product_service.decrease_stock(product_id, abs(request.quantity))
    return {"status": "ok"}

