import pytest
from httpx import AsyncClient

from app.core.security import get_password_hash
from app.domain.entities.users import UserItem
from app.repositories.users_repository import UsersRepository


class TestAuthRegister:
    """Тесты для регистрации пользователей"""
    
    @pytest.mark.asyncio
    async def test_register_user_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешной регистрации пользователя"""
        user_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = await async_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert "message" in data
        assert data["message"] == "User created successfully"
        
        # Проверяем, что пользователь создан в БД
        user_repo = UsersRepository(test_db_session)
        user = await user_repo.get_user_by_email(user_data["email"])
        assert user is not None
        assert user.email == user_data["email"]
    
    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(
        self,
        async_client: AsyncClient,
    ):
        """Тест регистрации с существующим email"""
        user_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        # Создаем первого пользователя
        await async_client.post("/auth/register", json=user_data)
        
        # Пытаемся создать второго с тем же email
        response = await async_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 409
        data = response.json()
        assert "detail" in data
        assert "уже существует" in data["detail"] or "already exists" in data["detail"].lower()
    
    @pytest.mark.asyncio
    async def test_register_user_invalid_email(
        self,
        async_client: AsyncClient
    ):
        """Тест регистрации с невалидным email"""
        user_data = {
            "email": "invalid-email",
            "password": "password123"
        }
        
        response = await async_client.post("/auth/register", json=user_data)
        
        assert response.status_code == 422


class TestAuthLogin:
    """Тесты для входа пользователей"""
    
    @pytest.mark.asyncio
    async def test_login_user_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного входа пользователя"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            balance=0
        )
        await user_repo.create_user(user)
        await test_db_session.commit()

        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        
        response = await async_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert isinstance(data["access_token"], str)
        assert isinstance(data["refresh_token"], str)
        
        # Проверяем cookies
        cookies = response.cookies
        assert "access_token" in cookies
        assert "refresh_token" in cookies
    
    @pytest.mark.asyncio
    async def test_login_user_wrong_password(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест входа с неверным паролем"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            balance=0
        )
        await user_repo.create_user(user)
        await test_db_session.commit()

        login_data = {
            "email": "test@example.com",
            "password": "wrongpassword"
        }
        
        response = await async_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_login_user_not_found(
        self,
        async_client: AsyncClient
    ):
        """Тест входа несуществующего пользователя"""
        login_data = {
            "email": "nonexistent@example.com",
            "password": "password123"
        }
        
        response = await async_client.post("/auth/login", json=login_data)
        
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data


class TestAuthMe:
    """Тесты для получения текущего пользователя"""
    
    @pytest.mark.asyncio
    async def test_get_me_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест получения текущего пользователя"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            name="Test User",
            delivery_address="Test Address",
            balance=100
        )
        created_user = await user_repo.create_user(user)
        await test_db_session.commit()

        login_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        login_response = await async_client.post("/auth/login", json=login_data)
        access_token = login_response.json()["access_token"]
        
        # Получаем текущего пользователя
        response = await async_client.get(
            "/auth/me",
            cookies={"access_token": access_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user.id
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["delivery_address"] == "Test Address"
        assert data["balance"] == 100
    
    @pytest.mark.asyncio
    async def test_get_me_no_token(
        self,
        async_client: AsyncClient
    ):
        """Тест получения текущего пользователя без токена"""
        response = await async_client.get("/auth/me")
        
        assert response.status_code == 401


class TestUsersMe:
    """Тесты для получения пользователя по заголовку X-User-Id"""
    
    @pytest.mark.asyncio
    async def test_get_me_by_header_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест получения пользователя по заголовку"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            name="Test User",
            balance=100
        )
        created_user = await user_repo.create_user(user)
        await test_db_session.commit()
        
        response = await async_client.get(
            "/users/me",
            headers={"X-User-Id": str(created_user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == created_user.id
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["balance"] == 100
    
    @pytest.mark.asyncio
    async def test_get_me_by_header_not_found(
        self,
        async_client: AsyncClient
    ):
        """Тест получения несуществующего пользователя"""
        response = await async_client.get(
            "/users/me",
            headers={"X-User-Id": "99999"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data


class TestUsersChangeAddress:
    """Тесты для изменения адреса доставки"""
    
    @pytest.mark.asyncio
    async def test_change_address_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного изменения адреса"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            delivery_address="Old Address"
        )
        created_user = await user_repo.create_user(user)
        await test_db_session.commit()
        
        login_response = await async_client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        access_token = login_response.json()["access_token"]
        
        # Меняем адрес
        response = await async_client.post(
            "/users/address",
            json={"new_address": "New Address"},
            cookies={"access_token": access_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Address updated successfully"
        
        # Проверяем, что адрес изменился
        updated_user = await user_repo.get_user_by_id(created_user.id)
        assert updated_user.delivery_address == "New Address"


class TestUsersChangeName:
    """Тесты для изменения имени"""
    
    @pytest.mark.asyncio
    async def test_change_name_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного изменения имени"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            name="Old Name"
        )
        created_user = await user_repo.create_user(user)
        await test_db_session.commit()
        
        login_response = await async_client.post(
            "/auth/login",
            json={"email": "test@example.com", "password": "password123"}
        )
        access_token = login_response.json()["access_token"]
        
        # Меняем имя
        response = await async_client.post(
            "/users/name",
            json={"new_name": "New Name"},
            cookies={"access_token": access_token}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Name updated successfully"
        
        # Проверяем, что имя изменилось
        updated_user = await user_repo.get_user_by_id(created_user.id)
        assert updated_user.name == "New Name"


class TestUsersBatch:
    """Тесты для batch получения пользователей"""
    
    @pytest.mark.asyncio
    async def test_get_users_batch_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного получения пользователей батчем"""
        user_repo = UsersRepository(test_db_session)
        users = []
        for i in range(3):
            user = UserItem(
                email=f"user{i}@example.com",
                hashed_password=get_password_hash("password123"),
                name=f"User {i}"
            )
            created_user = await user_repo.create_user(user)
            users.append(created_user)
        await test_db_session.commit()
        
        # Получаем пользователей батчем
        user_ids = [u.id for u in users]
        response = await async_client.post(
            "/users/batch",
            json={"user_ids": user_ids}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) == 3
        
        for user_id in user_ids:
            assert str(user_id) in data["users"]
            user_info = data["users"][str(user_id)]
            assert "id" in user_info
            assert "email" in user_info
            assert "name" in user_info
    
    @pytest.mark.asyncio
    async def test_get_users_batch_partial(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест получения пользователей батчем (некоторые не найдены)"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            name="Test User"
        )
        created_user = await user_repo.create_user(user)
        await test_db_session.commit()
        
        # Запрашиваем существующего и несуществующего
        response = await async_client.post(
            "/users/batch",
            json={"user_ids": [created_user.id, 99999]}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "users" in data
        assert len(data["users"]) == 1
        assert str(created_user.id) in data["users"]


class TestUsersDecreaseBalance:
    """Тесты для уменьшения баланса"""
    
    @pytest.mark.asyncio
    async def test_decrease_balance_success(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест успешного уменьшения баланса"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            balance=100
        )
        created_user = await user_repo.create_user(user)
        await test_db_session.commit()
        
        # Уменьшаем баланс
        response = await async_client.post(
            "/users/balance/decrease",
            json={"amount": 30},
            headers={"X-User-Id": str(created_user.id)}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Balance decreased successfully"
        
        # Проверяем баланс
        updated_user = await user_repo.get_user_by_id(created_user.id)
        assert updated_user.balance == 70
    
    @pytest.mark.asyncio
    async def test_decrease_balance_insufficient(
        self,
        async_client: AsyncClient,
        test_db_session
    ):
        """Тест уменьшения баланса при недостаточных средствах"""
        user_repo = UsersRepository(test_db_session)
        user = UserItem(
            email="test@example.com",
            hashed_password=get_password_hash("password123"),
            balance=10
        )
        created_user = await user_repo.create_user(user)
        await test_db_session.commit()

        response = await async_client.post(
            "/users/balance/decrease",
            json={"amount": 100},
            headers={"X-User-Id": str(created_user.id)},
            follow_redirects=False
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
