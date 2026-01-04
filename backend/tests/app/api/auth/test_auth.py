import json
from http import HTTPStatus

import pytest

from backend.di_container import container, get_script_uow
from backend.src.app.core.security import hash_password
from backend.src.app.pydantic_models.auth import AuthScheme
from backend.src.infrastructure.enums.users.enums import UserTypeEnum
from backend.src.infrastructure.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_login_without_user(client, test_uow):
    """
    Тест для аутентификации провальный
    """
    
    login = 'not_registered_login'
    user_in_db = await test_uow.user_repository.get_by_login(login)
    assert not user_in_db
    
    data = AuthScheme(login=login, password='password')

    response = client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.UNAUTHORIZED


@pytest.mark.asyncio
async def test_login_with_wrong_password(client, test_uow):
    """
    Тест для аутентификации провальный
    """

    login = 'not_registered_login'
    right_password = 'right'
    wrong_password = 'wrong'
    
    await test_uow.user_repository.add_many(
        values=[
            {
                'login': login,
                'password_hash': hash_password(right_password),
                'updated_by': 'test',
                'user_type': UserTypeEnum.admin.value,
            }
        ],
        commit=True
    )
    user_in_db = await test_uow.user_repository.get_by_login(login)
    assert user_in_db

    data = AuthScheme(login=login, password=wrong_password)

    response = client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.UNAUTHORIZED
    
    await test_uow.user_repository.delete_by_id(user_in_db.id, commit=True)


@pytest.mark.asyncio
async def test_login_right_path(client, test_uow):
    """
    Тест для аутентификации - правильный результат
    """

    login = 'not_registered_login'
    right_password = 'right'

    await test_uow.user_repository.add_many(
        values=[
            {
                'login': login,
                'password_hash': hash_password(right_password),
                'updated_by': 'test',
                'user_type': UserTypeEnum.admin.value,
            }
        ],
        commit=True
    )
    user_in_db = await test_uow.user_repository.get_by_login(login)
    assert user_in_db

    data = AuthScheme(login=login, password=right_password)

    response = client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.OK
    await test_uow.user_repository.delete_by_id(user_in_db.id, commit=True)
    