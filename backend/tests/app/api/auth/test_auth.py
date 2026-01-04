import json

import pytest

from backend.di_container import container, get_script_uow
from backend.src.app.core.security import hash_password
from backend.src.app.pydantic_models.auth import LoginScheme
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
    
    data = LoginScheme(login=login, password='password')

    response = client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == 401


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
        ]
    )
    user_in_db = await test_uow.user_repository.get_by_login(login)
    assert user_in_db

    data = LoginScheme(login=login, password=wrong_password)

    response = client.post(f"/auth/login", json=data.model_dump(mode='json'))
    assert response.status_code == 401
