from pydantic import BaseModel


class StockUpdateRequest(BaseModel):
    quantity: int  # Может быть отрицательным для уменьшения


