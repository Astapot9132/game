from http import HTTPStatus
from unittest.mock import AsyncMock

import pytest

from backend.src.app.pydantic_models.auth import AuthScheme
from backend.src.infrastructure.pydantic_models.users import PyUser
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
async def test_login_with_wrong_password(client, test_uow, prepared_data):
    """
    Тест для аутентификации провальный
    """
    wrong_password = 'wrong'

    user_in_db: PyUser = await test_uow.user_repository.get_by_id(prepared_data.user_id)
    assert user_in_db

    data = AuthScheme(login=user_in_db.login, password=wrong_password)

    response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.FORBIDDEN



@pytest.mark.asyncio
async def test_login_right_path(client, test_uow, prepared_data):
    """
    Тест для аутентификации - правильный результат
    """
    right_password = 'password'
    user_in_db = await test_uow.user_repository.get_by_id(prepared_data.user_id)
    assert user_in_db and not user_in_db.refresh_token_hash

    data = AuthScheme(login=user_in_db.login, password=right_password)

    response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.OK

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
    try:
        response = await client.post(f"/auth/registration", json=data.model_dump(mode='json'))
        assert response.status_code == HTTPStatus.OK


        user_in_db = await test_uow.user_repository.get_by_login(login)
        assert user_in_db
        assert not user_in_db.refresh_token_hash
    finally:
        await test_uow.user_repository.delete_by_id(user_in_db.id, commit=True)

@pytest.mark.asyncio
async def test_refresh_right_path(client, test_uow, prepared_data, monkeypatch):

    password = 'password'
    user_in_db = await test_uow.user_repository.get_by_id(prepared_data.user_id)
    assert user_in_db and not user_in_db.refresh_token_hash

    data = AuthScheme(login=user_in_db.login, password=password)

    response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.OK
    await test_uow.session.rollback()
    user_in_db = await test_uow.user_repository.get_by_id(prepared_data.user_id)
    assert user_in_db.refresh_token_hash
    mock_update = AsyncMock(return_value=None)
    monkeypatch.setattr(UserRepository, "update_by_id", mock_update)
    refresh_response = await client.post(f"/auth/refresh")
    assert refresh_response.status_code == HTTPStatus.OK
    assert mock_update.call_count == 1
    kwargs = mock_update.call_args.kwargs
    assert 'refresh_token_hash' in kwargs['values']


@pytest.mark.asyncio
async def test_logout_right_path(client, test_uow, prepared_data):

    password = 'password'
    user_in_db = await test_uow.user_repository.get_by_id(prepared_data.user_id)
    assert user_in_db and not user_in_db.refresh_token_hash

    data = AuthScheme(login=user_in_db.login, password=password)

    response = await client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == HTTPStatus.OK
    await test_uow.session.rollback()
    user_in_db = await test_uow.user_repository.get_by_id(prepared_data.user_id)
    assert user_in_db.refresh_token_hash

    refresh_response = await client.post(f"/auth/logout")
    assert refresh_response.status_code == HTTPStatus.OK

    await test_uow.session.rollback()
    user_in_db = await test_uow.user_repository.get_by_id(prepared_data.user_id)
    assert not user_in_db.refresh_token_hash

#
