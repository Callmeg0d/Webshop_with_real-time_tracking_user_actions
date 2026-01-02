from pydantic import BaseModel, ConfigDict, EmailStr


class SUserAuth(BaseModel):
    email: EmailStr
    password: str

    model_config = ConfigDict(from_attributes=True)


class SChangeAddress(BaseModel):
    new_address: str

    model_config = ConfigDict(from_attributes=True)


class SChangeName(BaseModel):
    new_name: str

    model_config = ConfigDict(from_attributes=True)


class STokenResponse(BaseModel):
    """Схема для ответа с токенами доступа."""
    access_token: str
    refresh_token: str

    model_config = ConfigDict(from_attributes=True)


class SBatchUsersRequest(BaseModel):
    """Схема для batch-запроса получения пользователей."""
    user_ids: list[int]

    model_config = ConfigDict(from_attributes=True)


class SUserInfo(BaseModel):
    """Схема для информации о пользователе (для batch-ответа)."""
    id: int
    email: str
    name: str | None

    model_config = ConfigDict(from_attributes=True)


class SBatchUsersResponse(BaseModel):
    """Схема для batch-ответа с пользователями."""
    users: dict[int, SUserInfo]

    model_config = ConfigDict(from_attributes=True)
