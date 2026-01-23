import pytest

from app.services.order_validator import OrderValidator
from app.schemas.orders import SCartItemForOrder
from app.exceptions import (
    CannotMakeOrderWithoutAddress,
    CannotMakeOrderWithoutItems,
    NotEnoughProductsInStock,
    UserIsNotPresentException,
    NotEnoughBalanceToMakeOrder
)


class TestOrderValidatorValidateOrder:
    """Тесты для метода validate_order OrderValidator"""
    
    @pytest.fixture
    def validator(self):
        return OrderValidator()
    
    @pytest.mark.asyncio
    async def test_validate_order_success(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест успешной валидации заказа"""
        user_id = 1
        cart_items = [
            SCartItemForOrder(product_id=1, quantity=2),
            SCartItemForOrder(product_id=2, quantity=1)
        ]
        total_cost = 3500
        
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
        
        # Не должно быть исключений
        await validator.validate_order(user_id, cart_items, total_cost)
    
    @pytest.mark.asyncio
    async def test_validate_order_no_address(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест валидации заказа без адреса"""
        user_id = 1
        cart_items = [SCartItemForOrder(product_id=1, quantity=1)]
        total_cost = 1000
        
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value=None)
        )
        
        with pytest.raises(CannotMakeOrderWithoutAddress):
            await validator.validate_order(user_id, cart_items, total_cost)
    
    @pytest.mark.asyncio
    async def test_validate_order_empty_cart(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест валидации заказа с пустой корзиной"""
        user_id = 1
        cart_items = []
        total_cost = 0
        
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value="Test Address")
        )
        
        with pytest.raises(CannotMakeOrderWithoutItems):
            await validator.validate_order(user_id, cart_items, total_cost)
    
    @pytest.mark.asyncio
    async def test_validate_order_insufficient_stock(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест валидации заказа при недостатке товара на складе"""
        user_id = 1
        cart_items = [
            SCartItemForOrder(product_id=1, quantity=10)
        ]
        total_cost = 5000
        
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value="Test Address")
        )
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={1: 5})  # Доступно только 5, запрашивается 10
        )
        
        with pytest.raises(NotEnoughProductsInStock):
            await validator.validate_order(user_id, cart_items, total_cost)
    
    @pytest.mark.asyncio
    async def test_validate_order_user_not_found(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест валидации заказа при отсутствии пользователя"""
        user_id = 1
        cart_items = [SCartItemForOrder(product_id=1, quantity=1)]
        total_cost = 1000
        
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value="Test Address")
        )
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={1: 10})
        )
        mocker.patch(
            'app.services.order_validator.get_user_balance',
            new=mocker.AsyncMock(return_value=None)  # Пользователь не найден
        )
        
        with pytest.raises(UserIsNotPresentException):
            await validator.validate_order(user_id, cart_items, total_cost)
    
    @pytest.mark.asyncio
    async def test_validate_order_insufficient_balance(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест валидации заказа при недостатке баланса"""
        user_id = 1
        cart_items = [SCartItemForOrder(product_id=1, quantity=1)]
        total_cost = 5000
        
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value="Test Address")
        )
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={1: 10})
        )
        mocker.patch(
            'app.services.order_validator.get_user_balance',
            new=mocker.AsyncMock(return_value=3000)  # Баланс меньше стоимости
        )
        
        with pytest.raises(NotEnoughBalanceToMakeOrder):
            await validator.validate_order(user_id, cart_items, total_cost)


