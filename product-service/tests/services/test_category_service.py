import pytest

from app.domain.entities.categories import CategoryItem
from app.services.category_service import CategoryService


class TestCategoryServiceGetAllCategories:
    """Юнит-тесты для метода get_all_categories CategoryService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        """Мок репозитория"""
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        """Мок фабрики UnitOfWork"""
        return mocker.Mock()
    
    @pytest.fixture
    def category_service(self, mock_repository, mock_uow_factory):
        """Создает экземпляр CategoryService с моками"""
        return CategoryService(
            category_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_all_categories_success(
        self,
        category_service: CategoryService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения всех категорий"""
        categories = [
            CategoryItem(id=1, name="Category 1", description="Description 1"),
            CategoryItem(id=2, name="Category 2", description="Description 2")
        ]
        
        mock_repository.get_all = mocker.AsyncMock(return_value=categories)
        
        result = await category_service.get_all_categories()
        
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].name == "Category 1"
        assert result[1].id == 2
        assert result[1].name == "Category 2"
        
        mock_repository.get_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_categories_empty(
        self,
        category_service: CategoryService,
        mock_repository,
        mocker
    ):
        """Тест получения всех категорий при пустой БД"""
        mock_repository.get_all = mocker.AsyncMock(return_value=[])
        
        result = await category_service.get_all_categories()
        
        assert result == []
        mock_repository.get_all.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_all_categories_error(
        self,
        category_service: CategoryService,
        mock_repository,
        mocker
    ):
        """Тест обработки ошибки при получении категорий"""
        mock_repository.get_all = mocker.AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await category_service.get_all_categories()


class TestCategoryServiceGetCategoryById:
    """Юнит-тесты для метода get_category_by_id CategoryService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def category_service(self, mock_repository, mock_uow_factory):
        return CategoryService(
            category_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_category_by_id_success(
        self,
        category_service: CategoryService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения категории по ID"""
        category = CategoryItem(id=1, name="Test Category", description="Test Description")
        
        mock_repository.get_by_id = mocker.AsyncMock(return_value=category)
        
        result = await category_service.get_category_by_id(1)
        
        assert result is not None
        assert result.id == 1
        assert result.name == "Test Category"
        assert result.description == "Test Description"
        
        mock_repository.get_by_id.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_category_by_id_not_found(
        self,
        category_service: CategoryService,
        mock_repository,
        mocker
    ):
        """Тест получения несуществующей категории"""
        mock_repository.get_by_id = mocker.AsyncMock(return_value=None)
        
        result = await category_service.get_category_by_id(99999)
        
        assert result is None
        mock_repository.get_by_id.assert_called_once_with(99999)


class TestCategoryServiceGetCategoryByName:
    """Юнит-тесты для метода get_category_by_name CategoryService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def category_service(self, mock_repository, mock_uow_factory):
        return CategoryService(
            category_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_category_by_name_success(
        self,
        category_service: CategoryService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения категории по названию"""
        category = CategoryItem(id=1, name="Test Category", description="Test Description")
        
        mock_repository.get_by_name = mocker.AsyncMock(return_value=category)
        
        result = await category_service.get_category_by_name("Test Category")
        
        assert result is not None
        assert result.id == 1
        assert result.name == "Test Category"
        
        mock_repository.get_by_name.assert_called_once_with("Test Category")
    
    @pytest.mark.asyncio
    async def test_get_category_by_name_not_found(
        self,
        category_service: CategoryService,
        mock_repository,
        mocker
    ):
        """Тест получения несуществующей категории по названию"""
        mock_repository.get_by_name = mocker.AsyncMock(return_value=None)
        
        result = await category_service.get_category_by_name("NonExistent")
        
        assert result is None
        mock_repository.get_by_name.assert_called_once_with("NonExistent")


class TestCategoryServiceCreateCategory:
    """Юнит-тесты для метода create_category CategoryService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow(self, mocker):
        uow = mocker.AsyncMock()
        uow.__aenter__ = mocker.AsyncMock(return_value=uow)
        uow.__aexit__ = mocker.AsyncMock(return_value=None)
        return uow
    
    @pytest.fixture
    def mock_uow_factory(self, mock_uow, mocker):
        factory = mocker.Mock()
        factory.create = mocker.Mock(return_value=mock_uow)
        return factory
    
    @pytest.fixture
    def category_service(self, mock_repository, mock_uow_factory):
        return CategoryService(
            category_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_create_category_success(
        self,
        category_service: CategoryService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного создания категории"""
        category_data = CategoryItem(
            id=None,
            name="New Category",
            description="New Description"
        )
        
        created_category = CategoryItem(
            id=1,
            name="New Category",
            description="New Description"
        )
        
        mock_repository.create = mocker.AsyncMock(return_value=created_category)
        
        result = await category_service.create_category(category_data)
        
        assert isinstance(result, CategoryItem)
        assert result.id == 1
        assert result.name == "New Category"
        assert result.description == "New Description"
        
        mock_repository.create.assert_called_once()
        mock_uow_factory.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_category_without_description(
        self,
        category_service: CategoryService,
        mock_repository,
        mocker
    ):
        """Тест создания категории без описания"""
        category_data = CategoryItem(
            id=None,
            name="Category Without Description",
            description=None
        )
        
        created_category = CategoryItem(
            id=1,
            name="Category Without Description",
            description=None
        )
        
        mock_repository.create = mocker.AsyncMock(return_value=created_category)
        
        result = await category_service.create_category(category_data)
        
        assert result.id == 1
        assert result.name == "Category Without Description"
        assert result.description is None
    
    @pytest.mark.asyncio
    async def test_create_category_error(
        self,
        category_service: CategoryService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест обработки ошибки при создании категории"""
        category_data = CategoryItem(
            id=None,
            name="New Category",
            description="New Description"
        )
        
        mock_repository.create = mocker.AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await category_service.create_category(category_data)
        
        mock_uow.__aexit__.assert_called_once()
