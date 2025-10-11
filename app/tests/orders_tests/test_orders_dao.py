import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.database import async_session_maker
from app.models.products import Products


@pytest.mark.asyncio
async def test_make_order_success(async_client: AsyncClient, auth_headers):
    async with async_session_maker() as session:
        stock_query = select(Products.product_id, Products.product_quantity).where(
            Products.product_id.in_([4, 6, 8])
        )
        stock_result = await session.execute(stock_query)
        initial_stock = {
            row["product_id"]: row["product_quantity"]
            for row in stock_result.mappings().all()}

    response = await async_client.post("/orders/checkout", headers=auth_headers)
    assert response.status_code == 200
    order_data = response.json()

    async with async_session_maker() as session:
        stock_result = await session.execute(stock_query)
        new_stock = {
            row["product_id"]: row["product_quantity"]
            for row in stock_result.mappings().all()}

    for item in order_data["order_items"]:
        product_id = item["product_id"]
        ordered_quantity = item["quantity"]
        assert new_stock[product_id] == initial_stock[product_id] - ordered_quantity
