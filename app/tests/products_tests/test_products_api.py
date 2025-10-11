import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "product_id, expected_status, expected_response",
    [
        (1, 200, {"product_id": 1, "name": "iPhone 13",
                  "description": "Новый смартфон от Apple с A15 Bionic и 128 ГБ памяти.",
                  "price": 79990, "product_quantity": 3, "image": 1,
                  "features": {'Память': '128 ГБ', 'Вес': '173 г', 'Размеры': '146.7 x 71.5 x 7.65 мм'},
                  "category_name": "Телефоны"}),
        (999, 404, {"detail": "Товара с таким id не существует"}),
    ],
)
async def test_get_product_by_id_endpoint(async_client: AsyncClient, product_id, expected_status, expected_response):
    response = await async_client.get(f"/products/{product_id}")
    assert response.status_code == expected_status
    assert response.json() == expected_response
