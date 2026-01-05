from fastapi import APIRouter, Depends, Body
from typing import Annotated
from shared import get_logger

from app.dependencies import get_products_service
from app.schemas.products import SProducts
from app.schemas.stock import StockUpdateRequest
from app.services.product_service import ProductService

router = APIRouter(
    prefix="/products",
    tags=["Товары"]
)

logger = get_logger(__name__)


@router.get("/", response_model=list[SProducts])
async def get_products(
        product_service: ProductService = Depends(get_products_service)
):
    logger.info("GET /products/ request")
    try:
        products = await product_service.get_all_products()
        logger.info(f"Returned {len(products)} products")
        return products
    except Exception as e:
        logger.error(f"Error fetching products by API: {e}", exc_info=True)
        raise


@router.get("/{product_id}", response_model=SProducts)
async def get_product(
        product_id: int,
        product_service: ProductService = Depends(get_products_service)
):
    logger.info(f"GET /products/{product_id} request")
    try:
        product = await product_service.get_product_by_id(product_id)
        logger.info(f"Product {product_id} returned successfully")
        return product
    except Exception as e:
        logger.error(f"Error fetching product {product_id} by API: {e}", exc_info=True)
        raise


@router.post("/stock/batch")
async def get_stock_batch(
        product_ids: Annotated[list[int], Body()],
        product_service: ProductService = Depends(get_products_service)
) -> dict[int, int]:
    """Получает остатки товаров по списку ID (batch endpoint)"""
    logger.info(f"POST /products/stock/batch request for {len(product_ids)} products")
    try:
        stock = await product_service.get_stock_by_ids(product_ids)
        logger.info(f"Stock returned for {len(stock)} products")
        return stock
    except Exception as e:
        logger.error(f"Error fetching stock batch by API: {e}", exc_info=True)
        raise


@router.patch("/{product_id}/stock")
async def update_stock(
        product_id: int,
        request: StockUpdateRequest,
        product_service: ProductService = Depends(get_products_service)
):
    """Обновляет остаток товара (уменьшает если quantity отрицательный)"""
    logger.info(f"PATCH /products/{product_id}/stock request, quantity: {request.quantity}")
    try:
        if request.quantity < 0:
            await product_service.decrease_stock(product_id, abs(request.quantity))
            logger.info(f"Stock updated successfully for product {product_id}")
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error updating stock for product {product_id} by API: {e}", exc_info=True)
        raise

