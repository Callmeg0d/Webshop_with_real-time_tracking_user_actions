import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, product_id, rating, feedback, expected_status",
    [
        # Тест 1: Успешное создание отзыва
        (1, 4, 5, "Отличный товар", 200),
        # Тест 2: Несуществующий товар
        (1, 497, 3, "Пользовался неделю, товар не понравился", 404),
        # Тест 3: Некорректный рейтинг
        (1, 4, 0, "Плохой товар", 422),
        # Тест 4: Некорректный рейтинг
        (1, 4, 6, "Отличный товар", 422),
        # Тест 5: Пустой отзыв
        (1, 4, 4, "", 200),
    ]
)
async def test_create_review(user_id: int,
                            product_id: int,
                            rating: int,
                            feedback: str,
                            expected_status: int,
                            async_client: AsyncClient,
                            auth_headers: dict
                        ):
    review_data = {
        "rating": rating,
        "feedback": feedback
    }

    response = await async_client.post(
        f"/reviews/{product_id}",
        json=review_data,
        headers=auth_headers
    )

    assert response.status_code == expected_status, \
        f"Ожидался статус {expected_status}, получен {response.status_code}"

    if expected_status == 200:
        data = response.json()
        assert "id" in data
        assert data["user_id"] == user_id
        assert data["product_id"] == product_id
        assert data["rating"] == rating
        assert data["feedback"] == feedback
        assert "created_at" in data

    elif expected_status == 404:
        data = response.json()
        assert "detail" in data

    elif expected_status == 422:
        data = response.json()
        assert "detail" in data