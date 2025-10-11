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
