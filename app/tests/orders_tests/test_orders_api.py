import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_orders_with_items(async_client: AsyncClient, auth_headers):
    response = await async_client.get("/orders", headers=auth_headers)

    assert response.status_code == 200

    orders = response.json()

    assert isinstance(orders, list)

    for order in orders:
        if "order_items" in order and order["order_items"]:
            for item in order["order_items"]:
                assert "product_image_url" in item
                assert item["product_image_url"].startswith("/static/images/")
                assert item["product_image_url"].endswith(".webp")


@pytest.mark.asyncio
async def test_make_order_success(async_client: AsyncClient, auth_headers):
    response = await async_client.post("orders/checkout", headers=auth_headers)

    assert response.status_code == 200

    order_response = response.json()

    assert isinstance(order_response, dict)
    assert "order_id" in order_response
    assert "status" in order_response
    assert order_response["status"] == "Arriving"
    assert "order_items" in order_response
    assert isinstance(order_response["order_items"], list)
    assert len(order_response["order_items"]) > 0

