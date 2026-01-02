from pydantic import BaseModel


class BalanceDecreaseRequest(BaseModel):
    amount: int


