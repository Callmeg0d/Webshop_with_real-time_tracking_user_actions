import pytest
import httpx

from app.services.product_client import get_product


class TestProductClientGetProduct:
    """Тесты для функции get_product"""
    
    @pytest.mark.asyncio
    async def test_get_product_success(self, mocker):
        """Тест успешного получения продукта"""
        product_id = 1
        expected_product = {
            "id": 1,
            "name": "Test Product",
            "price": 1000,
            "description": "Test Description",
            "product_quantity": 10
        }
        
        mock_response = mocker.Mock()
        mock_response.json.return_value = expected_product
        mock_response.raise_for_status = mocker.Mock()
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.get = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        result = await get_product(product_id)
        
        assert result == expected_product
        mock_client.get.assert_called_once()
        call_args = mock_client.get.call_args
        assert str(product_id) in call_args[0][0]
    
    @pytest.mark.asyncio
    async def test_get_product_not_found(self, mocker):
        """Тест получения несуществующего продукта"""
        product_id = 999
        
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock(
            side_effect=httpx.HTTPStatusError(
                "Not Found",
                request=mocker.Mock(),
                response=mocker.Mock(status_code=404)
            )
        )
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.get = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            await get_product(product_id)
    
    @pytest.mark.asyncio
    async def test_get_product_service_unavailable(self, mocker):
        """Тест получения продукта при недоступности сервиса"""
        product_id = 1
        
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock(
            side_effect=httpx.HTTPStatusError(
                "Service Unavailable",
                request=mocker.Mock(),
                response=mocker.Mock(status_code=503)
            )
        )
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.get = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            await get_product(product_id)
