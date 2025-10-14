from datetime import datetime, timedelta, timezone

from jose import jwt as jose_jwt, JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.exceptions import UserAlreadyExistsException, IncorrectEmailOrPasswordException, TokenExpiredException
from app.models import Users
from app.repositories import UsersRepository
from app.schemas.users import SUserAuth
from app.tasks.tasks import send_registration_confirmation_email
from app.users.auth import get_password_hash, authenticate_user, create_access_token, create_refresh_token


class AuthService:
    def __init__(self,
                 user_repository: UsersRepository,
                 db: AsyncSession):
        self.db = db
        self.user_repository = user_repository

    async def register_user(self, user_data: SUserAuth) -> Users:
        # Проверяем существование пользователя
        existing_user = await self.user_repository.get_user_by_email(user_data.email)
        if existing_user:
            raise UserAlreadyExistsException

        # Создаем пользователя с хешированным паролем
        hashed_password = get_password_hash(user_data.password)
        user = await self.user_repository.create_user({
            "email": user_data.email,
            "hashed_password": hashed_password
        })

        await self.db.commit()
        await self.db.refresh(user)

        # Отправляем email с подтверждением регистрации
        send_registration_confirmation_email.delay(user_data.email)

        return user

    async def login_user(self, user_data: SUserAuth) -> dict[str, str]:
        # Аутентифицируем пользователя
        user = await authenticate_user(user_data.email, user_data.password)
        if not user:
            raise IncorrectEmailOrPasswordException

        # Создаем токены
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    async def refresh_tokens(self, token: str) -> dict[str, str]:
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
        if not user_id or user_id == "None":
            raise JWTError

        # Ищем пользователя
        user = await self.user_repository.get(int(user_id))
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

        return {
            "access_token": new_access_token,
            "refresh_token": new_refresh_token
        }
