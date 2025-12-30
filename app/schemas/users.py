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