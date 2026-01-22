import pytest
from httpx import AsyncClient

from shared.constants import DEFAULT_TEST_USER_ID
from tests.fixtures.test_data import (
    ReviewTestData,
    get_existing_product_id,
    get_nonexistent_product_id
)


class TestCreateReview:
    """Тесты для создания отзывов"""
    
    @pytest.mark.asyncio
    async def test_create_review_success(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Тест успешного создания отзыва"""
        product_id = get_existing_product_id()
        review_data = ReviewTestData.create_valid(product_id=product_id)

        response = await async_client.post(
            f"/reviews/{product_id}",
            json=review_data.to_dict(),
            headers=auth_headers
        )

        assert response.status_code == 200, \
            f"Ожидался статус 200, получен {response.status_code}. Response: {response.text}"
        
        data = response.json()
        assert "user_email" in data
        assert "user_name" in data
        assert "rating" in data
        assert "feedback" in data
        assert data["rating"] == review_data.rating
        assert data["feedback"] == review_data.feedback
        # Проверяем, что email соответствует дефолтному user_id из мока
        assert data["user_email"] == f"user{DEFAULT_TEST_USER_ID}@example.com"
        assert data["user_name"] == f"User {DEFAULT_TEST_USER_ID}"
        assert isinstance(data["rating"], int)
        assert isinstance(data["feedback"], str)
    
    @pytest.mark.asyncio
    async def test_create_review_with_empty_feedback(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Тест создания отзыва с пустым текстом"""
        product_id = get_existing_product_id()
        review_data = ReviewTestData.create_with_feedback("", product_id=product_id)

        response = await async_client.post(
            f"/reviews/{product_id}",
            json=review_data.to_dict(),
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["feedback"] == ""
        assert data["rating"] == review_data.rating
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("rating", [1, 2, 3, 4, 5])
    async def test_create_review_with_valid_ratings(
        self,
        rating: int,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Тест создания отзыва с валидными рейтингами"""
        product_id = get_existing_product_id()
        review_data = ReviewTestData.create_with_rating(rating, product_id=product_id)

        response = await async_client.post(
            f"/reviews/{product_id}",
            json=review_data.to_dict(),
            headers=auth_headers
        )

        assert response.status_code == 200
        data = response.json()
        assert data["rating"] == rating
    
    @pytest.mark.asyncio
    @pytest.mark.parametrize("rating", [0, -1, 6, 10])
    async def test_create_review_with_invalid_rating(
        self,
        rating: int,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Тест создания отзыва с невалидным рейтингом"""
        product_id = get_existing_product_id()
        review_data = ReviewTestData.create_with_rating(rating, product_id=product_id)

        response = await async_client.post(
            f"/reviews/{product_id}",
            json=review_data.to_dict(),
            headers=auth_headers
        )

        assert response.status_code == 422
        data = response.json()
        assert "detail" in data
    
    @pytest.mark.asyncio
    async def test_create_review_nonexistent_product(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Тест создания отзыва для несуществующего продукта"""
        product_id = get_nonexistent_product_id()
        review_data = ReviewTestData.create_valid(product_id=product_id)

        response = await async_client.post(
            f"/reviews/{product_id}",
            json=review_data.to_dict(),
            headers=auth_headers
        )

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower() or str(product_id) in str(data["detail"])


class TestGetReviews:
    """Тесты для получения отзывов"""
    
    @pytest.mark.asyncio
    async def test_get_reviews_empty(self, async_client: AsyncClient):
        """Тест получения отзывов для продукта без отзывов"""
        product_id = get_existing_product_id()

        response = await async_client.get(f"/reviews/{product_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0
    
    @pytest.mark.asyncio
    async def test_get_reviews_with_data(
        self,
        async_client: AsyncClient,
        auth_headers: dict
    ):
        """Тест получения отзывов для продукта с отзывами"""
        product_id = get_existing_product_id()
        reviews_data = [
            ReviewTestData.create_with_rating(5, product_id=product_id),
            ReviewTestData.create_with_rating(4, product_id=product_id),
            ReviewTestData.create_with_rating(3, product_id=product_id),
        ]

        for review_data in reviews_data:
            await async_client.post(
                f"/reviews/{product_id}",
                json=review_data.to_dict(),
                headers=auth_headers
            )

        response = await async_client.get(f"/reviews/{product_id}")

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 3

        for review in data:
            assert "user_email" in review
            assert "user_name" in review
            assert "rating" in review
            assert "feedback" in review
            assert isinstance(review["rating"], int)
            assert isinstance(review["feedback"], str)
            assert 1 <= review["rating"] <= 5
            assert isinstance(review["user_email"], str)
            assert review["user_email"]

        ratings = [r["rating"] for r in data]
        assert 5 in ratings
        assert 4 in ratings
        assert 3 in ratings
    
    @pytest.mark.asyncio
    async def test_get_reviews_multiple_users(
        self,
        async_client: AsyncClient,
        auth_headers_with_user_id
    ):
        """Тест получения отзывов от разных пользователей"""
        product_id = get_existing_product_id()
        user_ids = [1, 2, 3]

        for user_id in user_ids:
            review_data = ReviewTestData.create_valid(product_id=product_id)
            review_data.user_id = user_id
            
            headers = auth_headers_with_user_id(user_id)
            await async_client.post(
                f"/reviews/{product_id}",
                json=review_data.to_dict(),
                headers=headers
            )

        response = await async_client.get(f"/reviews/{product_id}")

        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Проверяем, что user_email присутствует и различается
        user_emails = {review["user_email"] for review in data}
        assert len(user_emails) == 3

        for review in data:
            assert "user_email" in review
            assert "user_name" in review
            assert review["user_email"].startswith("user")  # Из мока
            assert "@example.com" in review["user_email"]
