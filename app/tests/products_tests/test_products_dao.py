import ast

import pytest
from httpx import AsyncClient

from app.products.dao import ProductDAO


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "product_id, expected_product",
    [
        (1, {"product_id": 1, "name": "iPhone 13",
             "description": "Новый смартфон от Apple с A15 Bionic и 128 ГБ памяти.", "price": 79990,
             "product_quantity": 3, "image": 1,
             "features": {'Вес': '173 г', 'Память': '128 ГБ', 'Размеры': '146.7 x 71.5 x 7.65 мм'},
             "category_name": "Телефоны"}),
        (999, None),
    ],
)
async def test_get_product_by_id(product_id, expected_product, async_client: AsyncClient):
    product_data = await ProductDAO.get_product_by_id(product_id)

    if expected_product:
        assert product_data is not None
        for key, value in expected_product.items():
            if key == "features":
                product_features = product_data[key]

                if isinstance(product_features, str):
                    try:
                        product_features = ast.literal_eval(product_features)  # преобразование строки в словарь
                    except (SyntaxError, ValueError):
                        assert False

                assert isinstance(product_features, dict)
                assert sorted(product_features.items()) == sorted(value.items())
            else:
                assert product_data[key] == value
