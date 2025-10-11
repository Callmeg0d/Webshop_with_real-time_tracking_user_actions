import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_leave_review_success(async_client: AsyncClient, auth_headers):
    review_data = {
        "product_id": 1,
        "rating": 5,
        "feedback": "Отличный товар!"
    }

    response = await async_client.post("/reviews/", json=review_data, headers=auth_headers)

    assert response.status_code == 200
    response_data = response.json()

    assert response_data["user_name"] is not None
    assert response_data["rating"] == review_data["rating"]
    assert response_data["feedback"] == review_data["feedback"]