import json
import sys
import time
from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest

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

    response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.FORBIDDEN


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

    response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.FORBIDDEN

    await test_uow.user_repository.delete_by_id(user_in_db.id, commit=True)


@pytest.mark.asyncio
async def test_login_right_path(client, test_uow):
    """
    Тест для аутентификации - правильный результат
    """

    login = 'not_registered_login'
    right_password = 'right'

    await test_uow.user_repository.add_with_ignore_conflict(
        value={
                'login': login,
                'password_hash': hash_password(right_password),
                'updated_by': 'test',
                'user_type': UserTypeEnum.admin.value,
            },
        commit=True
    )
    user_in_db = await test_uow.user_repository.get_by_login(login)
    assert user_in_db and not user_in_db.refresh_token_hash

    data = AuthScheme(login=login, password=right_password)

    response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.OK
    await test_uow.user_repository.delete_by_id(user_in_db.id, commit=True)

@pytest.mark.asyncio
async def test_registration_right_path(client, test_uow):
    """
    Тест для аутентификации - правильный результат
    """

    login = 'not_registered_login'
    password = 'password'

    user_in_db = await test_uow.user_repository.get_by_login(login)
    assert not user_in_db

    data = AuthScheme(login=login, password=password)

    response = await client.post(f"/auth/registration", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.OK


    user_in_db = await test_uow.user_repository.get_by_login(login)
    assert user_in_db
    assert not user_in_db.refresh_token_hash

    await test_uow.user_repository.delete_by_id(user_in_db.id, commit=True)

@pytest.mark.asyncio
async def test_refresh_right_path(client, test_uow, monkeypatch):
    login = 'not_registered_login'
    password = 'password'
    await test_uow.user_repository.add_with_ignore_conflict(
        value={
                'login': login,
                'password_hash': hash_password(password),
                'updated_by': 'test',
                'user_type': UserTypeEnum.admin.value,
            },
        commit=True
    )

    user_in_db = await test_uow.user_repository.get_by_login(login)
    assert user_in_db and not user_in_db.refresh_token_hash

    data = AuthScheme(login=login, password=password)

    response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.OK
    user_in_db = await test_uow.user_repository.get_by_login(login)
    print(user_in_db.refresh_token_hash)
    # assert user_in_db.refresh_token_hash
    # mock_update = AsyncMock(return_value=None)
    # monkeypatch.setattr(UserRepository, "update_by_id", mock_update)
    # refresh_response = await client.post(f"/auth/refresh")
    # assert refresh_response.status_code == HTTPStatus.OK
    # assert mock_update.call_count == 1
    # kwargs = mock_update.call_args.kwargs
    # assert 'refresh_token_hash' in kwargs['values']
    #
    # user_in_db = await test_uow.user_repository.get_by_login(login)

    await test_uow.user_repository.delete_by_id(user_in_db.id, commit=True)

#
# @pytest.mark.asyncio
# async def test_logout_right_path(client, test_uow):
#     login = 'not_registered_login'
#     password = 'password'
#     await test_uow.user_repository.add_with_ignore_conflict(
#         value={
#                 'login': login,
#                 'password_hash': hash_password(password),
#                 'updated_by': 'test',
#                 'user_type': UserTypeEnum.admin.value,
#             },
#         commit=True
#     )
#
#     user_in_db = await test_uow.user_repository.get_by_login(login)
#     assert user_in_db and not user_in_db.refresh_token_hash
#
#     data = AuthScheme(login=login, password=password)
#
#     response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
#     assert response.status_code == HTTPStatus.OK
#     user_in_db = await test_uow.user_repository.get_by_login(login)
#     assert user_in_db.refresh_token_hash
#
#     refresh_response = await client.post(f"/auth/logout")
#     assert refresh_response.status_code == HTTPStatus.OK
#
#
#     user_in_db = await test_uow.user_repository.get_by_login(login)
#     assert not user_in_db.refresh_token_hash
#
#     await test_uow.user_repository.delete_by_id(user_in_db.id, commit=True)
#
