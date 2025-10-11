import json
from datetime import datetime

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import insert

from app.models.categories import Categories
from app.config import settings
from app.database import Base, async_session_maker, engine
from app.main import app as fastapi_app
from app.models.orders import Orders
from app.models.products import Products
from app.models.reviews import Reviews
from app.models.carts import ShoppingCarts
from app.models.users import Users


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():
    assert settings.MODE == "TEST"

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_test_file(model: str):
        with open(f"app/tests/mock_{model}.json", encoding="utf-8") as file:
            return json.load(file)

    users = open_test_file("users")
    categories = open_test_file("categories")
    products = open_test_file("products")
    shopping_carts = open_test_file("shopping_carts")
    orders = open_test_file("orders")
    reviews = open_test_file("reviews")

    for order in orders:
        # Алхимия не принимает дату в текстовом формате, поэтому форматируем к datetime
        order["created_at"] = datetime.strptime(order["created_at"], "%Y-%m-%d")

    async with async_session_maker() as session:
        for Model, values in [
            (Users, users),
            (Categories, categories),
            (Products, products),
            (ShoppingCarts, shopping_carts),
            (Orders, orders),
            (Reviews, reviews)
        ]:
            query = insert(Model).values(values)
            await session.execute(query)

        await session.commit()


@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(transport=ASGITransport(fastapi_app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def authenticated_user(async_client: AsyncClient):
    login_data = {"email": "test2@test2.com", "password": "test2"}

    response = await async_client.post("/auth/login", json=login_data)
    assert response.status_code == 200

    tokens = response.json()
    return {"access_token": tokens["access_token"]}


@pytest.fixture
def auth_headers(authenticated_user):
    """Фикстура для заголовков авторизации"""
    return {"Authorization": f"Bearer {authenticated_user['access_token']}"}
