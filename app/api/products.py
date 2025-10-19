from typing import List
from fastapi import APIRouter, Depends

from app.dependencies import get_products_service
from app.schemas.products import SProducts
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Товары"]
)


@router.get("/", response_model=List[SProducts])
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

