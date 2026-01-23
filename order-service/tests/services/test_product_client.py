import pytest
import httpx

from app.services.product_client import get_product, get_stock_by_ids, decrease_stock


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
            "image": "test.jpg"
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


class TestProductClientGetStockByIds:
    """Тесты для функции get_stock_by_ids"""
    
    @pytest.mark.asyncio
    async def test_get_stock_by_ids_success(self, mocker):
        """Тест успешного получения остатков"""
        product_ids = [1, 2, 3]
        expected_stock = {1: 10, 2: 20, 3: 30}
        
        mock_response = mocker.Mock()
        mock_response.json.return_value = expected_stock
        mock_response.raise_for_status = mocker.Mock()
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.post = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        result = await get_stock_by_ids(product_ids)
        
        assert result == expected_stock
        mock_client.post.assert_called_once()
        call_args = mock_client.post.call_args
        assert call_args[1]["json"] == product_ids
    
    @pytest.mark.asyncio
    async def test_get_stock_by_ids_empty_list(self, mocker):
        """Тест получения остатков для пустого списка"""
        product_ids = []
        expected_stock = {}
        
        mock_response = mocker.Mock()
        mock_response.json.return_value = expected_stock
        mock_response.raise_for_status = mocker.Mock()
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.post = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        result = await get_stock_by_ids(product_ids)
        
        assert result == expected_stock
    
    @pytest.mark.asyncio
    async def test_get_stock_by_ids_partial(self, mocker):
        """Тест получения остатков для части товаров"""
        product_ids = [1, 2, 3]
        expected_stock = {1: 10, 2: 0}  # Товар 3 отсутствует
        
        mock_response = mocker.Mock()
        mock_response.json.return_value = expected_stock
        mock_response.raise_for_status = mocker.Mock()
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.post = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        result = await get_stock_by_ids(product_ids)
        
        assert result == expected_stock
    
    @pytest.mark.asyncio
    async def test_get_stock_by_ids_service_unavailable(self, mocker):
        """Тест получения остатков при недоступности сервиса"""
        product_ids = [1, 2]
        
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
        mock_client.post = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            await get_stock_by_ids(product_ids)


class TestProductClientDecreaseStock:
    """Тесты для функции decrease_stock"""
    
    @pytest.mark.asyncio
    async def test_decrease_stock_success(self, mocker):
        """Тест успешного уменьшения остатков"""
        product_id = 1
        quantity = 5
        
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.patch = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        await decrease_stock(product_id, quantity)
        
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        assert str(product_id) in call_args[0][0]
        assert call_args[1]["json"] == {"quantity": -quantity}
    
    @pytest.mark.asyncio
    async def test_decrease_stock_zero_quantity(self, mocker):
        """Тест уменьшения остатков на ноль"""
        product_id = 1
        quantity = 0
        
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.patch = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        await decrease_stock(product_id, quantity)
        
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        assert call_args[1]["json"] == {"quantity": 0}
    
    @pytest.mark.asyncio
    async def test_decrease_stock_large_quantity(self, mocker):
        """Тест уменьшения остатков на большое количество"""
        product_id = 1
        quantity = 1000
        
        mock_response = mocker.Mock()
        mock_response.raise_for_status = mocker.Mock()
        
        mock_client = mocker.AsyncMock()
        mock_client.__aenter__ = mocker.AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = mocker.AsyncMock(return_value=None)
        mock_client.patch = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        await decrease_stock(product_id, quantity)
        
        mock_client.patch.assert_called_once()
        call_args = mock_client.patch.call_args
        assert call_args[1]["json"] == {"quantity": -quantity}
    
    @pytest.mark.asyncio
    async def test_decrease_stock_product_not_found(self, mocker):
        """Тест уменьшения остатков несуществующего товара"""
        product_id = 999
        quantity = 5
        
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
        mock_client.patch = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            await decrease_stock(product_id, quantity)
    
    @pytest.mark.asyncio
    async def test_decrease_stock_service_unavailable(self, mocker):
        """Тест уменьшения остатков при недоступности сервиса"""
        product_id = 1
        quantity = 5
        
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
        mock_client.patch = mocker.AsyncMock(return_value=mock_response)
        
        mocker.patch(
            'app.services.product_client.httpx.AsyncClient',
            return_value=mock_client
        )
        
        with pytest.raises(httpx.HTTPStatusError):
            await decrease_stock(product_id, quantity)
