import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("email", "password", "status_code"),
    [
        ("kot@pes.com", "kotopes", 201),
        ("kot@pes.com", "kot0pes", 409),
        ("abcdef", "test_pass", 422),
    ]
)
async def test_register_user(email, password, status_code, async_client: AsyncClient):
    response = await async_client.post("/auth/register", json={
        "email": email,
        "password": password
    })

    assert response.status_code == status_code


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("email", "password", "status_code"),
    [
        ("test@test.com", "test", 200),
        ("bebra@bebra.com", "bebra", 200),
        ("wrong@person.com", "test_pass", 401),
    ]
)
async def test_login_user(email, password, status_code, async_client: AsyncClient):
    response = await async_client.post("/auth/login", json={
        "email": email,
        "password": password
    })

    assert response.status_code == status_code


@pytest.mark.asyncio
async def test_logout_user(async_client: AsyncClient):
    login_response = await async_client.post("/auth/login", json={"email": "test@test.com", "password": "test"})
    assert login_response.status_code == 200

    access_token = login_response.cookies.get("access_token")
    refresh_token = login_response.cookies.get("refresh_token")

    assert access_token
    assert refresh_token

    logout_response = await async_client.post("/auth/logout")

    assert logout_response.status_code == 200
    assert logout_response.json() == {"message": "User logged out successfully"}

    assert "access_token" not in logout_response.cookies or not logout_response.cookies.get("access_token")
    assert "refresh_token" not in logout_response.cookies or not logout_response.cookies.get("refresh_token")


@pytest.mark.asyncio
async def test_change_name(async_client: AsyncClient, auth_headers):
    new_name = "New Test Name"
    data = {"new_name": new_name}

    response = await async_client.post("/users/name", json=data, headers=auth_headers)
    assert response.status_code == 200

    updated_user = response.json()
    assert updated_user == new_name


@pytest.mark.asyncio
async def test_change_address(async_client: AsyncClient, auth_headers):
    new_address = "Москва, Никольская 52"
    data = {"new_address": new_address}

    response = await async_client.post("/users/address", json=data, headers=auth_headers)
    assert response.status_code == 200

    updated_user = response.json()
    assert updated_user == new_address
