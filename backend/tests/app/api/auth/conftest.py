import pytest_asyncio

from backend.src.app.core.security import hash_password
from backend.src.infrastructure.enums.users.enums import UserTypeEnum


class PreparedData:
    def __init__(self):
        self.user_id = None
        self.user_login = 'test_login'
        self.user_password = 'password'
        self.user_type = UserTypeEnum.admin.value
        self.user_updated_by = 'test'


@pytest_asyncio.fixture(scope='function', loop_scope='function')
async def prepared_data(test_uow):

    data = PreparedData()
    user_id = await test_uow.user_repository.add_with_ignore_conflict(
        value={
            'login': data.user_login,
            'password_hash': hash_password(data.user_password),
            'updated_by': data.user_updated_by,
            'user_type': data.user_type,
        },
        commit=True
    )
    data.user_id = user_id
    yield data

    await test_uow.user_repository.delete_by_id(user_id, commit=True)
