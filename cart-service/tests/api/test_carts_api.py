import pytest
from httpx import AsyncClient

from app.models.carts import ShoppingCarts
from app.repositories.carts_repository import CartsRepository


class TestGetCart:
    """Тесты для получения корзины"""
    
    @pytest.mark.asyncio
    async def test_get_cart_success(
        self,
        async_client: AsyncClient,
        test_db_session,
        mocker
    ):
        """Тест успешного получения корзины"""
        user_id = 1
        
        cart_item1 = ShoppingCarts(
            user_id=user_id,
            product_id=1,
            quantity=2,
            total_cost=2000
        )
        cart_item2 = ShoppingCarts(
            user_id=user_id,
            product_id=2,
            quantity=1,
            total_cost=1500
        )
        test_db_session.add(cart_item1)
        test_db_session.add(cart_item2)
        await test_db_session.commit()
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(side_effect=[
                {
                    "name": "Product 1",
                    "description": "Description 1",
                    "price": 1000,
                    "product_quantity": 10
                },
                {
                    "name": "Product 2",
                    "description": "Description 2",
                    "price": 1500,
                    "product_quantity": 5
                }
            ])
        )
        
        response = await async_client.get(
            "/cart/",
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["product_id"] in [1, 2]
        assert data[1]["product_id"] in [1, 2]
    
    @pytest.mark.asyncio
    async def test_get_cart_empty(
        self,
        async_client: AsyncClient
    ):
        """Тест получения пустой корзины"""
        response = await async_client.get(
            "/cart/",
            headers={"X-User-Id": "1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestAddToCart:
    """Тесты для добавления товара в корзину"""
    
    @pytest.mark.asyncio
    async def test_add_to_cart_success(
        self,
        async_client: AsyncClient,
        test_db_session,
        mocker
    ):
        """Тест успешного добавления товара в корзину"""
        user_id = 1
        product_id = 1
        quantity = 2
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(return_value={
                "price": 1000
            })
        )
        
        response = await async_client.post(
            f"/cart/{product_id}",
            params={"quantity": quantity},
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Product added to cart"
        
        # Проверяем, что товар добавлен в БД
        cart_repo = CartsRepository(test_db_session)
        cart_item = await cart_repo.get_cart_item_by_id(user_id, product_id)
        assert cart_item is not None
        assert cart_item.quantity == quantity
        assert cart_item.total_cost == 1000 * quantity
    
    @pytest.mark.asyncio
    async def test_add_to_cart_update_existing(
        self,
        async_client: AsyncClient,
        test_db_session,
        mocker
    ):
        """Тест обновления количества существующего товара"""
        user_id = 1
        product_id = 1
        
        # Создаем существующий товар в корзине
        existing_item = ShoppingCarts(
            user_id=user_id,
            product_id=product_id,
            quantity=2,
            total_cost=2000
        )
        test_db_session.add(existing_item)
        await test_db_session.commit()
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(return_value={
                "price": 1000
            })
        )
        
        response = await async_client.post(
            f"/cart/{product_id}",
            params={"quantity": 3},
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        
        # Проверяем, что количество обновлено
        cart_repo = CartsRepository(test_db_session)
        cart_item = await cart_repo.get_cart_item_by_id(user_id, product_id)
        assert cart_item.quantity == 5
        assert cart_item.total_cost == 5000


class TestRemoveFromCart:
    """Тесты для удаления товара из корзины"""
    
    @pytest.mark.asyncio
    async def test_remove_from_cart_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного удаления товара из корзины"""
        user_id = 1
        product_id = 1
        
        cart_item = ShoppingCarts(
            user_id=user_id,
            product_id=product_id,
            quantity=2,
            total_cost=2000
        )
        test_db_session.add(cart_item)
        await test_db_session.commit()
        
        response = await async_client.delete(
            f"/cart/{product_id}",
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Product removed from cart"
        
        # Проверяем, что товар удален из БД
        cart_repo = CartsRepository(test_db_session)
        cart_item = await cart_repo.get_cart_item_by_id(user_id, product_id)
        assert cart_item is None


class TestUpdateCartItem:
    """Тесты для обновления товара в корзине"""
    
    @pytest.mark.asyncio
    async def test_update_cart_item_success(
        self,
        async_client: AsyncClient,
        test_db_session,
        mocker
    ):
        """Тест успешного обновления товара в корзине"""
        user_id = 1
        product_id = 1
        new_quantity = 5
        
        cart_item = ShoppingCarts(
            user_id=user_id,
            product_id=product_id,
            quantity=2,
            total_cost=2000
        )
        test_db_session.add(cart_item)
        await test_db_session.commit()
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(return_value={
                "price": 1000
            })
        )
        
        response = await async_client.put(
            f"/cart/{product_id}",
            json={"quantity": new_quantity},
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Cart updated"
        assert "total_cost" in data
        assert data["total_cost"] == 5000
        assert "cart_total" in data
    
    @pytest.mark.asyncio
    async def test_update_cart_item_invalid_quantity(
        self,
        async_client: AsyncClient,
    ):
        """Тест обновления товара с невалидным количеством"""
        user_id = 1
        product_id = 1
        
        response = await async_client.put(
            f"/cart/{product_id}",
            json={"quantity": 0},
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_update_cart_item_not_found(
        self,
        async_client: AsyncClient,
        mocker
    ):
        """Тест обновления несуществующего товара"""
        user_id = 1
        product_id = 999
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(return_value={
                "price": 1000
            })
        )
        
        response = await async_client.put(
            f"/cart/{product_id}",
            json={"quantity": 5},
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "detail" in data


class TestClearCart:
    """Тесты для очистки корзины"""
    
    @pytest.mark.asyncio
    async def test_clear_cart_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешной очистки корзины"""
        user_id = 1
        
        cart_item1 = ShoppingCarts(
            user_id=user_id,
            product_id=1,
            quantity=2,
            total_cost=2000
        )
        cart_item2 = ShoppingCarts(
            user_id=user_id,
            product_id=2,
            quantity=1,
            total_cost=1500
        )
        test_db_session.add(cart_item1)
        test_db_session.add(cart_item2)
        await test_db_session.commit()
        
        response = await async_client.delete(
            "/cart/clear",
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Cart cleared"
        
        # Проверяем, что корзина пуста
        cart_repo = CartsRepository(test_db_session)
        cart_items = await cart_repo.get_cart_items(user_id)
        assert len(cart_items) == 0
    
    @pytest.mark.asyncio
    async def test_clear_cart_empty(
        self,
        async_client: AsyncClient
    ):
        """Тест очистки пустой корзины"""
        response = await async_client.delete(
            "/cart/clear",
            headers={"X-User-Id": "1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Cart cleared"
