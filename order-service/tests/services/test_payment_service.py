import pytest

from app.services.payment_service import PaymentService


class TestPaymentService:
    """Тесты для PaymentService"""
    
    @pytest.fixture
    def payment_service(self):
        return PaymentService()
    
    @pytest.mark.asyncio
    async def test_process_payment_success(
        self,
        payment_service: PaymentService,
        mocker
    ):
        """Тест успешной обработки оплаты"""
        user_id = 1
        total_cost = 3500
        
        mock_decrease = mocker.patch(
            'app.services.payment_service.decrease_user_balance',
            new=mocker.AsyncMock(return_value=None)
        )
        
        await payment_service.process_payment(user_id, total_cost)
        
        mock_decrease.assert_called_once_with(user_id, total_cost)
    
    @pytest.mark.asyncio
    async def test_process_payment_zero_cost(
        self,
        payment_service: PaymentService,
        mocker
    ):
        """Тест обработки оплаты с нулевой стоимостью"""
        user_id = 1
        total_cost = 0
        
        mock_decrease = mocker.patch(
            'app.services.payment_service.decrease_user_balance',
            new=mocker.AsyncMock(return_value=None)
        )
        
        await payment_service.process_payment(user_id, total_cost)
        
        mock_decrease.assert_called_once_with(user_id, total_cost)
    
    @pytest.mark.asyncio
    async def test_process_payment_large_amount(
        self,
        payment_service: PaymentService,
        mocker
    ):
        """Тест обработки оплаты с большой суммой"""
        user_id = 1
        total_cost = 100000
        
        mock_decrease = mocker.patch(
            'app.services.payment_service.decrease_user_balance',
            new=mocker.AsyncMock(return_value=None)
        )
        
        await payment_service.process_payment(user_id, total_cost)
        
        mock_decrease.assert_called_once_with(user_id, total_cost)
    
    @pytest.mark.asyncio
    async def test_process_payment_different_users(
        self,
        payment_service: PaymentService,
        mocker
    ):
        """Тест обработки оплаты для разных пользователей"""
        user_id_1 = 1
        user_id_2 = 2
        total_cost = 1000
        
        mock_decrease = mocker.patch(
            'app.services.payment_service.decrease_user_balance',
            new=mocker.AsyncMock(return_value=None)
        )
        
        await payment_service.process_payment(user_id_1, total_cost)
        await payment_service.process_payment(user_id_2, total_cost)
        
        assert mock_decrease.call_count == 2
        mock_decrease.assert_any_call(user_id_1, total_cost)
        mock_decrease.assert_any_call(user_id_2, total_cost)
