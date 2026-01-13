from fastapi import APIRouter, Request, Response
import httpx
from app.config import settings
from shared.constants import HttpTimeout

router = APIRouter(prefix="/api", tags=["API Gateway"])


@router.api_route("/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"])
async def proxy_request(service: str, path: str, request: Request):
    """
    Проксирует запросы к микросервисам.
    
    Примеры:
    - /api/user/auth/login -> USER_SERVICE_URL/auth/login
    - /api/product/products -> PRODUCT_SERVICE_URL/products
    - /api/cart/cart -> CART_SERVICE_URL/cart
    """
    service_urls = {
        "user": settings.USER_SERVICE_URL,
        "product": settings.PRODUCT_SERVICE_URL,
        "cart": settings.CART_SERVICE_URL,
        "order": settings.ORDER_SERVICE_URL,
        "review": settings.REVIEW_SERVICE_URL,
        "analytics": settings.ANALYTICS_SERVICE_URL,
    }
    
    if service not in service_urls:
        return Response(status_code=404, content="Service not found")
    
    base_url = service_urls[service]
    target_url = f"{base_url}/{path}"
    
    # Получаем тело запроса
    body = await request.body()
    
    # Получаем заголовки (исключаем host и connection)
    headers = dict(request.headers)
    headers.pop("host", None)
    headers.pop("connection", None)
    
    # Получаем cookies
    cookies = dict(request.cookies)
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.request(
                method=request.method,
                url=target_url,
                headers=headers,
                cookies=cookies,
                content=body if body else None,
                timeout=HttpTimeout.GATEWAY.value,
                follow_redirects=True
            )
            
            # Создаем ответ с теми же заголовками и cookies
            response_headers = dict(response.headers)
            response_headers.pop("content-encoding", None)
            response_headers.pop("transfer-encoding", None)
            
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=response_headers,
                media_type=response.headers.get("content-type")
            )
        except Exception as e:
            return Response(
                status_code=500,
                content=f"Gateway error: {str(e)}"
            )

