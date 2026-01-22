import pytest
from httpx import AsyncClient

from app.models.products import Products
from app.models.categories import Categories
from app.repositories.products_repository import ProductsRepository


class TestGetProducts:
    """Тесты для получения всех товаров"""
    
    @pytest.mark.asyncio
    async def test_get_products_empty(
        self,
        async_client: AsyncClient,
    ):
        """Тест получения товаров при пустой БД"""
        response = await async_client.get("/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_products_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного получения товаров"""
        category = Categories(name="Test Category", description="Test Description")
        test_db_session.add(category)
        await test_db_session.flush()

        product1 = Products(
            product_id=1,
            name="Product 1",
            description="Description 1",
            price=1000,
            product_quantity=10,
            image=None,
            features=None,
            category_id=category.id
        )
        product2 = Products(
            product_id=2,
            name="Product 2",
            description="Description 2",
            price=2000,
            product_quantity=20,
            image=None,
            features={"color": "red"},
            category_id=category.id
        )
        test_db_session.add(product1)
        test_db_session.add(product2)
        await test_db_session.commit()
        
        response = await async_client.get("/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] in ["Product 1", "Product 2"]
        assert data[1]["name"] in ["Product 1", "Product 2"]


class TestGetProduct:
    """Тесты для получения товара по ID"""
    
    @pytest.mark.asyncio
    async def test_get_product_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного получения товара"""
        category = Categories(name="Test Category", description="Test Description")
        test_db_session.add(category)
        await test_db_session.flush()

        product = Products(
            product_id=1,
            name="Test Product",
            description="Test Description",
            price=1500,
            product_quantity=5,
            image=123,
            features={"size": "M", "color": "blue"},
            category_id=category.id
        )
        test_db_session.add(product)
        await test_db_session.commit()
        
        response = await async_client.get("/products/1")
        
        assert response.status_code == 200
        data = response.json()
        assert data["product_id"] == 1
        assert data["name"] == "Test Product"
        assert data["description"] == "Test Description"
        assert data["price"] == 1500
        assert data["product_quantity"] == 5
        assert data["image"] == 123
        assert data["features"] == {"size": "M", "color": "blue"}
        assert data["category_id"] == category.id
    
    @pytest.mark.asyncio
    async def test_get_product_not_found(
        self,
        async_client: AsyncClient
    ):
        """Тест получения несуществующего товара"""
        response = await async_client.get("/products/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestGetStockBatch:
    """Тесты для batch получения остатков"""
    
    @pytest.mark.asyncio
    async def test_get_stock_batch_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного получения остатков батчем"""
        category = Categories(name="Test Category", description="Test Description")
        test_db_session.add(category)
        await test_db_session.flush()

        product1 = Products(
            product_id=1,
            name="Product 1",
            description="Description 1",
            price=1000,
            product_quantity=10,
            image=None,
            features=None,
            category_id=category.id
        )
        product2 = Products(
            product_id=2,
            name="Product 2",
            description="Description 2",
            price=2000,
            product_quantity=20,
            image=None,
            features=None,
            category_id=category.id
        )
        product3 = Products(
            product_id=3,
            name="Product 3",
            description="Description 3",
            price=3000,
            product_quantity=30,
            image=None,
            features=None,
            category_id=category.id
        )
        test_db_session.add(product1)
        test_db_session.add(product2)
        test_db_session.add(product3)
        await test_db_session.commit()
        
        response = await async_client.post(
            "/products/stock/batch",
            json=[1, 2, 3]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert data["1"] == 10
        assert data["2"] == 20
        assert data["3"] == 30
    
    @pytest.mark.asyncio
    async def test_get_stock_batch_partial(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест получения остатков батчем (некоторые не найдены)"""
        category = Categories(name="Test Category", description="Test Description")
        test_db_session.add(category)
        await test_db_session.flush()

        product = Products(
            product_id=1,
            name="Product 1",
            description="Description 1",
            price=1000,
            product_quantity=10,
            image=None,
            features=None,
            category_id=category.id
        )
        test_db_session.add(product)
        await test_db_session.commit()
        
        response = await async_client.post(
            "/products/stock/batch",
            json=[1, 99999]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 1
        assert data["1"] == 10
        assert "99999" not in data
    
    @pytest.mark.asyncio
    async def test_get_stock_batch_empty(
        self,
        async_client: AsyncClient
    ):
        """Тест получения остатков батчем при пустом списке"""
        response = await async_client.post(
            "/products/stock/batch",
            json=[]
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 0


class TestUpdateStock:
    """Тесты для обновления остатков"""
    
    @pytest.mark.asyncio
    async def test_update_stock_decrease_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного уменьшения остатков"""
        category = Categories(name="Test Category", description="Test Description")
        test_db_session.add(category)
        await test_db_session.flush()

        product = Products(
            product_id=1,
            name="Test Product",
            description="Test Description",
            price=1000,
            product_quantity=100,
            image=None,
            features=None,
            category_id=category.id
        )
        test_db_session.add(product)
        await test_db_session.commit()
        
        # Уменьшаем остаток
        response = await async_client.patch(
            "/products/1/stock",
            json={"quantity": -30}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        
        # Проверяем, что остаток уменьшился
        product_repo = ProductsRepository(test_db_session)
        quantity = await product_repo.get_quantity(1)
        assert quantity == 70
