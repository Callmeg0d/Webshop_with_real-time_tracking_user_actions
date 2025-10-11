import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.database import async_session_maker
from app.models.reviews import Reviews


@pytest.mark.asyncio
async def test_add_review_success(async_client: AsyncClient, auth_headers):
    review_data = {
        "product_id": 1,
        "rating": 5,
        "feedback": "Отличный товар, советую"
    }

    response = await async_client.post("/reviews/", json=review_data, headers=auth_headers)

    assert response.status_code == 200
    review_response = response.json()

    assert review_response["rating"] == review_data["rating"]
    assert review_response["feedback"] == review_data["feedback"]

    async with async_session_maker() as session:
        result = await session.execute(
            select(Reviews)
            .where(Reviews.product_id == review_data["product_id"])
        )
        review_in_db = result.scalar()
        assert review_in_db is not None
        assert review_in_db.rating == review_data["rating"]
        assert review_in_db.feedback == review_data["feedback"]
