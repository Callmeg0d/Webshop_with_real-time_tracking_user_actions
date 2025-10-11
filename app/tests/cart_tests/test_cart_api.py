import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_cart(async_client: AsyncClient, auth_headers):

    response = await async_client.get("/cart", headers=auth_headers)

    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_get_cart_unauthorized(async_client: AsyncClient):

    response = await async_client.get("/cart")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_add_to_cart(async_client: AsyncClient, auth_headers):
    cart_data = {
        "product_id": 5,
        "quantity": 3
    }

    response = await async_client.post("/cart/add", json=cart_data, headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"success": True}


@pytest.mark.asyncio
async def test_remove_from_cart(async_client: AsyncClient, auth_headers):
    product_id = 5

    response = await async_client.delete(f"/cart/remove/{product_id}", headers=auth_headers)

    assert response.status_code == 200
    assert response.json() == {"message": "Товар удален"}


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "product_id, quantity, expected_status, expected_response",
    [
        (4, 3, 200, None),  # Обновление с корректными данными
        (5, 0, 400, {"detail": "Невозможно иметь менее одного товара в корзине"}),  # Попытка установить 0 товаров
        (999, 2, 400, {"detail": "Для увеличения количества товара, он должен находиться в корзине"}),  # Продукт отсутствует
    ]
)
async def test_update_cart_item(async_client: AsyncClient, auth_headers,
                                product_id, quantity, expected_status, expected_response):
    payload = {"quantity": quantity}

    response = await async_client.put(
        f"/cart/update/{product_id}",
        json=payload,
        headers=auth_headers,
    )

    assert response.status_code == expected_status

    if expected_response:
        assert response.json() == expected_response
    else:
        json_response = response.json()
        assert "total_cost" in json_response
        assert "cart_total" in json_response
        assert isinstance(json_response["total_cost"], int)
        assert isinstance(json_response["cart_total"], int)
