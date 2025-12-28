from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import InstrumentedAttribute

from backend.src.infrastructure.models.users import User
from backend.src.infrastructure.pydantic_models.users import PyUser
from backend.src.infrastructure.repositories._base_repository import SqlAlchemyRepository


class UserRepository(SqlAlchemyRepository):
    model = User
    pydantic_model = PyUser

    async def get_by_login(self, login: str, select_fields: list[InstrumentedAttribute[Any]] | None = None) -> PyUser | None:
        model_fields = select_fields if select_fields else (self.model,)
        query = select(*model_fields).where(self.model.login == login)
        executed_query = await self.session.execute(query)
        result = executed_query.first() if select_fields else executed_query.scalars().first()
        return PyUser.model_validate(result, from_attributes=True) if result else None