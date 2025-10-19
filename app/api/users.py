from fastapi import APIRouter, Depends, Body
from starlette.responses import JSONResponse, Response

from app.dependencies import get_auth_service, get_refresh_token, get_current_user, get_users_service
from app.models import Users
from app.schemas import SUserAuth, SChangeAddress, SChangeName
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


@router_auth.post("/login")
async def login_user(
        response: Response,
        user_data: SUserAuth,
        auth_service: AuthService = Depends(get_auth_service)
):
    tokens = await auth_service.login_user(user_data)

    response.set_cookie("access_token", tokens["access_token"],
                        max_age=1800, httponly=True, samesite="lax",
                        secure=False, path="/")
    response.set_cookie("refresh_token", tokens["refresh_token"],
                        max_age=604800, httponly=True, samesite="lax",
                        secure=False, path="/")

    return tokens


@router_auth.post("/logout")
async def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "User logged out successfully"}


@router_auth.post("/refresh")
async def refresh_token(
        response: Response,
        token: str = Depends(get_refresh_token),
        auth_service: AuthService = Depends(get_auth_service)
):
    tokens = await auth_service.refresh_tokens(token)

    response.set_cookie("access_token", tokens["access_token"], max_age=1800, httponly=True, samesite="lax",
                        path="/", secure=False)

    # Обновляем refresh_token только если он был обновлен
    if tokens["refresh_token"] != token:
        response.set_cookie("refresh_token", tokens["refresh_token"], max_age=604800, httponly=True,
                            samesite="lax", path="/", secure=False)

    return tokens


@router_auth.get("/me")
async def get_me(user: Users = Depends(get_current_user)):
    return user


@router_users.post("/address")
async def change_address(
        address: SChangeAddress = Body(...),
        user: Users = Depends(get_current_user),
        user_service: UserService = Depends(get_users_service)
):
    await user_service.change_delivery_address(user.id, address.new_address)
    return {"message": "Address updated successfully"}


@router_users.post("/name")
async def change_name(
        name: SChangeName = Body(...),
        user: Users = Depends(get_current_user),
        user_service: UserService = Depends(get_users_service)
):
    await user_service.change_user_name(user.id, name.new_name)
    return {"message": "Name updated successfully"}

