import pytest

import app.services.review_service as review_service_module
from app.domain.entities.reviews import ReviewItem
from app.services.review_service import ReviewService
from app.schemas.reviews import SReviewWithUser
from shared.constants import AnonymousUser


class TestReviewServiceCreateReview:
    """Юнит-тесты для метода create_review ReviewService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        """Мок репозитория"""
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow(self, mocker):
        """Мок UnitOfWork"""
        uow = mocker.AsyncMock()
        uow.__aenter__ = mocker.AsyncMock(return_value=uow)
        uow.__aexit__ = mocker.AsyncMock(return_value=None)
        return uow
    
    @pytest.fixture
    def mock_uow_factory(self, mock_uow, mocker):
        """Мок фабрики UnitOfWork"""
        factory = mocker.Mock()
        factory.create = mocker.Mock(return_value=mock_uow)
        return factory
    
    @pytest.fixture
    def review_service(self, mock_repository, mock_uow_factory):
        """Создает экземпляр ReviewService с моками"""
        return ReviewService(
            reviews_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_create_review_success(
        self,
        review_service: ReviewService,
        mock_repository,
        mock_uow,
        mock_uow_factory,
        mocker
    ):
        """Тест успешного создания отзыва"""
        user_id = 1
        product_id = 4
        rating = 5
        feedback = "Отличный товар"
        
        created_review = ReviewItem(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            feedback=feedback,
            review_id=1
        )
        mock_repository.create_review = mocker.AsyncMock(return_value=created_review)

        mocker.patch.object(
            review_service_module,
            'get_user_info',
            return_value={"email": "user1@example.com", "name": "User 1"}
        )
        
        result = await review_service.create_review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            feedback=feedback
        )
        
        assert isinstance(result, SReviewWithUser)
        assert result.user_email == "user1@example.com"
        assert result.user_name == "User 1"
        assert result.rating == rating
        assert result.feedback == feedback
        
        mock_repository.create_review.assert_called_once()
        mock_uow_factory.create.assert_called_once()
        mock_uow.__aenter__.assert_called_once()
        mock_uow.__aexit__.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_review_user_info_fallback(
        self,
        review_service: ReviewService,
        mock_repository,
        mocker
    ):
        """Тест fallback на AnonymousUser при ошибке получения данных пользователя"""
        user_id = 1
        product_id = 4
        rating = 4
        feedback = "Хороший товар"
        
        created_review = ReviewItem(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            feedback=feedback,
            review_id=1
        )
        mock_repository.create_review = mocker.AsyncMock(return_value=created_review)

        mocker.patch.object(
            review_service_module,
            'get_user_info',
            side_effect=Exception("User service unavailable")
        )
        
        result = await review_service.create_review(
            user_id=user_id,
            product_id=product_id,
            rating=rating,
            feedback=feedback
        )
        
        assert isinstance(result, SReviewWithUser)
        assert result.user_email == AnonymousUser.EMAIL
        assert result.user_name == AnonymousUser.NAME
        assert result.rating == rating
        assert result.feedback == feedback
    
    @pytest.mark.asyncio
    async def test_create_review_repository_error(
        self,
        review_service: ReviewService,
        mock_repository,
        mock_uow,
        mocker
    ):
        """Тест обработки ошибки при создании отзыва в репозитории"""
        user_id = 1
        product_id = 4
        rating = 3
        feedback = "Средний товар"
        
        mock_repository.create_review = mocker.AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await review_service.create_review(
                user_id=user_id,
                product_id=product_id,
                rating=rating,
                feedback=feedback
            )
        
        mock_repository.create_review.assert_called_once()
        mock_uow.__aexit__.assert_called_once()


class TestReviewServiceGetReviews:
    """Юнит-тесты для метода get_reviews ReviewService"""
    
    @pytest.fixture
    def mock_repository(self, mocker):
        """Мок репозитория"""
        return mocker.AsyncMock()
    
    @pytest.fixture
    def mock_uow_factory(self, mocker):
        """Мок фабрики UnitOfWork"""
        return mocker.Mock()
    
    @pytest.fixture
    def review_service(self, mock_repository, mock_uow_factory):
        """Создает экземпляр ReviewService с моками"""
        return ReviewService(
            reviews_repository=mock_repository,
            uow_factory=mock_uow_factory
        )
    
    @pytest.mark.asyncio
    async def test_get_reviews_empty(
        self,
        review_service: ReviewService,
        mock_repository,
        mocker
    ):
        """Тест получения пустого списка отзывов"""
        product_id = 4
        mock_repository.get_reviews_by_product = mocker.AsyncMock(return_value=[])
        
        result = await review_service.get_reviews(product_id)
        
        assert result == []
        mock_repository.get_reviews_by_product.assert_called_once_with(product_id)
    
    @pytest.mark.asyncio
    async def test_get_reviews_with_data(
        self,
        review_service: ReviewService,
        mock_repository,
        mocker
    ):
        """Тест получения отзывов с данными пользователей"""
        product_id = 4
        reviews = [
            ReviewItem(user_id=1, product_id=product_id, rating=5, feedback="Отлично", review_id=1),
            ReviewItem(user_id=2, product_id=product_id, rating=4, feedback="Хорошо", review_id=2),
            ReviewItem(user_id=3, product_id=product_id, rating=3, feedback="Средне", review_id=3),
        ]
        mock_repository.get_reviews_by_product = mocker.AsyncMock(return_value=reviews)

        mock_get_users_batch = mocker.patch.object(
            review_service_module,
            'get_users_batch',
            return_value={
                1: {"email": "user1@example.com", "name": "User 1"},
                2: {"email": "user2@example.com", "name": "User 2"},
                3: {"email": "user3@example.com", "name": "User 3"},
            }
        )
        
        result = await review_service.get_reviews(product_id)
        
        assert len(result) == 3
        assert all(isinstance(r, SReviewWithUser) for r in result)
        
        assert result[0].user_email == "user1@example.com"
        assert result[0].user_name == "User 1"
        assert result[0].rating == 5
        assert result[0].feedback == "Отлично"
        
        assert result[1].user_email == "user2@example.com"
        assert result[1].rating == 4
        
        assert result[2].user_email == "user3@example.com"
        assert result[2].rating == 3
        
        mock_repository.get_reviews_by_product.assert_called_once_with(product_id)
        mock_get_users_batch.assert_called_once_with([1, 2, 3])
    
    @pytest.mark.asyncio
    async def test_get_reviews_user_info_fallback(
        self,
        review_service: ReviewService,
        mock_repository,
        mocker
    ):
        """Тест fallback на AnonymousUser при ошибке получения данных пользователей"""
        product_id = 4
        reviews = [
            ReviewItem(user_id=1, product_id=product_id, rating=5, feedback="Отлично", review_id=1),
            ReviewItem(user_id=2, product_id=product_id, rating=4, feedback="Хорошо", review_id=2),
        ]
        mock_repository.get_reviews_by_product = mocker.AsyncMock(return_value=reviews)
        
        mocker.patch.object(
            review_service_module,
            'get_users_batch',
            return_value={}
        )
        
        result = await review_service.get_reviews(product_id)
        
        assert len(result) == 2
        assert all(isinstance(r, SReviewWithUser) for r in result)
        assert all(r.user_email == AnonymousUser.EMAIL for r in result)
        assert all(r.user_name == AnonymousUser.NAME for r in result)
        assert result[0].rating == 5
        assert result[1].rating == 4
    
    @pytest.mark.asyncio
    async def test_get_reviews_partial_user_info(
        self,
        review_service: ReviewService,
        mock_repository,
        mocker
    ):
        product_id = 4
        reviews = [
            ReviewItem(user_id=1, product_id=product_id, rating=5, feedback="Отлично", review_id=1),
            ReviewItem(user_id=2, product_id=product_id, rating=4, feedback="Хорошо", review_id=2),
            ReviewItem(user_id=999, product_id=product_id, rating=3, feedback="Средне", review_id=3),
        ]
        mock_repository.get_reviews_by_product = mocker.AsyncMock(return_value=reviews)
        
        # Мокаем get_users_batch чтобы возвращал данные только для некоторых пользователей
        mocker.patch.object(
            review_service_module,
            'get_users_batch',
            return_value={
                1: {"email": "user1@example.com", "name": "User 1"},
                # user_id=2 отсутствует
                # user_id=999 отсутствует
            }
        )
        
        result = await review_service.get_reviews(product_id)
        
        assert len(result) == 3
        assert result[0].user_email == "user1@example.com"
        assert result[0].user_name == "User 1"
        assert result[1].user_email == AnonymousUser.EMAIL
        assert result[1].user_name == AnonymousUser.NAME
        assert result[2].user_email == AnonymousUser.EMAIL
        assert result[2].user_name == AnonymousUser.NAME
    
    @pytest.mark.asyncio
    async def test_get_reviews_repository_error(
        self,
        review_service: ReviewService,
        mock_repository,
        mocker
    ):
        """Тест обработки ошибки при получении отзывов из репозитория"""
        product_id = 4
        mock_repository.get_reviews_by_product = mocker.AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(Exception, match="Database error"):
            await review_service.get_reviews(product_id)
        
        mock_repository.get_reviews_by_product.assert_called_once_with(product_id)
