from fastapi import APIRouter, Depends, Body, HTTPException
from starlette.responses import JSONResponse, Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.container import container
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

router_auth = APIRouter(
    prefix="/auth",
    tags=["Auth"]
)

router_users = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)

@router_auth.post("/register")
async def register_user(
        user_data: SUserAuth,
        auth_service: AuthService = Depends(get_auth_service)
):
    """Регистрация нового пользователя"""
    await auth_service.register_user(user_data)
    return JSONResponse(
        content={"message": "User created successfully"}, status_code=201
    )


@router_auth.post("/login", response_model=STokenResponse)
async def login_user(
        response: Response,
        user_data: SUserAuth,
        auth_service: AuthService = Depends(get_auth_service)
) -> STokenResponse:
    tokens = await auth_service.login_user(user_data)

    response.set_cookie("access_token", tokens.access_token,
                        max_age=1800, httponly=True, samesite="lax",
                        secure=False, path="/")
    response.set_cookie("refresh_token", tokens.refresh_token,
                        max_age=604800, httponly=True, samesite="lax",
                        secure=False, path="/")

    return tokens


@router_auth.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "User logged out successfully"}


@router_auth.post("/refresh", response_model=STokenResponse)
async def refresh_token(
        response: Response,
        token: str = Depends(get_refresh_token),
        auth_service: AuthService = Depends(get_auth_service)
) -> STokenResponse:
    tokens = await auth_service.refresh_tokens(token)

    response.set_cookie("access_token", tokens.access_token, max_age=1800, httponly=True, samesite="lax",
                        path="/", secure=False)

    # Обновляем refresh_token только если он был обновлен
    if tokens.refresh_token != token:
        response.set_cookie("refresh_token", tokens.refresh_token, max_age=604800, httponly=True,
                            samesite="lax", path="/", secure=False)

    return tokens


@router_auth.get("/me")
async def get_me(user: UserItem = Depends(get_current_user)):
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
    user_repo = container.users_repository(db=db)
    user = await user_repo.get_user_by_id(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "id": user.id,
        "email": user.email,
        "name": user.name,
        "delivery_address": user.delivery_address,
        "balance": user.balance
    }


@router_users.post("/address")
async def change_address(
        address: SChangeAddress = Body(...),
        user: UserItem = Depends(get_current_user),
        user_service: UserService = Depends(get_users_service)
):
    await user_service.change_delivery_address(user.id, address.new_address)
    return {"message": "Address updated successfully"}


@router_users.post("/name")
async def change_name(
        name: SChangeName = Body(...),
        user: UserItem = Depends(get_current_user),
        user_service: UserService = Depends(get_users_service)
):
    await user_service.change_user_name(user.id, name.new_name)
    return {"message": "Name updated successfully"}


@router_users.post("/balance/decrease")
async def decrease_balance(
        request: BalanceDecreaseRequest = Body(...),
        user_id: int = Depends(get_user_id_from_header),
        user_service: UserService = Depends(get_users_service)
):
    """Уменьшает баланс пользователя (используется order-service)"""
    await user_service.decrease_balance(user_id, request.amount)
    return {"message": "Balance decreased successfully"}


@router_users.post("/batch", response_model=SBatchUsersResponse)
async def get_users_batch(
        request: SBatchUsersRequest = Body(...),
        user_service: UserService = Depends(get_users_service)
):
    """
    Получает информацию о нескольких пользователях по списку ID.
    Используется другими сервисами для получения данных пользователей батчем.
    """
    users = await user_service.get_users_by_ids(request.user_ids)
    
    users_dict = {
        user_id: SUserInfo(
            id=user.id,
            email=user.email,
            name=user.name
        )
        for user_id, user in users.items()
    }
    
    return SBatchUsersResponse(users=users_dict)
