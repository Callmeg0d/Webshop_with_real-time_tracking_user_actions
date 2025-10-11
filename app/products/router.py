from fastapi import APIRouter

from app.exceptions import CannotFindProductWithThisId
from app.products.dao import ProductDAO
from app.products.schemas import SProducts

router = APIRouter(
    prefix="/products",
    tags=["Товары"]
)


@router.get("")
async def get_products() -> list[SProducts]:
    return await ProductDAO.find_all()


@router.get("/{product_id}")
async def get_products_by_id(product_id: int) -> SProducts:
    product = await ProductDAO.get_product_by_id(product_id)
    if not product:
        raise CannotFindProductWithThisId
    return product
