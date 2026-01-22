import pytest

from app.domain.entities.users import UserItem
from app.services.user_service import UserService


class TestUserServiceCreateUser:
    """Юнит-тесты для метода create_user UserService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        """Мок репозитория"""
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow(self, mocker):
        """Мок UnitOfWork"""
        uow = mocker.AsyncMock()
        uow.__aenter__ = mocker.AsyncMock(return_value=uow)
        uow.__aexit__ = mocker.AsyncMock(return_value=None)
        return uow
    
    @pytest.fixture
    def mock_uow_factory(self, mock_uow, mocker):
        """Мок фабрики UnitOfWork"""
        factory = mocker.Mock()
        factory.create = mocker.Mock(return_value=mock_uow)
        return factory
    
    @pytest.fixture
    def user_service(self, mock_repository, mock_uow_factory):
        """Создает экземпляр UserService с моками"""
        return UserService(
            user_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_create_user_success(
        self,
        user_service: UserService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного создания пользователя"""
        user_data = UserItem(
            email="test@example.com",
            hashed_password="hashed_password",
            balance=0
        )
        
        created_user = UserItem(
            email="test@example.com",
            hashed_password="hashed_password",
            balance=0,
            id=1
        )
        mock_repository.create_user = mocker.AsyncMock(return_value=created_user)
        
        result = await user_service.create_user(user_data)
        
        assert isinstance(result, UserItem)
        assert result.id == 1
        assert result.email == "test@example.com"
        
        mock_repository.create_user.assert_called_once()
        mock_uow_factory.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_user_repository_error(
        self,
        user_service: UserService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест обработки ошибки при создании пользователя"""
        user_data = UserItem(
            email="test@example.com",
            hashed_password="hashed_password",
            balance=0
        )
        
        mock_repository.create_user = mocker.AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await user_service.create_user(user_data)
        
        mock_repository.create_user.assert_called_once()
        mock_uow.__aexit__.assert_called_once()


class TestUserServiceChangeDeliveryAddress:
    """Юнит-тесты для метода change_delivery_address"""
    
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
    def user_service(self, mock_repository, mock_uow_factory):
        return UserService(
            user_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_change_delivery_address_success(
        self,
        user_service: UserService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного изменения адреса доставки"""
        user_id = 1
        new_address = "New Address"
        
        mock_repository.change_delivery_address = mocker.AsyncMock(return_value=None)
        
        await user_service.change_delivery_address(user_id, new_address)
        
        mock_repository.change_delivery_address.assert_called_once_with(user_id=user_id, new_address=new_address)
        mock_uow_factory.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()


class TestUserServiceChangeName:
    """Юнит-тесты для метода change_user_name"""
    
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
    def user_service(self, mock_repository, mock_uow_factory):
        return UserService(
            user_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_change_user_name_success(
        self,
        user_service: UserService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного изменения имени"""
        user_id = 1
        new_name = "New Name"
        
        mock_repository.change_user_name = mocker.AsyncMock(return_value=None)
        
        await user_service.change_user_name(user_id, new_name)
        
        mock_repository.change_user_name.assert_called_once_with(user_id, new_name)
        mock_uow_factory.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()


class TestUserServiceDecreaseBalance:
    """Юнит-тесты для метода decrease_balance"""
    
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
    def user_service(self, mock_repository, mock_uow_factory):
        return UserService(
            user_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_decrease_balance_success(
        self,
        user_service: UserService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного уменьшения баланса"""
        user_id = 1
        amount = 50
        
        mock_repository.decrease_balance = mocker.AsyncMock(return_value=None)
        
        await user_service.decrease_balance(user_id, amount)
        
        mock_repository.decrease_balance.assert_called_once_with(user_id, amount)
        mock_uow_factory.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()


class TestUserServiceGetUsersByIds:
    """Юнит-тесты для метода get_users_by_ids"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        return mocker.Mock()
    
    @pytest.fixture
    def user_service(self, mock_repository, mock_uow_factory):
        return UserService(
            user_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_users_by_ids_success(
        self,
        user_service: UserService,
        mock_repository,
        mocker
    ):
        """Тест успешного получения пользователей по ID"""
        user_ids = [1, 2, 3]
        users = {
            1: UserItem(email="user1@example.com", hashed_password="hash1", id=1, name="User 1"),
            2: UserItem(email="user2@example.com", hashed_password="hash2", id=2, name="User 2"),
            3: UserItem(email="user3@example.com", hashed_password="hash3", id=3, name="User 3"),
        }
        
        mock_repository.get_users_by_ids = mocker.AsyncMock(return_value=users)
        
        result = await user_service.get_users_by_ids(user_ids)
        
        assert len(result) == 3
        assert all(isinstance(u, UserItem) for u in result.values())
        assert result[1].email == "user1@example.com"
        assert result[2].email == "user2@example.com"
        assert result[3].email == "user3@example.com"
        
        mock_repository.get_users_by_ids.assert_called_once_with(user_ids)
    
    @pytest.mark.asyncio
    async def test_get_users_by_ids_empty(
        self,
        user_service: UserService,
        mock_repository,
        mocker
    ):
        """Тест получения пользователей с пустым списком ID"""
        mock_repository.get_users_by_ids = mocker.AsyncMock(return_value={})
        
        result = await user_service.get_users_by_ids([])
        
        assert result == {}
        mock_repository.get_users_by_ids.assert_called_once_with([])
    
    @pytest.mark.asyncio
    async def test_get_users_by_ids_partial(
        self,
        user_service: UserService,
        mock_repository,
        mocker
    ):
        """Тест получения пользователей (некоторые не найдены)"""
        user_ids = [1, 2, 999]
        users = {
            1: UserItem(email="user1@example.com", hashed_password="hash1", id=1),
            2: UserItem(email="user2@example.com", hashed_password="hash2", id=2),
        }
        
        mock_repository.get_users_by_ids = mocker.AsyncMock(return_value=users)
        
        result = await user_service.get_users_by_ids(user_ids)
        
        assert len(result) == 2
        assert 1 in result
        assert 2 in result
        assert 999 not in result
