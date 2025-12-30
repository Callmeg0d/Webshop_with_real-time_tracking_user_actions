from datetime import datetime, timedelta, timezone

from jose import jwt as jose_jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.core.security import get_password_hash, authenticate_user, create_access_token, create_refresh_token
from app.core.unit_of_work import UnitOfWork
from app.domain.entities.users import UserItem
from app.domain.interfaces.users_repo import IUsersRepository
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, TokenExpiredException
from app.schemas.users import SUserAuth, STokenResponse
from app.messaging.publisher import publish_registration_confirmation


class AuthService:
    def __init__(self,
                 user_repository: IUsersRepository,
                 db: AsyncSession):
        """
        Сервис аутентификации для регистрации, входа и обновления токенов пользователей

        Args:
            user_repository: Репозиторий для работы с пользователями в БД
            db: Асинхронная сессия базы данных
        """
        self.db = db
        self.user_repository = user_repository

    async def register_user(self, user_data: SUserAuth) -> UserItem:
        """
        Регистрирует нового пользователя в системе

        Args:
            user_data: Данные для регистрации

        Returns:
            UserItem: Доменная сущность зарегистрированного пользователя

        Raises:
            UserAlreadyExistsException: Если пользователь с таким email уже существует
        """

        # Проверяем существование пользователя
        async with UnitOfWork(self.db):
            existing_user = await self.user_repository.get_user_by_email(user_data.email)
            if existing_user:
                raise UserAlreadyExistsException

            # Создаем пользователя с хешированным паролем
            hashed_password = get_password_hash(user_data.password)
            user = await self.user_repository.create_user(
                UserItem(
                    email=user_data.email,
                    hashed_password=hashed_password,
                    balance=0,
                )
            )


        # Отправляем email с подтверждением регистрации
        await publish_registration_confirmation(user_data.email)

        return user

    async def login_user(self, user_data: SUserAuth) -> STokenResponse:
        """
        Аутентифицирует пользователя и возвращает токены доступа

        Args:
            user_data: Данные для входа (email и пароль)

        Returns:
            Схема с access_token и refresh_token

        Raises:
            IncorrectEmailOrPasswordException: Если неверный email или пароль
        """

        # Аутентифицируем пользователя
        user = await authenticate_user(user_data.email, user_data.password, self.db)
        if not user:
            raise IncorrectEmailOrPasswordException

        # Создаем токены
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return STokenResponse(
            access_token=access_token,
            refresh_token=refresh_token
        )

    async def refresh_tokens(self, token: str) -> STokenResponse:
        """
        Обновляет access token и при необходимости refresh token

        Args:
            token: Refresh token для верификации

        Returns:
            Схема с новым access_token и refresh_token (если нужно обновить)

        Raises:
            TokenExpiredException: Если refresh token истек
            JWTError: Если токен невалиден или пользователь не найден
        """

        # Декодируем токен
        try:
            payload = jose_jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        except JWTError:
            raise JWTError

        # Проверяем срок действия refresh токена
        expire = payload.get("exp")
        if not expire or int(expire) < datetime.now(tz=timezone.utc).timestamp():
            raise TokenExpiredException

        # Проверяем наличие user_id
        user_id = payload.get("sub")
        if not isinstance(user_id, str) or user_id == "None":
            raise JWTError

        # Ищем пользователя
        user = await self.user_repository.get_user_by_id(int(user_id))
        if not user:
            raise JWTError

        # Создаём новый access token
        new_access_token = jose_jwt.encode(
            {"sub": str(user.id), "exp": datetime.now(tz=timezone.utc) + timedelta(minutes=30)},
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM,
        )

        # Проверяем, нужно ли обновить refresh token (если скоро истечет)
        refresh_expire_time = datetime.fromtimestamp(expire, tz=timezone.utc)
        if refresh_expire_time - datetime.now(tz=timezone.utc) < timedelta(minutes=2):
            new_refresh_token = jose_jwt.encode(
                {"sub": str(user.id), "exp": datetime.now(tz=timezone.utc) + timedelta(days=7)},
                settings.SECRET_KEY,
                algorithm=settings.ALGORITHM,
            )
        else:
            new_refresh_token = token  # Оставляем старый refresh_token

        return STokenResponse(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
