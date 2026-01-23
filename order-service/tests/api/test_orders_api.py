import pytest
from httpx import AsyncClient
from datetime import date

from app.models.orders import Orders
from app.repositories.orders_repository import OrdersRepository
from app.constants import ORDER_STATUS_PENDING, ORDER_STATUS_CONFIRMED


class TestCreateOrder:
    """Тесты для создания заказа"""
    
    @pytest.mark.asyncio
    async def test_create_order_success(
        self,
        async_client: AsyncClient,
        test_db_session,
        mocker
    ):
        """Тест успешного создания заказа"""
        user_id = 1
        
        mocker.patch(
            'app.services.order_service.get_cart_items',
            new=mocker.AsyncMock(return_value=[
                {"product_id": 1, "quantity": 2, "total_cost": 2000},
                {"product_id": 2, "quantity": 1, "total_cost": 1500}
            ])
        )
        mocker.patch(
            'app.services.order_service.get_cart_total',
            new=mocker.AsyncMock(return_value=3500)
        )
        mocker.patch(
            'app.services.order_service.get_user_delivery_address',
            new=mocker.AsyncMock(return_value="Test Address")
        )
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value="Test Address")
        )
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={1: 10, 2: 5})
        )
        mocker.patch(
            'app.services.order_validator.get_user_balance',
            new=mocker.AsyncMock(return_value=5000)
        )
        mocker.patch(
            'app.services.order_service.publish_order_processing_started',
            new=mocker.AsyncMock(return_value=None)
        )
        
        response = await async_client.post(
            "/orders/",
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert data["message"] == "Order created successfully"
        assert "order_id" in data
        assert "total_cost" in data
        assert data["total_cost"] == 3500
        
        # Проверяем, что заказ создан в БД
        order_repo = OrdersRepository(test_db_session)
        order = await order_repo.get_order_by_id(data["order_id"])
        assert order is not None
        assert order.user_id == user_id
        assert order.total_cost == 3500
        assert order.status == ORDER_STATUS_PENDING
    


class TestGetUserOrders:
    """Тесты для получения заказов пользователя"""
    
    @pytest.mark.asyncio
    async def test_get_user_orders_success(
        self,
        async_client: AsyncClient,
        test_db_session,
        mocker
    ):
        """Тест успешного получения заказов пользователя"""
        user_id = 1
        
        order1 = Orders(
            user_id=user_id,
            created_at=date.today(),
            status=ORDER_STATUS_CONFIRMED,
            delivery_address="Address 1",
            order_items=[{"product_id": 1, "quantity": 2}],
            total_cost=2000
        )
        order2 = Orders(
            user_id=user_id,
            created_at=date.today(),
            status=ORDER_STATUS_PENDING,
            delivery_address="Address 2",
            order_items=[{"product_id": 2, "quantity": 1}],
            total_cost=1500
        )
        test_db_session.add(order1)
        test_db_session.add(order2)
        await test_db_session.commit()
        
        mocker.patch(
            'app.services.order_service.get_product',
            new=mocker.AsyncMock(return_value={"image": 123})
        )
        
        response = await async_client.get(
            "/orders/",
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["total_cost"] in [2000, 1500]
        assert data[1]["total_cost"] in [2000, 1500]
    
    @pytest.mark.asyncio
    async def test_get_user_orders_empty(
        self,
        async_client: AsyncClient
    ):
        """Тест получения заказов при пустой БД"""
        response = await async_client.get(
            "/orders/",
            headers={"X-User-Id": "1"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_user_orders_different_user(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест получения заказов другого пользователя"""
        user_id = 1
        other_user_id = 2
        
        order = Orders(
            user_id=other_user_id,
            created_at=date.today(),
            status=ORDER_STATUS_CONFIRMED,
            delivery_address="Address",
            order_items=[{"product_id": 1, "quantity": 1}],
            total_cost=1000
        )
        test_db_session.add(order)
        await test_db_session.commit()
        
        response = await async_client.get(
            "/orders/",
            headers={"X-User-Id": str(user_id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 0
