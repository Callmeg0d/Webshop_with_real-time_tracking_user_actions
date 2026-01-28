import pytest
from httpx import AsyncClient

from app.models.categories import Categories
from app.repositories.categories_repository import CategoriesRepository


class TestGetAllCategories:
    """Тесты для получения всех категорий"""
    
    @pytest.mark.asyncio
    async def test_get_all_categories_empty(
        self,
        async_client: AsyncClient
    ):
        """Тест получения категорий при пустой БД"""
        response = await async_client.get("/categories/")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_all_categories_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного получения всех категорий"""
        category1 = Categories(name="Category 1", description="Description 1")
        category2 = Categories(name="Category 2", description="Description 2")
        test_db_session.add(category1)
        test_db_session.add(category2)
        await test_db_session.commit()
        
        response = await async_client.get("/categories/")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        names = [cat["name"] for cat in data]
        assert "Category 1" in names
        assert "Category 2" in names


class TestGetCategoryById:
    """Тесты для получения категории по ID"""
    
    @pytest.mark.asyncio
    async def test_get_category_by_id_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного получения категории по ID"""
        category = Categories(name="Test Category", description="Test Description")
        test_db_session.add(category)
        await test_db_session.flush()
        
        response = await async_client.get(f"/categories/{category.id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category.id
        assert data["name"] == "Test Category"
        assert data["description"] == "Test Description"
    
    @pytest.mark.asyncio
    async def test_get_category_by_id_not_found(
        self,
        async_client: AsyncClient
    ):
        """Тест получения несуществующей категории"""
        response = await async_client.get("/categories/99999")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestGetCategoryByName:
    """Тесты для получения категории по названию"""
    
    @pytest.mark.asyncio
    async def test_get_category_by_name_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного получения категории по названию"""
        category = Categories(name="Unique Category", description="Unique Description")
        test_db_session.add(category)
        await test_db_session.commit()
        
        response = await async_client.get("/categories/name/Unique Category")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == category.id
        assert data["name"] == "Unique Category"
        assert data["description"] == "Unique Description"
    
    @pytest.mark.asyncio
    async def test_get_category_by_name_not_found(
        self,
        async_client: AsyncClient
    ):
        """Тест получения несуществующей категории по названию"""
        response = await async_client.get("/categories/name/NonExistent")
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestCreateCategory:
    """Тесты для создания категории"""
    
    @pytest.mark.asyncio
    async def test_create_category_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного создания категории"""
        category_data = {
            "name": "New Category",
            "description": "New Description"
        }
        
        response = await async_client.post("/categories/", json=category_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "New Category"
        assert data["description"] == "New Description"
        
        # Проверяем, что категория создана в БД
        category_repo = CategoriesRepository(test_db_session)
        created_category = await category_repo.get_by_id(data["id"])
        assert created_category is not None
        assert created_category.name == "New Category"
        assert created_category.description == "New Description"
    
    @pytest.mark.asyncio
    async def test_create_category_without_description(
        self,
        async_client: AsyncClient,
    ):
        """Тест создания категории без описания"""
        category_data = {
            "name": "Category Without Description"
        }
        
        response = await async_client.post("/categories/", json=category_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert data["name"] == "Category Without Description"
        assert data["description"] is None
    
    @pytest.mark.asyncio
    async def test_create_category_duplicate_name(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест создания категории с существующим названием"""
        category = Categories(name="Existing Category", description="Description")
        test_db_session.add(category)
        await test_db_session.commit()
        
        # Пытаемся создать вторую с тем же названием
        category_data = {
            "name": "Existing Category",
            "description": "Another Description"
        }
        
        response = await async_client.post("/categories/", json=category_data)
        
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()
