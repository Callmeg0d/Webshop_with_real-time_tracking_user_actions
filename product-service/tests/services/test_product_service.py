import pytest

from app.domain.entities.product import ProductItem
from app.exceptions import CannotFindProductWithThisId
from app.services.product_service import ProductService
from app.schemas.products import Pagination, SortEnum


class TestProductServiceGetAllProducts:
    """Юнит-тесты для метода get_all_products ProductService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        """Мок репозитория"""
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        """Мок фабрики UnitOfWork"""
        return mocker.Mock()
    
    @pytest.fixture
    def product_service(self, mock_repository, mock_uow_factory):
        """Создает экземпляр ProductService с моками"""
        return ProductService(
            products_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_all_products_success(
        self,
        product_service: ProductService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения всех товаров"""
        pagination = Pagination(page=1, per_page=10, order=SortEnum.DESC)
        products = [
            ProductItem(
                product_id=1,
                name="Product 1",
                description="Description 1",
                price=1000,
                product_quantity=10,
                image=None,
                features=None,
                category_id=1
            ),
            ProductItem(
                product_id=2,
                name="Product 2",
                description="Description 2",
                price=2000,
                product_quantity=20,
                image="image-2",
                features={"color": "red"},
                category_id=1
            )
        ]
        
        mock_repository.get_all_products = mocker.AsyncMock(return_value=products)
        
        result = await product_service.get_all_products(pagination)
        
        assert len(result) == 2
        assert result[0].product_id == 1
        assert result[0].name == "Product 1"
        assert result[1].product_id == 2
        assert result[1].name == "Product 2"
        
        mock_repository.get_all_products.assert_called_once_with(pagination)
    
    @pytest.mark.asyncio
    async def test_get_all_products_empty(
        self,
        product_service: ProductService,
        mock_repository,
        mocker
    ):
        """Тест получения всех товаров при пустой БД"""
        pagination = Pagination(page=1, per_page=10, order=SortEnum.DESC)
        mock_repository.get_all_products = mocker.AsyncMock(return_value=[])
        
        result = await product_service.get_all_products(pagination)
        
        assert result == []
        mock_repository.get_all_products.assert_called_once_with(pagination)
    
    @pytest.mark.asyncio
    async def test_get_all_products_error(
        self,
        product_service: ProductService,
        mock_repository,
        mocker
    ):
        """Тест обработки ошибки при получении товаров"""
        pagination = Pagination(page=1, per_page=10, order=SortEnum.DESC)
        mock_repository.get_all_products = mocker.AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await product_service.get_all_products(pagination)


class TestProductServiceGetProductById:
    """Юнит-тесты для метода get_product_by_id ProductService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def product_service(self, mock_repository, mock_uow_factory):
        return ProductService(
            products_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_success(
        self,
        product_service: ProductService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения товара по ID"""
        product = ProductItem(
            product_id=1,
            name="Test Product",
            description="Test Description",
            price=1500,
            product_quantity=5,
            image="test-image",
            features={"size": "M"},
            category_id=1
        )
        
        mock_repository.get_product_by_id = mocker.AsyncMock(return_value=product)
        
        result = await product_service.get_product_by_id(1)
        
        assert result.product_id == 1
        assert result.name == "Test Product"
        assert result.price == 1500
        
        mock_repository.get_product_by_id.assert_called_once_with(1)
    
    @pytest.mark.asyncio
    async def test_get_product_by_id_not_found(
        self,
        product_service: ProductService,
        mock_repository,
        mocker
    ):
        """Тест получения несуществующего товара"""
        mock_repository.get_product_by_id = mocker.AsyncMock(return_value=None)
        
        with pytest.raises(CannotFindProductWithThisId):
            await product_service.get_product_by_id(99999)
        
        mock_repository.get_product_by_id.assert_called_once_with(99999)


class TestProductServiceGetStockByIds:
    """Юнит-тесты для метода get_stock_by_ids ProductService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def product_service(self, mock_repository, mock_uow_factory):
        return ProductService(
            products_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_stock_by_ids_success(
        self,
        product_service: ProductService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения остатков батчем"""
        product_ids = [1, 2, 3]
        stock = {1: 10, 2: 20, 3: 30}
        
        mock_repository.get_stock_by_ids = mocker.AsyncMock(return_value=stock)
        
        result = await product_service.get_stock_by_ids(product_ids)
        
        assert result == stock
        assert result[1] == 10
        assert result[2] == 20
        assert result[3] == 30
        
        mock_repository.get_stock_by_ids.assert_called_once_with(product_ids)
    
    @pytest.mark.asyncio
    async def test_get_stock_by_ids_empty(
        self,
        product_service: ProductService,
        mock_repository,
        mocker
    ):
        """Тест получения остатков для пустого списка"""
        mock_repository.get_stock_by_ids = mocker.AsyncMock(return_value={})
        
        result = await product_service.get_stock_by_ids([])
        
        assert result == {}
        mock_repository.get_stock_by_ids.assert_called_once_with([])
    
    @pytest.mark.asyncio
    async def test_get_stock_by_ids_partial(
        self,
        product_service: ProductService,
        mock_repository,
        mocker
    ):
        """Тест получения остатков (некоторые не найдены)"""
        product_ids = [1, 999]
        stock = {1: 10}
        
        mock_repository.get_stock_by_ids = mocker.AsyncMock(return_value=stock)
        
        result = await product_service.get_stock_by_ids(product_ids)
        
        assert len(result) == 1
        assert result[1] == 10
        assert 999 not in result


class TestProductServiceDecreaseStock:
    """Юнит-тесты для метода decrease_stock ProductService"""
    
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
    def product_service(self, mock_repository, mock_uow_factory):
        return ProductService(
            products_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_decrease_stock_success(
        self,
        product_service: ProductService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного уменьшения остатков"""
        product_id = 1
        quantity = 10
        
        mock_repository.decrease_stock = mocker.AsyncMock(return_value=None)
        
        await product_service.decrease_stock(product_id, quantity)
        
        mock_repository.decrease_stock.assert_called_once_with(product_id, quantity)
        mock_uow_factory.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_decrease_stock_error(
        self,
        product_service: ProductService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест обработки ошибки при уменьшении остатков"""
        product_id = 1
        quantity = 10
        
        mock_repository.decrease_stock = mocker.AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await product_service.decrease_stock(product_id, quantity)
        
        mock_uow.__aexit__.assert_called_once()


class TestProductServiceIncreaseStock:
    """Юнит-тесты для метода increase_stock ProductService"""
    
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
    def product_service(self, mock_repository, mock_uow_factory):
        return ProductService(
            products_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_increase_stock_success(
        self,
        product_service: ProductService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного увеличения остатков"""
        product_id = 1
        quantity = 10
        
        mock_repository.increase_stock = mocker.AsyncMock(return_value=None)
        
        await product_service.increase_stock(product_id, quantity)
        
        mock_repository.increase_stock.assert_called_once_with(product_id, quantity)
        mock_uow_factory.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_increase_stock_error(
        self,
        product_service: ProductService,
        mock_repository,
        mock_uow,
        mocker
    ):
        """Тест обработки ошибки при увеличении остатков"""
        product_id = 1
        quantity = 10
        
        mock_repository.increase_stock = mocker.AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await product_service.increase_stock(product_id, quantity)
        
        mock_uow.__aexit__.assert_called_once()
