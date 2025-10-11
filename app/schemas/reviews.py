from pydantic import BaseModel, ConfigDict


class SReviews(BaseModel):
    product_id: int
    rating: int
    feedback: str

    model_config = ConfigDict(from_attributes=True)