class TestOrderValidatorValidateAddress:
    """Тесты для метода _validate_address OrderValidator"""
    
    @pytest.fixture
    def validator(self):
        return OrderValidator()
    
    @pytest.mark.asyncio
    async def test_validate_address_success(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест успешной проверки адреса"""
        user_id = 1
        
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value="Test Address")
        )
        
        # Не должно быть исключений
        await validator._validate_address(user_id)
    
    @pytest.mark.asyncio
    async def test_validate_address_empty(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки адреса при его отсутствии"""
        user_id = 1
        
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value="")
        )
        
        with pytest.raises(CannotMakeOrderWithoutAddress):
            await validator._validate_address(user_id)
    
    @pytest.mark.asyncio
    async def test_validate_address_none(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки адреса при None"""
        user_id = 1
        
        mocker.patch(
            'app.services.order_validator.get_user_delivery_address',
            new=mocker.AsyncMock(return_value=None)
        )
        
        with pytest.raises(CannotMakeOrderWithoutAddress):
            await validator._validate_address(user_id)


class TestOrderValidatorValidateCart:
    """Тесты для метода _validate_cart_not_empty OrderValidator"""
    
    @pytest.fixture
    def validator(self):
        return OrderValidator()
    
    @pytest.mark.asyncio
    async def test_validate_cart_not_empty_success(
        self,
        validator: OrderValidator
    ):
        """Тест успешной проверки корзины"""
        cart_items = [
            SCartItemForOrder(product_id=1, quantity=1)
        ]
        
        # Не должно быть исключений
        await validator._validate_cart_not_empty(cart_items)
    
    @pytest.mark.asyncio
    async def test_validate_cart_empty(
        self,
        validator: OrderValidator
    ):
        """Тест проверки пустой корзины"""
        cart_items = []
        
        with pytest.raises(CannotMakeOrderWithoutItems):
            await validator._validate_cart_not_empty(cart_items)


class TestOrderValidatorValidateStock:
    """Тесты для метода _validate_stock OrderValidator"""
    
    @pytest.fixture
    def validator(self):
        return OrderValidator()
    
    @pytest.mark.asyncio
    async def test_validate_stock_success(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест успешной проверки остатков"""
        cart_items = [
            SCartItemForOrder(product_id=1, quantity=5),
            SCartItemForOrder(product_id=2, quantity=3)
        ]
        
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={1: 10, 2: 5})
        )
        
        # Не должно быть исключений
        await validator._validate_stock(cart_items)
    
    @pytest.mark.asyncio
    async def test_validate_stock_insufficient_single(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки остатков при недостатке одного товара"""
        cart_items = [
            SCartItemForOrder(product_id=1, quantity=10)
        ]
        
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={1: 5})
        )
        
        with pytest.raises(NotEnoughProductsInStock):
            await validator._validate_stock(cart_items)
    
    @pytest.mark.asyncio
    async def test_validate_stock_insufficient_multiple(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки остатков при недостатке нескольких товаров"""
        cart_items = [
            SCartItemForOrder(product_id=1, quantity=5),
            SCartItemForOrder(product_id=2, quantity=10)
        ]
        
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={1: 10, 2: 5})
        )
        
        with pytest.raises(NotEnoughProductsInStock):
            await validator._validate_stock(cart_items)
    
    @pytest.mark.asyncio
    async def test_validate_stock_product_not_found(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки остатков при отсутствии товара в ответе"""
        cart_items = [
            SCartItemForOrder(product_id=1, quantity=5)
        ]
        
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={})  # Товар отсутствует
        )
        
        with pytest.raises(NotEnoughProductsInStock):
            await validator._validate_stock(cart_items)
    
    @pytest.mark.asyncio
    async def test_validate_stock_exact_match(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки остатков при точном совпадении количества"""
        cart_items = [
            SCartItemForOrder(product_id=1, quantity=10)
        ]
        
        mocker.patch(
            'app.services.order_validator.get_stock_by_ids',
            new=mocker.AsyncMock(return_value={1: 10})
        )
        
        # Не должно быть исключений (равенство допустимо)
        await validator._validate_stock(cart_items)


class TestOrderValidatorValidateBalance:
    """Тесты для метода _validate_balance OrderValidator"""
    
    @pytest.fixture
    def validator(self):
        return OrderValidator()
    
    @pytest.mark.asyncio
    async def test_validate_balance_success(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест успешной проверки баланса"""
        user_id = 1
        total_cost = 1000
        
        mocker.patch(
            'app.services.order_validator.get_user_balance',
            new=mocker.AsyncMock(return_value=5000)
        )
        
        # Не должно быть исключений
        await validator._validate_balance(user_id, total_cost)
    
    @pytest.mark.asyncio
    async def test_validate_balance_exact_match(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки баланса при точном совпадении"""
        user_id = 1
        total_cost = 1000
        
        mocker.patch(
            'app.services.order_validator.get_user_balance',
            new=mocker.AsyncMock(return_value=1000)
        )
        
        # Не должно быть исключений (равенство допустимо)
        await validator._validate_balance(user_id, total_cost)
    
    @pytest.mark.asyncio
    async def test_validate_balance_insufficient(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки баланса при недостатке средств"""
        user_id = 1
        total_cost = 5000
        
        mocker.patch(
            'app.services.order_validator.get_user_balance',
            new=mocker.AsyncMock(return_value=3000)
        )
        
        with pytest.raises(NotEnoughBalanceToMakeOrder):
            await validator._validate_balance(user_id, total_cost)
    
    @pytest.mark.asyncio
    async def test_validate_balance_user_not_found(
        self,
        validator: OrderValidator,
        mocker
    ):
        """Тест проверки баланса при отсутствии пользователя"""
        user_id = 1
        total_cost = 1000
        
        mocker.patch(
            'app.services.order_validator.get_user_balance',
            new=mocker.AsyncMock(return_value=None)
        )
        
        with pytest.raises(UserIsNotPresentException):
            await validator._validate_balance(user_id, total_cost)
