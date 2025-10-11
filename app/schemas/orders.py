from datetime import datetime
from typing import Dict, List

from pydantic import BaseModel, ConfigDict


class SOrderResponse(BaseModel):
    order_id: int
    user_id: int
    created_at: datetime
    status: str
    delivery_address: str
    order_items: List[Dict[str, int]]
    total_cost: int

    model_config = ConfigDict(from_attributes=True)
