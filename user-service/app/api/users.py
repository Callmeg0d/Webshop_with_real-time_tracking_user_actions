from fastapi import APIRouter, Depends, Body, HTTPException
from starlette.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from shared import get_logger

from app.core.container import Container
from app.dependencies import (
    get_auth_service, get_refresh_token, get_current_user, get_users_service,
    get_user_id_from_header, get_db
)


from app.domain.entities.users import UserItem
from app.schemas import SUserAuth, SChangeAddress, SChangeName
from app.schemas.users import STokenResponse, SBatchUsersRequest, SBatchUsersResponse, SUserInfo
from app.schemas.balance import BalanceDecreaseRequest
from app.services.auth_service import AuthService
from app.services.user_service import UserService

container = Container()

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

router_users = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

logger = get_logger(__name__)

@router_auth.post("/register")
async def register_user(
        user_data: SUserAuth,
        auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    logger.info(f"POST /auth/register request for email: {user_data.email}")
    try:
        await auth_service.register_user(user_data)
        logger.info(f"User registered successfully by API: {user_data.email}")
        return JSONResponse(
            content={"message": "User created successfully"}, status_code=201
        )
    except Exception as e:
        logger.error(f"Error registering user by API: {e}", exc_info=True)
        raise


@router_auth.post("/login", response_model=STokenResponse)
async def login_user(
        response: Response,
        user_data: SUserAuth,
        auth_service: AuthService = Depends(get_auth_service)
) -> STokenResponse:
    logger.info(f"POST /auth/login request for email: {user_data.email}")
    try:
        tokens = await auth_service.login_user(user_data)

        response.set_cookie("access_token", tokens.access_token,
                            max_age=1800, httponly=True, samesite="lax",
                            secure=False, path="/")
        response.set_cookie("refresh_token", tokens.refresh_token,
                            max_age=604800, httponly=True, samesite="lax",
                            secure=False, path="/")

        logger.info(f"User logged in successfully by API: {user_data.email}")
        return tokens
    except Exception as e:
        logger.error(f"Error during login by API: {e}", exc_info=True)
        raise


@router_auth.post("/logout")
async def logout_user(response: Response):
    logger.info("POST /auth/logout request")
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    logger.info("User logged out successfully")
    return {"message": "User logged out successfully"}


@router_auth.post("/refresh", response_model=STokenResponse)
async def refresh_token(
        response: Response,
        token: str = Depends(get_refresh_token),
        auth_service: AuthService = Depends(get_auth_service)
) -> STokenResponse:
    logger.info("POST /auth/refresh request")
    try:
        tokens = await auth_service.refresh_tokens(token)

        response.set_cookie("access_token", tokens.access_token, max_age=1800, httponly=True, samesite="lax",
                            path="/", secure=False)

        # Обновляем refresh_token только если он был обновлен
        if tokens.refresh_token != token:
            response.set_cookie("refresh_token", tokens.refresh_token, max_age=604800, httponly=True,
                                samesite="lax", path="/", secure=False)

        logger.info("Tokens refreshed successfully by API")
        return tokens
    except Exception as e:
        logger.error(f"Error refreshing tokens by API: {e}", exc_info=True)
        raise


@router_auth.get("/me")
async def get_me(user: UserItem = Depends(get_current_user)):
    logger.info(f"GET /auth/me request for user {user.id}")
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "delivery_address": user.delivery_address,
        "balance": user.balance
    }


@router_users.get("/me")
async def get_me_by_header(
        user_id: int = Depends(get_user_id_from_header),
        db: AsyncSession = Depends(get_db)
):
    """Получает пользователя по заголовку X-User-Id (для других сервисов)"""
    logger.info(f"GET /users/me request for user {user_id}")
    try:
        with container.db.override(db):
            user_repo = container.users_repository()
            user = await user_repo.get_user_by_id(user_id)
            if not user:
                logger.warning(f"User {user_id} not found")
                raise HTTPException(status_code=404, detail="User not found")
            
            logger.info(f"User {user_id} returned successfully")
            return {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "delivery_address": user.delivery_address,
                "balance": user.balance
            }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching user {user_id} by API: {e}", exc_info=True)
        raise


@router_users.post("/address")
async def change_address(
        address: SChangeAddress = Body(...),
        user: UserItem = Depends(get_current_user),
        user_service: UserService = Depends(get_users_service)
):
    logger.info(f"POST /users/address request for user {user.id}")
    try:
        await user_service.change_delivery_address(user.id, address.new_address)
        logger.info(f"Address updated successfully via API for user {user.id}")
        return {"message": "Address updated successfully"}
    except Exception as e:
        logger.error(f"Error changing address by API for user {user.id}: {e}", exc_info=True)
        raise


@router_users.post("/name")
async def change_name(
        name: SChangeName = Body(...),
        user: UserItem = Depends(get_current_user),
        user_service: UserService = Depends(get_users_service)
):
    logger.info(f"POST /users/name request for user {user.id}")
    try:
        await user_service.change_user_name(user.id, name.new_name)
        logger.info(f"Name updated successfully via API for user {user.id}")
        return {"message": "Name updated successfully"}
    except Exception as e:
        logger.error(f"Error changing name by API for user {user.id}: {e}", exc_info=True)
        raise


@router_users.post("/balance/decrease")
async def decrease_balance(
        request: BalanceDecreaseRequest = Body(...),
        user_id: int = Depends(get_user_id_from_header),
        user_service: UserService = Depends(get_users_service)
):
    """Уменьшает баланс пользователя (используется order-service)"""
    logger.info(f"POST /users/balance/decrease request for user {user_id}, amount: {request.amount}")
    try:
        await user_service.decrease_balance(user_id, request.amount)
        logger.info(f"Balance decreased successfully by API for user {user_id}")
        return {"message": "Balance decreased successfully"}
    except IntegrityError as e:
        logger.error(f"Integrity error decreasing balance by API for user {user_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Database constraint violation")
    except Exception as e:
        logger.error(f"Error decreasing balance by API for user {user_id}: {e}", exc_info=True)
        raise


@router_users.post("/batch", response_model=SBatchUsersResponse)
async def get_users_batch(
        request: SBatchUsersRequest = Body(...),
        user_service: UserService = Depends(get_users_service)
):
    """
    Получает информацию о нескольких пользователях по списку ID.
    Используется другими сервисами для получения данных пользователей батчем.
    """
    logger.info(f"POST /users/batch request for {len(request.user_ids)} users")
    try:
        users = await user_service.get_users_by_ids(request.user_ids)
        
        users_dict = {
            user_id: SUserInfo(
                id=user.id,
                email=user.email,
                name=user.name
            )
            for user_id, user in users.items()
        }
        
        logger.info(f"Batch users returned successfully: {len(users_dict)} users")
        return SBatchUsersResponse(users=users_dict)
    except Exception as e:
        logger.error(f"Error fetching users batch by API: {e}", exc_info=True)
        raise
