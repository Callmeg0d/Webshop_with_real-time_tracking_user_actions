from pydantic import BaseModel, Field


class RecommendRequest(BaseModel):
    query: str = Field(..., min_length=1, description="Текст товара для поиска похожих (название, описание, категория, фичи)")
    limit: int = Field(default=3, ge=1, le=50, description="Максимум товаров в ответе")
