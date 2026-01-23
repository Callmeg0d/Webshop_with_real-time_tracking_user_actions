import pytest

from app.domain.entities.cart import CartItem
from app.services.cart_service import CartService
from app.schemas.carts import SCartItem, SCartItemWithProduct
from app.exceptions import CannotHaveLessThan1Product, NeedToHaveAProductToIncreaseItsQuantity


class TestCartServiceGetUserCart:
    """Тесты для метода get_user_cart CartService"""
    
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
    def cart_service(self, mock_repository, mock_uow_factory):
        return CartService(
            carts_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_user_cart_success(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения корзины пользователя"""
        user_id = 1
        
        cart_items = [
            SCartItem(product_id=1, quantity=2, total_cost=2000),
            SCartItem(product_id=2, quantity=1, total_cost=1500)
        ]
        
        mock_repository.get_cart_items = mocker.AsyncMock(return_value=cart_items)
        
        result = await cart_service.get_user_cart(user_id)
        
        assert len(result) == 2
        assert result[0].product_id in [1, 2]
        assert result[1].product_id in [1, 2]
        mock_repository.get_cart_items.assert_called_once_with(user_id=user_id)
    
    @pytest.mark.asyncio
    async def test_get_user_cart_empty(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест получения пустой корзины"""
        user_id = 1
        
        mock_repository.get_cart_items = mocker.AsyncMock(return_value=[])
        
        result = await cart_service.get_user_cart(user_id)
        
        assert result == []
        mock_repository.get_cart_items.assert_called_once_with(user_id=user_id)


class TestCartServiceAddToCart:
    """Тесты для метода add_to_cart CartService"""
    
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
    def cart_service(self, mock_repository, mock_uow_factory):
        return CartService(
            carts_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_add_to_cart_new_item(
        self,
        cart_service: CartService,
        mock_repository,
        mock_uow_factory,
        mocker
    ):
        """Тест добавления нового товара в корзину"""
        user_id = 1
        product_id = 1
        quantity = 2
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(return_value={"price": 1000})
        )
        mock_repository.get_cart_item_by_id = mocker.AsyncMock(return_value=None)
        mock_repository.add_cart_item = mocker.AsyncMock(return_value=None)
        
        await cart_service.add_to_cart(user_id, product_id, quantity)
        
        mock_repository.add_cart_item.assert_called_once_with(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            total_cost=2000
        )
        mock_uow_factory.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_add_to_cart_update_existing(
        self,
        cart_service: CartService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест обновления существующего товара в корзине"""
        user_id = 1
        product_id = 1
        quantity = 3
        
        existing_item = CartItem(
            cart_id=1,
            user_id=user_id,
            product_id=product_id,
            quantity=2,
            total_cost=2000
        )
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(return_value={"price": 1000})
        )
        mock_repository.get_cart_item_by_id = mocker.AsyncMock(return_value=existing_item)
        mock_repository.update_cart_item = mocker.AsyncMock(return_value=None)
        
        await cart_service.add_to_cart(user_id, product_id, quantity)
        
        mock_repository.update_cart_item.assert_called_once_with(
            user_id=user_id,
            product_id=product_id,
            quantity_add=quantity,
            cost_add=3000
        )
        mock_uow_factory.create.assert_called_once()


class TestCartServiceRemoveCartItem:
    """Тесты для метода remove_cart_item CartService"""
    
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
    def cart_service(self, mock_repository, mock_uow_factory):
        return CartService(
            carts_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_remove_cart_item_success(
        self,
        cart_service: CartService,
        mock_repository,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного удаления товара из корзины"""
        user_id = 1
        product_id = 1
        
        mock_repository.remove_cart_item = mocker.AsyncMock(return_value=None)
        
        await cart_service.remove_cart_item(user_id, product_id)
        
        mock_repository.remove_cart_item.assert_called_once_with(
            user_id=user_id,
            product_id=product_id
        )
        mock_uow_factory.create.assert_called_once()


class TestCartServiceClearUserCart:
    """Тесты для метода clear_user_cart CartService"""
    
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
    def cart_service(self, mock_repository, mock_uow_factory):
        return CartService(
            carts_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_clear_user_cart_success(
        self,
        cart_service: CartService,
        mock_repository,
        mock_uow_factory,
        mocker
    ):
        """Тест успешной очистки корзины"""
        user_id = 1
        
        mock_repository.clear_cart = mocker.AsyncMock(return_value=None)
        
        await cart_service.clear_user_cart(user_id)
        
        mock_repository.clear_cart.assert_called_once_with(user_id=user_id)
        mock_uow_factory.create.assert_called_once()


class TestCartServiceGetTotalCost:
    """Тесты для метода get_total_cost CartService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def cart_service(self, mock_repository, mock_uow_factory):
        return CartService(
            carts_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_total_cost_success(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения общей стоимости"""
        user_id = 1
        total_cost = 3500
        
        mock_repository.get_total_cost = mocker.AsyncMock(return_value=total_cost)
        
        result = await cart_service.get_total_cost(user_id)
        
        assert result == total_cost
        mock_repository.get_total_cost.assert_called_once_with(user_id=user_id)
    
    @pytest.mark.asyncio
    async def test_get_total_cost_zero(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест получения нулевой стоимости для пустой корзины"""
        user_id = 1
        
        mock_repository.get_total_cost = mocker.AsyncMock(return_value=0)
        
        result = await cart_service.get_total_cost(user_id)
        
        assert result == 0


class TestCartServiceGetCartItemsWithProducts:
    """Тесты для метода get_cart_items_with_products CartService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def cart_service(self, mock_repository, mock_uow_factory):
        return CartService(
            carts_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_cart_items_with_products_success(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения товаров с информацией о продуктах"""
        user_id = 1
        
        cart_items = [
            SCartItem(product_id=1, quantity=2, total_cost=2000),
            SCartItem(product_id=2, quantity=1, total_cost=1500)
        ]
        
        mock_repository.get_cart_items = mocker.AsyncMock(return_value=cart_items)
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
        
        result = await cart_service.get_cart_items_with_products(user_id)
        
        assert len(result) == 2
        assert result[0].product_id in [1, 2]
        assert result[1].product_id in [1, 2]
        assert all(isinstance(item, SCartItemWithProduct) for item in result)
    
    @pytest.mark.asyncio
    async def test_get_cart_items_with_products_empty(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест получения товаров для пустой корзины"""
        user_id = 1
        
        mock_repository.get_cart_items = mocker.AsyncMock(return_value=[])
        
        result = await cart_service.get_cart_items_with_products(user_id)
        
        assert result == []
    
    @pytest.mark.asyncio
    async def test_get_cart_items_with_products_skip_not_found(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест пропуска товаров, которые не найдены в product-service"""
        user_id = 1
        
        cart_items = [
            SCartItem(product_id=1, quantity=2, total_cost=2000),
            SCartItem(product_id=999, quantity=1, total_cost=1500)  # Несуществующий товар
        ]
        
        mock_repository.get_cart_items = mocker.AsyncMock(return_value=cart_items)
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(side_effect=[
                {
                    "name": "Product 1",
                    "description": "Description 1",
                    "price": 1000,
                    "product_quantity": 10
                },
                Exception("Product not found")  # Исключение для несуществующего товара
            ])
        )
        
        result = await cart_service.get_cart_items_with_products(user_id)
        
        # Должен вернуться только один товар (несуществующий пропущен)
        assert len(result) == 1
        assert result[0].product_id == 1


class TestCartServiceUpdateQuantity:
    """Тесты для метода update_quantity CartService"""
    
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
    def cart_service(self, mock_repository, mock_uow_factory):
        return CartService(
            carts_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_update_quantity_success(
        self,
        cart_service: CartService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного обновления количества"""
        user_id = 1
        product_id = 1
        quantity = 5
        
        existing_item = CartItem(
            cart_id=1,
            user_id=user_id,
            product_id=product_id,
            quantity=2,
            total_cost=2000
        )
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(return_value={"price": 1000})
        )
        mock_repository.get_cart_item_by_id = mocker.AsyncMock(return_value=existing_item)
        mock_repository.update_quantity = mocker.AsyncMock(return_value=5000)
        
        result = await cart_service.update_quantity(user_id, product_id, quantity)
        
        assert result == 5000
        mock_repository.update_quantity.assert_called_once_with(
            user_id=user_id,
            product_id=product_id,
            quantity=quantity,
            price=1000
        )
        mock_uow_factory.create.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_update_quantity_invalid(
        self,
        cart_service: CartService,
    ):
        """Тест обновления количества с невалидным значением"""
        user_id = 1
        product_id = 1
        quantity = 0
        
        with pytest.raises(CannotHaveLessThan1Product):
            await cart_service.update_quantity(user_id, product_id, quantity)
    
    @pytest.mark.asyncio
    async def test_update_quantity_item_not_found(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест обновления количества несуществующего товара"""
        user_id = 1
        product_id = 999
        quantity = 5
        
        mocker.patch(
            'app.services.cart_service.get_product',
            new=mocker.AsyncMock(return_value={"price": 1000})
        )
        mock_repository.get_cart_item_by_id = mocker.AsyncMock(return_value=None)
        
        with pytest.raises(NeedToHaveAProductToIncreaseItsQuantity):
            await cart_service.update_quantity(user_id, product_id, quantity)


class TestCartServiceGetCartItemById:
    """Тесты для метода get_cart_item_by_id CartService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def cart_service(self, mock_repository, mock_uow_factory):
        return CartService(
            carts_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_cart_item_by_id_success(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения товара по ID"""
        user_id = 1
        product_id = 1
        
        cart_item = CartItem(
            cart_id=1,
            user_id=user_id,
            product_id=product_id,
            quantity=2,
            total_cost=2000
        )
        
        mock_repository.get_cart_item_by_id = mocker.AsyncMock(return_value=cart_item)
        
        result = await cart_service.get_cart_item_by_id(user_id, product_id)
        
        assert result == cart_item
        mock_repository.get_cart_item_by_id.assert_called_once_with(
            user_id=user_id,
            product_id=product_id
        )
    
    @pytest.mark.asyncio
    async def test_get_cart_item_by_id_not_found(
        self,
        cart_service: CartService,
        mock_repository,
        mocker
    ):
        """Тест получения несуществующего товара"""
        user_id = 1
        product_id = 999
        
        mock_repository.get_cart_item_by_id = mocker.AsyncMock(return_value=None)
        
        result = await cart_service.get_cart_item_by_id(user_id, product_id)
        
        assert result is None
