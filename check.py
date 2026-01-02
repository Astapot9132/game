import datetime

from backend.src.infrastructure.models import User
from backend.src.infrastructure.pydantic_models.users import PyUser

user = User(
    id=1,
    login='test',
    password_hash='test',
    user_type='admin',
    created_at=datetime.datetime.now(),
    updated_at=datetime.datetime.now(),
    language='RU'
)

print(PyUser.model_validate(user, from_attributes=True))


class Check:

    def __init__(self):
        print('here')

    def __call__(self, *args, **kwargs):
        print('call')

    def check(self):
        print('test')

a = Check()

a()
a()
a.check()