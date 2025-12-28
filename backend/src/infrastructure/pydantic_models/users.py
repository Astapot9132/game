from pydantic import BaseModel, field_validator

from backend.src.infrastructure.enums.users.enums import UserLanguageEnum, UserTypeEnum


class PyUser(BaseModel):
    id: int
    login: str
    password_hash: str
    email: str | None = None
    surname: str | None = None
    firstname: str | None = None
    patronymic: str | None = None
    age: int | None = None
    language: UserLanguageEnum = UserLanguageEnum.RU
    user_type: UserTypeEnum

    @classmethod
    @field_validator("age")
    def validate_age(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if not 0 < value < 100:
            raise ValueError("Возраст должен быть между 1 и 99")
        return value