import httpx
from app.config import settings
from shared.constants import DEFAULT_HTTP_TIMEOUT


async def get_all_products() -> list[dict]:
    """Получает все продукты через product-service"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{settings.PRODUCT_SERVICE_URL}/products/",
            timeout=DEFAULT_HTTP_TIMEOUT
        )
        response.raise_for_status()
        products = response.json()
        
        # Получаем категории для всех продуктов
        category_ids = {p.get("category_id") for p in products if p.get("category_id")}
        categories_map = {}
        
        for category_id in category_ids:
            try:
                category_response = await client.get(
                    f"{settings.PRODUCT_SERVICE_URL}/categories/id/{category_id}",
                    timeout=DEFAULT_HTTP_TIMEOUT
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
            timeout=DEFAULT_HTTP_TIMEOUT
        )
        response.raise_for_status()
        product = response.json()
        
        # Получаем категорию если есть category_id
        if product.get("category_id"):
            try:
                category_response = await client.get(
                    f"{settings.PRODUCT_SERVICE_URL}/categories/id/{product['category_id']}",
                    timeout=DEFAULT_HTTP_TIMEOUT
                )
                if category_response.status_code == 200:
                    category = category_response.json()
                    product["category_name"] = category.get("name", "")
            except Exception:
                product["category_name"] = ""
        else:
            product["category_name"] = ""
        
        return product

