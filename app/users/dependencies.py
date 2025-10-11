from datetime import datetime

from fastapi import Depends, Request
from jose import JWTError, jwt

from app.config import settings
from app.exceptions import (
    IncorrectTokenFormatException,
    TokenAbsentException,
    TokenExpiredException,
    UserIsNotPresentException,
)
from app.users.dao import UsersDAO


def get_access_token(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise TokenAbsentException
    return token


def get_refresh_token(request: Request):
    token = request.cookies.get("refresh_token")
    if not token:
        raise TokenExpiredException
    return token


async def get_current_user(token: str = Depends(get_access_token)):
    try:  # декодим токен и достаём данные из payload
        payload = jwt.decode(
            token, settings.SECRET_KEY, settings.ALGORITHM
        )
    except JWTError:
        raise IncorrectTokenFormatException
    expire: str = payload.get("exp")  # достали время истечения токена
    if (not expire) or int(expire) < datetime.utcnow().timestamp():
        raise TokenExpiredException

    user_id: str = payload.get("sub")  # достали id
    if not user_id:
        raise UserIsNotPresentException

    user = await UsersDAO.find_one_or_none(id=int(user_id))
    if not user:
        raise UserIsNotPresentException
    return user
