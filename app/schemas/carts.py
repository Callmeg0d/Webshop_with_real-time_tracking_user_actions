from pydantic import BaseModel, ConfigDict


class UpdateCartItemRequest(BaseModel):
    quantity: int

    model_config = ConfigDict(from_attributes=True)