import pytest
from httpx import AsyncClient

from app.users.dao import UsersDAO


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("user_id", "new_name"),
    [
        (2, "Васёк"),
    ],
)
async def test_change_name_with_me_endpoint(user_id, new_name, async_client: AsyncClient):
    response = await UsersDAO.change_name(new_name=new_name, user_id=user_id)
    assert response == new_name, f"Имя не обновилось в базе для user_id={user_id}"

    login_response = await async_client.post("/auth/login", json={"email": "test@test.com", "password": "test"})
    assert login_response.status_code == 200, "Не удалось залогиниться"

    token = login_response.json().get("access_token")
    assert token, f"Токен не получен: {login_response.json()}"

    me_response = await async_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200, f"Ошибка при запросе /me"
    me_data = me_response.json()

    assert me_data["name"] == new_name, (
        f"Ожидалось имя {new_name}, а в /me вернулось {me_data.get('name')}"
    )


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("user_id", "new_address"),
    [
        (2, "Москва, кузнечихиснкая 100"),
    ],
)
async def test_change_address_with_me_endpoint(user_id, new_address, async_client: AsyncClient):
    response = await UsersDAO.change_address(new_address=new_address, user_id=user_id)
    assert response == new_address

    login_response = await async_client.post("/auth/login", json={"email": "test@test.com", "password": "test"})
    assert login_response.status_code == 200

    token = login_response.json().get("access_token")
    assert token

    me_response = await async_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})

    assert me_response.status_code == 200
    me_data = me_response.json()

    assert me_data["delivery_address"] == new_address, (
        f"Ожидалось {new_address}, а в /me вернулось {me_data.get('delivery_address')}"
    )



