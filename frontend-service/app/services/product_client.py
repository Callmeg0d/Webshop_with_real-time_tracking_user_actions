import httpx
from app.config import settings
from shared.constants import HttpTimeout


async def get_products_count() -> int:
    """Получает общее количество продуктов через product-service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.PRODUCT_SERVICE_URL}/products/count",
            timeout=HttpTimeout.DEFAULT.value,
        )
        response.raise_for_status()
        payload = response.json()
        return int(payload.get("total", 0))


async def get_all_products(
    *,
    page: int = 1,
    per_page: int = 10,
    order: str = "DESC",
) -> list[dict]:
    """Получает продукты через product-service (с пагинацией)"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.PRODUCT_SERVICE_URL}/products/",
            params={"page": page, "per_page": per_page, "order": order},
            timeout=HttpTimeout.DEFAULT.value
        )
        response.raise_for_status()
        products = response.json()
        
        # Получаем категории для всех продуктов
        category_ids = {p.get("category_id") for p in products if p.get("category_id")}
        categories_map = {}
        
        for category_id in category_ids:
            try:
                category_response = await client.get(
                    f"{settings.PRODUCT_SERVICE_URL}/categories/{category_id}",
                    timeout=HttpTimeout.DEFAULT.value
                )
                if category_response.status_code == 200:
                    category = category_response.json()
                    categories_map[category_id] = category.get("name", "")
            except Exception:
                pass
        
        # Добавляем category_name к каждому продукту
        for product in products:
            category_id = product.get("category_id")
            product["category_name"] = categories_map.get(category_id, "")
        
        return products


async def get_product(product_id: int) -> dict:
    """Получает продукт по ID через product-service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}",
            timeout=HttpTimeout.DEFAULT.value
        )
        response.raise_for_status()
        product = response.json()
        
        # Получаем категорию если есть category_id
        if product.get("category_id"):
            try:
                category_response = await client.get(
                    f"{settings.PRODUCT_SERVICE_URL}/categories/{product['category_id']}",
                    timeout=HttpTimeout.DEFAULT.value
                )
                if category_response.status_code == 200:
                    category = category_response.json()
                    product["category_name"] = category.get("name", "")
            except Exception:
                product["category_name"] = ""
        else:
            product["category_name"] = ""
        
        return product

