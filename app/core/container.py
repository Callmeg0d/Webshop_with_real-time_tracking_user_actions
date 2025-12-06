from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories import UsersRepository, ProductsRepository, CartsRepository, OrdersRepository, ReviewRepository, \
    CategoriesRepository
from app.services.auth_service import AuthService
from app.services.cart_service import CartService
from app.services.category_service import CategoryService
from app.services.order_notification_service import OrderNotificationService
from app.services.order_service import OrderService
from app.services.order_validator import OrderValidator
from app.services.payment_service import PaymentService
from app.services.product_service import ProductService
from app.services.review_service import ReviewService
from app.services.user_service import UserService


class Container(containers.DeclarativeContainer):
    """DI-контейнер для управления зависимостями"""

    db = providers.Dependency(instance_of=AsyncSession)

    users_repository = providers.Factory(
        UsersRepository,
        db=db
    )

    products_repository = providers.Factory(
        ProductsRepository,
        db=db
    )

    carts_repository = providers.Factory(
        CartsRepository,
        db=db
    )

    orders_repository = providers.Factory(
        OrdersRepository,
        db=db
    )

    reviews_repository = providers.Factory(
        ReviewRepository,
        db=db
    )

    categories_repository = providers.Factory(
        CategoriesRepository,
        db=db
    )

    order_validator = providers.Factory(
        OrderValidator,
        users_repository=users_repository,
        products_repository=products_repository
    )

    payment_service = providers.Factory(
        PaymentService,
        users_repository=users_repository
    )

    order_notification_service = providers.Factory(
        OrderNotificationService,
        users_repository=users_repository
    )

    order_service = providers.Factory(
        OrderService,
        orders_repository=orders_repository,
        users_repository=users_repository,
        products_repository=products_repository,
        carts_repository=carts_repository,
        order_validator=order_validator,
        payment_service=payment_service,
        notification_service=order_notification_service,
        db=db
    )

    authentication_service = providers.Factory(
        AuthService,
        users_repository=users_repository,
        db=db
    )

    cart_service = providers.Factory(
        CartService,
        carts_repository=carts_repository,
        db=db

    )

    category_service = providers.Factory(
        CategoryService,
        categories_repository=categories_repository,
        db=db
    )

    product_service = providers.Factory(
        ProductService,
        products_repository=products_repository,
        db=db
    )

    review_service = providers.Factory(
        ReviewService,
        users_repository=users_repository,
        reviews_repository=reviews_repository,
        db=db
    )

    user_service = providers.Factory(
        UserService,
        users_repository=users_repository,
        db=db
    )