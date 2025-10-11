import pytest
from sqlalchemy import select

from app.database import async_session_maker
from app.products.dao import ProductDAO
from app.shopping_carts.dao import CartsDAO
from app.models.carts import ShoppingCarts


@pytest.mark.parametrize(
    "user_id, product_id, updated_quantity, expected_total_cost",
    [
        (3, 6, 4, 49990 * 4),
        (3, 4, 2, 109990 * 2),
    ]
)
@pytest.mark.asyncio
async def test_update_quantity(user_id, product_id, updated_quantity, expected_total_cost):
    product = await ProductDAO.get_product_by_id(product_id)
    if product is None:
        pytest.fail(f"Продукт с id {product_id} не найден в базе данных")

    result = await CartsDAO.update_quantity(user_id, product_id, updated_quantity)

    assert result[0] == expected_total_cost

    async with async_session_maker() as session:
        query = select(ShoppingCarts).filter(
            ShoppingCarts.user_id == user_id,
            ShoppingCarts.product_id == product_id
        )
        result = await session.execute(query)
        cart_item = result.scalars().first()

        assert cart_item is not None
        assert cart_item.quantity == updated_quantity
        assert cart_item.total_cost == expected_total_cost


@pytest.mark.asyncio
async def test_remove_from_cart():
    user_id = 3
    product_id = 8

    async with async_session_maker() as session:
        query = select(ShoppingCarts).filter(
            ShoppingCarts.user_id == user_id,
            ShoppingCarts.product_id == product_id
        )
        result = await session.execute(query)
        cart_item = result.scalars().first()

        assert cart_item is not None

    result = await CartsDAO.remove_from_cart(user_id, product_id)

    assert result is True

    async with async_session_maker() as session:
        stmt = select(ShoppingCarts).filter(
            ShoppingCarts.user_id == user_id, ShoppingCarts.product_id == product_id
        )
        result = await session.execute(stmt)
        cart_item = result.scalars().first()

        assert cart_item is None

    result = await CartsDAO.remove_from_cart(user_id, product_id)
    assert result is False


@pytest.mark.asyncio
async def test_get_cart_items():
    user_id = 3

    cart_items = await CartsDAO.get_cart_items(user_id)

    assert cart_items

    for item in cart_items:
        assert "product_id" in item
        assert "name" in item
        assert "description" in item
        assert "price" in item
        assert "quantity" in item
        assert "total_cost" in item
        assert "product_quantity" in item

        assert item["quantity"] > 0
        assert item["total_cost"] == item["price"] * item["quantity"]


@pytest.mark.asyncio
async def test_get_cart_items_empty():
    user_id = 52  # У этого пользователя нет товаров в корзине

    cart_items = await CartsDAO.get_cart_items(user_id)

    assert cart_items == []


@pytest.mark.asyncio
async def test_add_to_cart():
    user_id = 3
    product_id = 5
    quantity = 3

    product = await ProductDAO.get_product_by_id(product_id)
    assert product is not None

    await CartsDAO.add_to_cart(product_id, user_id, quantity)

    async with async_session_maker() as session:
        query = select(ShoppingCarts).where(
            ShoppingCarts.user_id == user_id, ShoppingCarts.product_id == product_id
        )
        result = await session.execute(query)
        cart_item = result.scalars().first()

        assert cart_item is not None
        assert cart_item.quantity == quantity
        assert cart_item.total_cost == cart_item.quantity * product.price


@pytest.mark.asyncio
async def test_update_existing_product_in_cart():
    user_id = 3
    product_id = 7
    initial_quantity = 1
    additional_quantity = 1

    product = await ProductDAO.get_product_by_id(product_id)
    initial_total_cost = product.price * initial_quantity

    # Добавляем товар в корзину первый раз
    await CartsDAO.add_to_cart(product_id, user_id, initial_quantity)

    # Добавляем тот же товар еще раз
    await CartsDAO.add_to_cart(product_id, user_id, additional_quantity)

    async with async_session_maker() as session:
        stmt = select(ShoppingCarts).where(
            ShoppingCarts.user_id == user_id, ShoppingCarts.product_id == product_id
        )
        result = await session.execute(stmt)
        cart_item = result.scalars().first()

        assert cart_item.quantity == initial_quantity + additional_quantity
        assert cart_item.total_cost == (
                initial_total_cost + product.price * additional_quantity
        )


@pytest.mark.asyncio
async def test_add_non_existing_product():
    user_id = 3
    product_id = 999  # Несуществующий товар
    quantity = 2

    with pytest.raises(Exception):
        await CartsDAO.add_to_cart(product_id, user_id, quantity)
