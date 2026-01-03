import json

import pytest

from backend.di_container import container
from backend.src.app.pydantic_models.auth import LoginScheme
from backend.src.infrastructure.repositories.user_repository import UserRepository


@pytest.mark.asyncio
async def test_update_successful_dialog_right_path(client):
    """
    Тест для аутентификации провальный
    """
    
    login = 'not_registered_login'
    
    data = LoginScheme(login=login, password='password')

    response = client.post(f"/auth/login", json=data.model_dump(mode='json'))
    print(response)
